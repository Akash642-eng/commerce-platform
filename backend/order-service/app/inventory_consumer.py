import pika
import json
import os
import time
from .database import SessionLocal
from .models import Order
from .state_machine import can_transition

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")

MAX_RETRIES = 3


def publish_to_queue(channel, queue_name, message, headers=None):
    channel.basic_publish(
        exchange='',
        routing_key=queue_name,
        body=json.dumps(message),
        properties=pika.BasicProperties(
            delivery_mode=2,
            headers=headers or {}
        )
    )


def callback(ch, method, properties, body):
    db = SessionLocal()

    try:
        data = json.loads(body)
        headers = properties.headers or {}
        retry_count = headers.get("x-retry", 0)

        print(f"📦 Inventory event received (retry={retry_count}): {data}", flush=True)

        order = db.query(Order).filter(Order.id == data["order_id"]).first()

        if order:
            if can_transition(order.status, "RESERVED"):
                order.status = "RESERVED"
                db.commit()
                print(f"📦 Order {order.id} moved to RESERVED", flush=True)
            else:
                raise Exception(f"Invalid transition {order.status} → RESERVED")

        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print(f"❌ Error: {str(e)}", flush=True)

        headers = properties.headers or {}
        retry_count = headers.get("x-retry", 0)

        if retry_count < MAX_RETRIES:
            new_headers = headers.copy()
            new_headers["x-retry"] = retry_count + 1

            print(f"🔁 Retrying... attempt {retry_count + 1}", flush=True)

            publish_to_queue(
                ch,
                "inventory_reserved",
                json.loads(body),
                headers=new_headers
            )
        else:
            print("💀 Sending to DLQ", flush=True)

            publish_to_queue(
                ch,
                "inventory_reserved_dlq",
                json.loads(body),
                headers=headers
            )

        ch.basic_ack(delivery_tag=method.delivery_tag)

    finally:
        db.close()


def start_inventory_consumer():
    print("🚀 Inventory consumer (order-service) started", flush=True)

    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=RABBITMQ_HOST)
            )

            channel = connection.channel()

            # main queue
            channel.queue_declare(queue="inventory_reserved", durable=True)

            # DLQ
            channel.queue_declare(queue="inventory_reserved_dlq", durable=True)

            channel.basic_consume(
                queue="inventory_reserved",
                on_message_callback=callback,
                auto_ack=False
            )

            print("📡 Waiting for inventory_reserved events...", flush=True)
            channel.start_consuming()

        except Exception as e:
            print("❌ Connection retry:", str(e), flush=True)
            time.sleep(5)