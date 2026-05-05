import pika
import json
import os
import time

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")


def get_connection():
    while True:
        try:
            return pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=RABBITMQ_HOST,
                    heartbeat=600,
                    blocked_connection_timeout=300
                )
            )
        except:
            print("❌ Retry connection in 5s...", flush=True)
            time.sleep(5)


def callback(ch, method, properties, body):
    try:
        data = json.loads(body)

        print("🔄 Inventory release received:", data, flush=True)

        time.sleep(1)

        print(f"📦 Stock released for order {data['order_id']}", flush=True)

        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print("❌ Release error:", str(e), flush=True)


def start_release_consumer():
    print("🚀 Inventory release consumer started", flush=True)

    while True:
        try:
            connection = get_connection()
            channel = connection.channel()

            channel.queue_declare(queue="inventory_release", durable=True)

            channel.basic_consume(
                queue="inventory_release",
                on_message_callback=callback,
                auto_ack=False
            )

            print("📡 Waiting for inventory_release...", flush=True)

            channel.start_consuming()

        except Exception as e:
            print("❌ Retry:", str(e), flush=True)
            time.sleep(5)