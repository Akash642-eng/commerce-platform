import pika
import json
import os
import time
from .database import SessionLocal
from .models import Order
from .state_machine import can_transition

from .logger import log_event

from shared.config.settings import settings

RABBITMQ_HOST = settings.RABBITMQ_HOST


def callback(ch, method, properties, body):
    db = SessionLocal()

    try:
        data = json.loads(body)

        headers = properties.headers or {}
        trace_id = headers.get("x-trace-id", "unknown")

        log_event("order-service", trace_id, f"Inventory event received: {data}", data)

        order = db.query(Order).filter(Order.id == data["order_id"]).first()

        if order and can_transition(order.status, "RESERVED"):
            order.status = "RESERVED"
            db.commit()

        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        log_event("order-service", "SYSTEM", "Error processing inventory event", {"error": str(e)}, level="ERROR")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    finally:
        db.close()


def start_inventory_consumer():
    log_event("order-service", "SYSTEM", "Inventory consumer started", {})

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

            log_event("order-service", "SYSTEM", "Waiting for inventory_reserved_order...", {})

            channel.start_consuming()

        except Exception as e:
            log_event("order-service", "SYSTEM", "Consumer retry", {"error": str(e)}, level="ERROR")
            time.sleep(5)