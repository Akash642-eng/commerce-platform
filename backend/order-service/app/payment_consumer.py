import pika
import json
import os
import time
from .database import SessionLocal
from .models import Order
from .state_machine import can_transition

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")


def extract_trace(properties):
    if properties and properties.headers:
        return properties.headers.get("x-trace-id", "N/A")
    return "N/A"


# ✅ PAYMENT SUCCESS
def payment_callback(ch, method, properties, body):
    db = SessionLocal()

    try:
        data = json.loads(body)
        trace_id = extract_trace(properties)

        print(f"[TRACE {trace_id}] 💰 Payment event: {data}", flush=True)

        order = db.query(Order).filter(Order.id == data["order_id"]).first()

        if order and can_transition(order.status, "PAID"):
            order.status = "PAID"
            db.commit()
            print(f"[TRACE {trace_id}] Order {order.id} → PAID", flush=True)

        ch.basic_ack(delivery_tag=method.delivery_tag)

    finally:
        db.close()


# ✅ INVENTORY RESERVED
def inventory_callback(ch, method, properties, body):
    db = SessionLocal()

    try:
        data = json.loads(body)
        trace_id = extract_trace(properties)

        print(f"[TRACE {trace_id}] 📦 Inventory event: {data}", flush=True)

        order = db.query(Order).filter(Order.id == data["order_id"]).first()

        if order and can_transition(order.status, "RESERVED"):
            order.status = "RESERVED"
            db.commit()
            print(f"[TRACE {trace_id}] Order {order.id} → RESERVED", flush=True)

        ch.basic_ack(delivery_tag=method.delivery_tag)

    finally:
        db.close()


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
                on_message_callback=payment_callback,
                auto_ack=False
            )

            print("📡 Waiting for payment events...", flush=True)
            channel.start_consuming()

        except Exception as e:
            print("❌ Retry:", str(e), flush=True)
            time.sleep(5)


def start_inventory_consumer():
    print("🚀 Inventory consumer started", flush=True)

    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=RABBITMQ_HOST)
            )

            channel = connection.channel()
            channel.queue_declare(queue="inventory_reserved", durable=True)

            channel.basic_consume(
                queue="inventory_reserved",
                on_message_callback=inventory_callback,
                auto_ack=False
            )

            print("📡 Waiting for inventory_reserved events...", flush=True)
            channel.start_consuming()

        except Exception as e:
            print("❌ Retry:", str(e), flush=True)
            time.sleep(5)