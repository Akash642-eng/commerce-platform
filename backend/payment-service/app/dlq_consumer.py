import pika
import json
import os
import time

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")


def callback(ch, method, properties, body):
    data = json.loads(body)

    print("💀 DLQ MESSAGE RECEIVED:", data, flush=True)

    ch.basic_ack(delivery_tag=method.delivery_tag)


def start_dlq_consumer():
    print("🚀 DLQ consumer started", flush=True)

    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=RABBITMQ_HOST)
            )

            channel = connection.channel()

            channel.queue_declare(queue="payment_dlq", durable=True)

            channel.basic_consume(
                queue="payment_dlq",
                on_message_callback=callback,
                auto_ack=False
            )

            print("📡 Waiting for DLQ messages...", flush=True)

            channel.start_consuming()

        except Exception as e:
            print("❌ DLQ ERROR:", str(e), flush=True)
            time.sleep(5)