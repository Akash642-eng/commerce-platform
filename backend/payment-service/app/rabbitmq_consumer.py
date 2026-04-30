import pika
import json
import os
import time
import random
import redis

from .logger import log_event  # ✅ NEW

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")

# 🔥 REDIS (Idempotency)
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
redis_client = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)


def publish_payment_event(data, trace_id):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST)
    )
    channel = connection.channel()

    is_success = random.choice([True, False])

    if is_success:
        event = {
            "version": "v1",
            "order_id": data["order_id"],
            "status": "SUCCESS"
        }
        queue = "payment_completed"
    else:
        event = {
            "version": "v1",
            "order_id": data["order_id"],
            "status": "FAILED"
        }
        queue = "payment_failed"

    channel.queue_declare(queue=queue, durable=True)

    channel.basic_publish(
        exchange='',
        routing_key=queue,
        body=json.dumps(event),
        properties=pika.BasicProperties(
            delivery_mode=2,
            headers={"x-trace-id": trace_id}
        )
    )

    log_event("payment-service", trace_id, f"Sent {queue}", event)

    connection.close()


def callback(ch, method, properties, body):
    try:
        data = json.loads(body)

        trace_id = properties.headers.get("x-trace-id") if properties.headers else "N/A"

        # 🔥 IDEMPOTENCY KEY
        event_id = f"payment:{data['order_id']}"

        # 🛑 DUPLICATE CHECK
        if redis_client.get(event_id):
            log_event("payment-service", trace_id, "Duplicate event skipped", data)
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        # mark event as processed
        redis_client.set(event_id, "1", ex=3600)

        log_event("payment-service", trace_id, "Processing payment", data)

        # 🔥 simulate failure
        if data["order_id"] % 5 == 0:
            raise Exception("Simulated payment failure")

        time.sleep(1)

        publish_payment_event(data, trace_id)

        ch.basic_ack(delivery_tag=method.delivery_tag)

        log_event("payment-service", trace_id, "Payment processed + ACK sent", data)

    except Exception as e:
        log_event("payment-service", trace_id, "Processing failed", {"error": str(e)}, level="ERROR")

        retry_count = data.get("retry", 0)

        # 🚫 MAX RETRIES → DLQ
        if retry_count >= 3:
            log_event("payment-service", trace_id, "Max retries reached → sending to DLQ", data, level="ERROR")

            data["version"] = "v1"

            ch.basic_publish(
                exchange='',
                routing_key="payment_dlq",
                body=json.dumps(data),
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    headers={"x-trace-id": trace_id}
                )
            )

            log_event("payment-service", trace_id, "Sent to DLQ", data, level="ERROR")

            ch.basic_ack(delivery_tag=method.delivery_tag)

        else:
            # 🔁 EXPONENTIAL BACKOFF
            retry_count += 1
            data["retry"] = retry_count

            delay = 2 ** retry_count  # 2, 4, 8 seconds

            log_event(
                "payment-service",
                trace_id,
                f"Retry {retry_count} after {delay}s",
                data,
                level="WARNING"
            )

            time.sleep(delay)

            ch.basic_publish(
                exchange='',
                routing_key="inventory_reserved",
                body=json.dumps(data),
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    headers={"x-trace-id": trace_id}
                )
            )

            ch.basic_ack(delivery_tag=method.delivery_tag)


def start_consumer():
    log_event("payment-service", "SYSTEM", "Payment consumer started")

    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=RABBITMQ_HOST,
                    heartbeat=600,
                    blocked_connection_timeout=300
                )
            )

            channel = connection.channel()

            # ✅ DECLARE QUEUES
            channel.queue_declare(queue="inventory_reserved", durable=True)
            channel.queue_declare(queue="payment_completed", durable=True)
            channel.queue_declare(queue="payment_failed", durable=True)
            channel.queue_declare(queue="payment_dlq", durable=True)

            channel.basic_qos(prefetch_count=1)

            channel.basic_consume(
                queue="inventory_reserved",
                on_message_callback=callback,
                auto_ack=False
            )

            log_event("payment-service", "SYSTEM", "Waiting for inventory_reserved")

            channel.start_consuming()

        except Exception as e:
            log_event("payment-service", "SYSTEM", "Consumer error", {"error": str(e)}, level="ERROR")
            log_event("payment-service", "SYSTEM", "Retrying in 5 seconds", level="WARNING")
            time.sleep(5)