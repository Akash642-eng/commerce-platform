import pika
import json
import os
import time

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")

def publish_inventory_event(channel, data):
    event = {
        "order_id": data["order_id"],
        "status": "RESERVED"
    }

    channel.queue_declare(queue="inventory_reserved", durable=True)

    channel.basic_publish(
        exchange='',
        routing_key="inventory_reserved",
        body=json.dumps(event),
        properties=pika.BasicProperties(delivery_mode=2)
    )

    print("📦 Sent inventory_reserved event:", event, flush=True)


def callback(ch, method, properties, body):
    try:
        data = json.loads(body)

        print("📥 Inventory received order:", data, flush=True)

        # 👉 simulate stock check
        time.sleep(1)

        publish_inventory_event(ch, data)

        ch.basic_ack(delivery_tag=method.delivery_tag)

        print("✅ Inventory reserved", flush=True)

    except Exception as e:
        print("❌ Inventory error:", str(e), flush=True)


def start_consumer():
    print("🚀 Inventory consumer started", flush=True)

    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=RABBITMQ_HOST)
            )

            channel = connection.channel()

            channel.queue_declare(queue="order_created", durable=True)

            channel.basic_consume(
                queue="order_created",
                on_message_callback=callback,
                auto_ack=False
            )

            print("📡 Waiting for order_created...", flush=True)
            channel.start_consuming()

        except Exception as e:
            print("❌ Retry:", str(e), flush=True)
            time.sleep(5)