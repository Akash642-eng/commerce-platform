import pika
import json
import os
import time
import redis

from .database import SessionLocal
from .models import Order
from .state_machine import can_transition
from .logger import log_event
from .config import settings  # ✅ NEW

RABBITMQ_HOST = settings.RABBITMQ_HOST  # ✅ UPDATED

# 🔥 REDIS (Idempotency)
redis_client = redis.Redis(  # ✅ UPDATED
    host=settings.REDIS_HOST,
    port=6379,
    decode_responses=True
)


def callback(ch, method, properties, body):
    db = SessionLocal()

    try:
        data = json.loads(body)

        trace_id = properties.headers.get("x-trace-id") if properties and properties.headers else "N/A"

        log_event("order-service", trace_id, "Event received", data)

        order = db.query(Order).filter(Order.id == data["order_id"]).first()

        if not order:
            log_event("order-service", trace_id, "Order not found", data, level="WARNING")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        status = data.get("status")

        # 🔥 IDEMPOTENCY KEY
        event_id = f"order:{order.id}:{status}"

        if redis_client.get(event_id):
            log_event(
                "order-service",
                trace_id,
                "Duplicate event skipped",
                {"event_id": event_id},
                level="WARNING"
            )
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        # mark processed
        redis_client.set(event_id, "1", ex=3600)

        # ============================
        # 🎯 HANDLE INVENTORY RESERVED
        # ============================
        if status == "RESERVED":
            old_status = order.status

            if can_transition(order.status, "RESERVED"):
                order.status = "RESERVED"
                db.commit()

                log_event(
                    "order-service",
                    trace_id,
                    "Order state transition",
                    {
                        "order_id": order.id,
                        "from": old_status,
                        "to": "RESERVED"
                    }
                )
            else:
                log_event(
                    "order-service",
                    trace_id,
                    "Invalid transition",
                    {
                        "order_id": order.id,
                        "from": order.status,
                        "to": "RESERVED"
                    },
                    level="WARNING"
                )

        # ============================
        # 💰 HANDLE PAYMENT SUCCESS
        # ============================
        elif status == "SUCCESS":
            old_status = order.status

            if can_transition(order.status, "PAID"):
                order.status = "PAID"
                db.commit()

                log_event(
                    "order-service",
                    trace_id,
                    "Order state transition",
                    {
                        "order_id": order.id,
                        "from": old_status,
                        "to": "PAID"
                    }
                )

            elif order.status == "CREATED":
                log_event(
                    "order-service",
                    trace_id,
                    "Fixing out-of-order event",
                    {"order_id": order.id},
                    level="WARNING"
                )

                order.status = "RESERVED"
                db.commit()

                order.status = "PAID"
                db.commit()

                log_event(
                    "order-service",
                    trace_id,
                    "Order force transitioned",
                    {
                        "order_id": order.id,
                        "from": "CREATED",
                        "to": "PAID"
                    }
                )

            else:
                log_event(
                    "order-service",
                    trace_id,
                    "Invalid transition",
                    {
                        "order_id": order.id,
                        "from": order.status,
                        "to": "PAID"
                    },
                    level="WARNING"
                )

        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        log_event(
            "order-service",
            trace_id if 'trace_id' in locals() else "N/A",
            "Processing error",
            {"error": str(e)},
            level="ERROR"
        )

    finally:
        db.close()


# ============================
# 💰 PAYMENT CONSUMER
# ============================
def start_payment_consumer():
    log_event("order-service", "SYSTEM", "Payment consumer started")

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

            log_event("order-service", "SYSTEM", "Waiting for payment events")

            channel.start_consuming()

        except Exception as e:
            log_event(
                "order-service",
                "SYSTEM",
                "Consumer retry",
                {"error": str(e)},
                level="ERROR"
            )
            time.sleep(5)


# ============================
# 📦 INVENTORY CONSUMER
# ============================
def start_inventory_consumer():
    log_event("order-service", "SYSTEM", "Inventory consumer started")

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

            log_event("order-service", "SYSTEM", "Waiting for inventory_reserved events")

            channel.start_consuming()

        except Exception as e:
            log_event(
                "order-service",
                "SYSTEM",
                "Consumer retry",
                {"error": str(e)},
                level="ERROR"
            )
            time.sleep(5)