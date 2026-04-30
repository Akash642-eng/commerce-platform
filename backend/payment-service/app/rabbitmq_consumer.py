import pika
import json
import os
import time
import random
import redis

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

    print(f"[TRACE {trace_id}] 📤 Sent {queue}: {event}", flush=True)

    connection.close()


def callback(ch, method, properties, body):
    try:
        data = json.loads(body)

        trace_id = properties.headers.get("x-trace-id") if properties.headers else "N/A"

        # 🔥 IDEMPOTENCY KEY
        event_id = f"payment:{data['order_id']}"

        # 🛑 DUPLICATE CHECK
        if redis_client.get(event_id):
            print(f"[TRACE {trace_id}] ⚠️ Duplicate event skipped", flush=True)
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        # mark event as processed (TTL 1 hour)
        redis_client.set(event_id, "1", ex=3600)

        print(f"[TRACE {trace_id}] 💳 Processing payment: {data}", flush=True)

        # 🔥 simulate failure
        if data["order_id"] % 5 == 0:
            raise Exception("Simulated payment failure")

        time.sleep(1)

        publish_payment_event(data, trace_id)

        ch.basic_ack(delivery_tag=method.delivery_tag)

        print(f"[TRACE {trace_id}] ✅ Payment processed + ACK sent", flush=True)

    except Exception as e:
        print(f"[TRACE {trace_id}] ❌ Processing failed: {str(e)}", flush=True)

        retry_count = data.get("retry", 0)

        # 🚫 SEND TO DLQ AFTER 3 RETRIES
        if retry_count >= 3:
            print(f"[TRACE {trace_id}] 🚫 Max retries reached → sending to DLQ", flush=True)

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

            print(f"[TRACE {trace_id}] 💀 Sent to DLQ", flush=True)

            ch.basic_ack(delivery_tag=method.delivery_tag)

        else:
            # 🔁 RETRY
            data["retry"] = retry_count + 1

            ch.basic_publish(
                exchange='',
                routing_key="inventory_reserved",
                body=json.dumps(data),
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    headers={"x-trace-id": trace_id}
                )
            )

            print(f"[TRACE {trace_id}] 🔁 Retrying... ({data['retry']})", flush=True)

            ch.basic_ack(delivery_tag=method.delivery_tag)


def start_consumer():
    print("🚀 Payment consumer started", flush=True)

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

            # ✅ DECLARE ALL QUEUES
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

            print("📡 Waiting for inventory_reserved...", flush=True)

            channel.start_consuming()

        except Exception as e:
            print("❌ ERROR:", str(e), flush=True)
            print("🔁 Retrying in 5 seconds...", flush=True)
            time.sleep(5)