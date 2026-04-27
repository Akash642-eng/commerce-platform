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

        print("💰 Payment event received:", data, flush=True)

        order = db.query(Order).filter(Order.id == data["order_id"]).first()

        if not order:
            print("❌ Order not found", flush=True)
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        # ✅ IDEMPOTENCY (CRITICAL)
        if order.status == "PAID":
            print(f"⚠️ Duplicate event ignored for order {order.id}", flush=True)
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        # ✅ Normal valid transition
        if can_transition(order.status, "PAID"):
            order.status = "PAID"
            db.commit()
            print(f"✅ Order {order.id} moved to PAID", flush=True)

        # 🔥 handle out-of-order events (CREATED → PAID)
        elif order.status == "CREATED":
            print(f"⚠️ Missing RESERVED, auto-fixing for order {order.id}", flush=True)

            order.status = "RESERVED"
            db.commit()

            order.status = "PAID"
            db.commit()

            print(f"✅ Order {order.id} force-moved CREATED → RESERVED → PAID", flush=True)

        # ❌ truly invalid case
        else:
            print(f"⚠️ Invalid transition {order.status} → PAID", flush=True)

        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print("❌ Error:", str(e), flush=True)

    finally:
        db.close()


def start_payment_consumer():
    print("🚀 Order service consumer started", flush=True)

    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=RABBITMQ_HOST)
            )

            channel = connection.channel()

            channel.queue_declare(queue="payment_completed", durable=True)

            channel.basic_consume(
                queue="payment_completed",
                on_message_callback=callback,
                auto_ack=False
            )

            print("📡 Waiting for payment events...", flush=True)
            channel.start_consuming()

        except Exception as e:
            print("❌ Retry:", repr(e), flush=True)
            time.sleep(5)