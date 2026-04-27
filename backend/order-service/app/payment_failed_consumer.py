import pika
import json
import os
import time
from .database import SessionLocal
from .models import Order
from .state_machine import can_transition

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")


def publish_inventory_release(data):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST)
    )
    channel = connection.channel()

    event = {
        "order_id": data["order_id"],
        "status": "RELEASED"
    }

    channel.queue_declare(queue="inventory_release", durable=True)

    channel.basic_publish(
        exchange='',
        routing_key="inventory_release",
        body=json.dumps(event),
        properties=pika.BasicProperties(delivery_mode=2)
    )

    print("🔄 Sent inventory_release event:", event, flush=True)

    connection.close()


def callback(ch, method, properties, body):
    db = SessionLocal()

    try:
        data = json.loads(body)

        print("❌ Payment failed event received:", data, flush=True)

        order = db.query(Order).filter(Order.id == data["order_id"]).first()

        if not order:
            print("❌ Order not found", flush=True)
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        # ✅ IDEMPOTENCY (CRITICAL)
        if order.status == "FAILED":
            print(f"⚠️ Duplicate FAILED ignored for order {order.id}", flush=True)
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        if can_transition(order.status, "FAILED"):
            order.status = "FAILED"
            db.commit()
            print(f"🚫 Order {order.id} moved to FAILED", flush=True)

            # 🔥 rollback only once
            publish_inventory_release(data)

        else:
            print(f"⚠️ Invalid transition {order.status} → FAILED", flush=True)

        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print("❌ Error:", str(e), flush=True)

    finally:
        db.close()


def start_failed_consumer():
    print("🚀 Payment FAILED consumer started", flush=True)

    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=RABBITMQ_HOST)
            )

            channel = connection.channel()

            channel.queue_declare(queue="payment_failed", durable=True)

            channel.basic_consume(
                queue="payment_failed",
                on_message_callback=callback,
                auto_ack=False
            )

            print("📡 Waiting for payment_failed events...", flush=True)
            channel.start_consuming()

        except Exception as e:
            print("❌ Retry:", str(e), flush=True)
            time.sleep(5)