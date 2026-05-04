import pika
import json
import os
import time
import random
import redis

from .logger import log_event

ENV = os.getenv("ENV", "dev")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
redis_client = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)

MAX_RETRIES = 3


# ---------- COMMON PUBLISH ----------
def publish(queue, message, trace_id, headers=None):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST)
    )
    channel = connection.channel()

    channel.queue_declare(queue=queue, durable=True)

    final_headers = headers or {}
    final_headers["x-trace-id"] = trace_id

    channel.basic_publish(
        exchange='',
        routing_key=queue,
        body=json.dumps(message),
        properties=pika.BasicProperties(
            delivery_mode=2,
            headers=final_headers
        )
    )

    connection.close()


# ---------- PAYMENT EVENT ----------
def publish_payment_event(data, trace_id):
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

    publish(queue, event, trace_id)

    log_event("payment-service", trace_id, f"Sent {queue}", event)


# ---------- CALLBACK ----------
def callback(ch, method, properties, body):
    trace_id = "N/A"

    try:
        data = json.loads(body)

        headers = properties.headers or {}
        trace_id = headers.get("x-trace-id", "N/A")
        retry_count = headers.get("x-retry", 0)

        event_id = f"payment:{data['order_id']}"

        if redis_client.get(event_id):
            log_event("payment-service", trace_id, "Duplicate skipped", data)
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        redis_client.set(event_id, "1", ex=3600)

        log_event(
            "payment-service",
            trace_id,
            f"Processing payment (retry={retry_count})",
            data
        )

        # simulate failure
        if data["order_id"] % 5 == 0:
            raise Exception("Simulated payment failure")

        time.sleep(1 if ENV == "dev" else 0.5)

        publish_payment_event(data, trace_id)

        ch.basic_ack(delivery_tag=method.delivery_tag)

        log_event("payment-service", trace_id, "Payment processed", data)

    except Exception as e:
        err = str(e) if ENV == "dev" else "processing failed"

        log_event(
            "payment-service",
            trace_id,
            "Processing failed",
            {"error": err},
            level="ERROR"
        )

        headers = properties.headers or {}
        retry_count = headers.get("x-retry", 0)

        if retry_count < MAX_RETRIES:
            new_headers = headers.copy()
            new_headers["x-retry"] = retry_count + 1

            log_event(
                "payment-service",
                trace_id,
                f"Retrying ({retry_count + 1})",
                {},
                level="WARNING"
            )

            publish(
                "inventory_reserved",  # retry same input queue
                json.loads(body),
                trace_id,
                headers=new_headers
            )

        else:
            log_event(
                "payment-service",
                trace_id,
                "Sending to DLQ",
                {},
                level="ERROR"
            )

            publish(
                "payment_dlq",
                json.loads(body),
                trace_id,
                headers=headers
            )

        ch.basic_ack(delivery_tag=method.delivery_tag)


# ---------- CONSUMER ----------
def start_consumer():
    log_event("payment-service", "SYSTEM", f"Payment consumer started ({ENV})")

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
            log_event(
                "payment-service",
                "SYSTEM",
                "Consumer error",
                {"error": str(e)},
                level="ERROR"
            )
            time.sleep(5)