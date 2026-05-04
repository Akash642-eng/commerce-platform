import pika
import json
import os
import time
from .database import SessionLocal
from .models import Order
from .state_machine import can_transition

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")

MAX_RETRIES = 3


# ---------- COMMON PUBLISH ----------
def publish(queue, message, headers=None):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST)
    )
    channel = connection.channel()

    channel.queue_declare(queue=queue, durable=True)

    channel.basic_publish(
        exchange='',
        routing_key=queue,
        body=json.dumps(message),
        properties=pika.BasicProperties(
            delivery_mode=2,
            headers=headers or {}
        )
    )

    connection.close()


# ---------- INVENTORY RELEASE ----------
def publish_inventory_release(data, trace_id):
    event = {
        "order_id": data["order_id"],
        "status": "RELEASED"
    }

    publish("inventory_release", event, headers={"x-trace-id": trace_id})

    print("🔄 Sent inventory_release event:", event, flush=True)


# ---------- CALLBACK ----------
def callback(ch, method, properties, body):
    db = SessionLocal()
    trace_id = "N/A"

    try:
        data = json.loads(body)

        headers = properties.headers or {}
        trace_id = headers.get("x-trace-id", "N/A")
        retry_count = headers.get("x-retry", 0)

        print(f"❌ Payment failed event received (retry={retry_count}):", data, flush=True)

        order = db.query(Order).filter(Order.id == data["order_id"]).first()

        if not order:
            print("❌ Order not found", flush=True)
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        # ✅ IDEMPOTENCY
        if order.status == "FAILED":
            print(f"⚠️ Duplicate FAILED ignored for order {order.id}", flush=True)
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        if can_transition(order.status, "FAILED"):
            order.status = "FAILED"
            db.commit()
            print(f"🚫 Order {order.id} moved to FAILED", flush=True)

            # rollback inventory
            publish_inventory_release(data, trace_id)

        else:
            raise Exception(f"Invalid transition {order.status} → FAILED")

        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print("❌ Error:", str(e), flush=True)

        headers = properties.headers or {}
        retry_count = headers.get("x-retry", 0)

        if retry_count < MAX_RETRIES:
            new_headers = headers.copy()
            new_headers["x-retry"] = retry_count + 1

            print(f"🔁 Retrying... {retry_count + 1}", flush=True)

            publish(
                "payment_failed",
                json.loads(body),
                headers=new_headers
            )

        else:
            print("💀 Sending to DLQ", flush=True)

            publish(
                "payment_failed_dlq",
                json.loads(body),
                headers=headers
            )

        ch.basic_ack(delivery_tag=method.delivery_tag)

    finally:
        db.close()


# ---------- CONSUMER ----------
def start_failed_consumer():
    print("🚀 Payment FAILED consumer started", flush=True)

    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=RABBITMQ_HOST)
            )

            channel = connection.channel()

            channel.queue_declare(queue="payment_failed", durable=True)
            channel.queue_declare(queue="payment_failed_dlq", durable=True)

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