import pika
import json
import os
import time
import redis

from .database import SessionLocal
from .models import Order
from .state_machine import can_transition

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")

# 🔥 REDIS (Idempotency)
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
redis_client = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)


def callback(ch, method, properties, body):
    db = SessionLocal()

    try:
        data = json.loads(body)

        trace_id = properties.headers.get("x-trace-id") if properties.headers else "N/A"

        print(f"[TRACE {trace_id}] 📦 Event received: {data}", flush=True)

        order = db.query(Order).filter(Order.id == data["order_id"]).first()

        if not order:
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        status = data.get("status")

        # 🔥 IDEMPOTENCY KEY (VERY IMPORTANT)
        event_id = f"order:{order.id}:{status}"

        if redis_client.get(event_id):
            print(f"[TRACE {trace_id}] ⚠️ Duplicate skipped ({event_id})", flush=True)
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        # mark processed
        redis_client.set(event_id, "1", ex=3600)

        # ============================
        # 🎯 HANDLE INVENTORY RESERVED
        # ============================
        if status == "RESERVED":
            if can_transition(order.status, "RESERVED"):
                order.status = "RESERVED"
                db.commit()
                print(f"[TRACE {trace_id}] Order {order.id} → RESERVED", flush=True)
            else:
                print(f"[TRACE {trace_id}] ⚠️ Invalid transition {order.status} → RESERVED", flush=True)

        # ============================
        # 💰 HANDLE PAYMENT SUCCESS
        # ============================
        elif status == "SUCCESS":
            if can_transition(order.status, "PAID"):
                order.status = "PAID"
                db.commit()
                print(f"[TRACE {trace_id}] Order {order.id} → PAID", flush=True)

            elif order.status == "CREATED":
                print(f"[TRACE {trace_id}] ⚠️ Fixing CREATED → RESERVED → PAID", flush=True)

                order.status = "RESERVED"
                db.commit()

                order.status = "PAID"
                db.commit()

                print(f"[TRACE {trace_id}] Order {order.id} force → PAID", flush=True)

            else:
                print(f"[TRACE {trace_id}] ⚠️ Invalid transition {order.status} → PAID", flush=True)

        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print(f"❌ Error: {str(e)}", flush=True)

    finally:
        db.close()


# ============================
# 💰 PAYMENT CONSUMER
# ============================
def start_payment_consumer():
    print("🚀 Payment consumer started", flush=True)

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
            print("❌ Retry:", str(e), flush=True)
            time.sleep(5)


# ============================
# 📦 INVENTORY CONSUMER
# ============================
def start_inventory_consumer():
    print("🚀 Inventory consumer (order-service) started", flush=True)

    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=RABBITMQ_HOST)
            )

            channel = connection.channel()
            channel.queue_declare(queue="inventory_reserved", durable=True)

            channel.basic_consume(
                queue="inventory_reserved",
                on_message_callback=callback,
                auto_ack=False
            )

            print("📡 Waiting for inventory_reserved events...", flush=True)
            channel.start_consuming()

        except Exception as e:
            print("❌ Retry:", str(e), flush=True)
            time.sleep(5)