import pika
import json
import os
import time
from .database import SessionLocal
from .models import Order
from .state_machine import can_transition

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")


def callback(ch, method, properties, body):
    db = SessionLocal()

    try:
        data = json.loads(body)

        headers = properties.headers or {}
        trace_id = headers.get("x-trace-id", "unknown")

        print(f"📦 Inventory event received: {data} trace={trace_id}", flush=True)

        order = db.query(Order).filter(Order.id == data["order_id"]).first()

        if order and can_transition(order.status, "RESERVED"):
            order.status = "RESERVED"
            db.commit()

        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print(f"❌ Error: {str(e)}", flush=True)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    finally:
        db.close()


def start_inventory_consumer():
    print("🚀 Inventory consumer started", flush=True)

    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=RABBITMQ_HOST)
            )

            channel = connection.channel()

            channel.queue_declare(queue="inventory_reserved_order", durable=True)

            channel.basic_consume(
                queue="inventory_reserved_order",
                on_message_callback=callback,
                auto_ack=False
            )

            print("📡 Waiting for inventory_reserved_order...", flush=True)

            channel.start_consuming()

        except Exception as e:
            print("Retry:", str(e), flush=True)
            time.sleep(5)