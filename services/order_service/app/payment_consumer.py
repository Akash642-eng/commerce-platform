import pika
import json
import time
import redis
import os

from .database import SessionLocal
from .models import Order
from .state_machine import can_transition
from .logger import log_event
from .config import settings

from .metrics import EVENTS_PROCESSED, EVENTS_FAILED

from shared.config.settings import settings

ENV = settings.ENV

RABBITMQ_HOST = settings.RABBITMQ_HOST

redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=6379,
    decode_responses=True
)

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

    trace_id = "unknown"

    try:
        data = json.loads(body)

        headers = properties.headers or {}
        retry_count = headers.get("x-retry", 0)
        trace_id = headers.get("x-trace-id", "unknown")

        log_event(
            "order-service",
            trace_id,
            f"Event received (retry={retry_count})",
            data
        )

        order = db.query(Order).filter(
            Order.id == data["order_id"]
        ).first()

        if not order:
            log_event(
                "order-service",
                trace_id,
                "Order not found",
                data,
                level="WARNING"
            )

            EVENTS_FAILED.labels(
                "order-service",
                "order_not_found"
            ).inc()

            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        status = data.get("status")
        event_id = f"order:{order.id}:{status}"

        if redis_client.get(event_id):
            log_event(
                "order-service",
                trace_id,
                "Duplicate event skipped",
                {"event_id": event_id},
                level="WARNING"
            )

            EVENTS_FAILED.labels(
                "order-service",
                "duplicate_event"
            ).inc()

            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        redis_client.set(event_id, "1", ex=3600)

        # ---------------- RESERVED ----------------

        if status == "RESERVED":

            old_status = order.status

            if can_transition(order.status, "RESERVED"):

                order.status = "RESERVED"
                db.commit()

                EVENTS_PROCESSED.labels(
                    "order-service",
                    "inventory_reserved"
                ).inc()

                log_event(
                    "order-service",
                    trace_id,
                    "State transition",
                    {
                        "order_id": order.id,
                        "from": old_status,
                        "to": "RESERVED"
                    }
                )

            else:
                raise Exception(
                    f"Invalid transition {order.status} → RESERVED"
                )

        # ---------------- SUCCESS ----------------

        elif status == "SUCCESS":

            old_status = order.status

            if can_transition(order.status, "PAID"):

                order.status = "PAID"
                db.commit()

                EVENTS_PROCESSED.labels(
                    "order-service",
                    "payment_completed"
                ).inc()

                log_event(
                    "order-service",
                    trace_id,
                    "State transition",
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
                    "Fixing out-of-order",
                    {"order_id": order.id},
                    level="WARNING"
                )

                order.status = "RESERVED"
                db.commit()

                order.status = "PAID"
                db.commit()

                EVENTS_PROCESSED.labels(
                    "order-service",
                    "forced_paid_transition"
                ).inc()

                log_event(
                    "order-service",
                    trace_id,
                    "Forced transition",
                    {
                        "order_id": order.id,
                        "to": "PAID"
                    }
                )

        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:

        err = str(e) if ENV == "dev" else "processing error"

        EVENTS_FAILED.labels(
            "order-service",
            "payment_processing"
        ).inc()

        log_event(
            "order-service",
            trace_id,
            "Processing error",
            {"error": err},
            level="ERROR"
        )

        headers = properties.headers or {}
        retry_count = headers.get("x-retry", 0)

        if retry_count < MAX_RETRIES:

            new_headers = headers.copy()

            new_headers["x-retry"] = retry_count + 1
            new_headers["x-trace-id"] = trace_id

            log_event(
                "order-service",
                trace_id,
                f"Retrying message ({retry_count + 1})",
                {},
                level="WARNING"
            )

            publish_to_queue(
                ch,
                "payment_completed",
                json.loads(body),
                headers=new_headers
            )

        else:

            EVENTS_FAILED.labels(
                "order-service",
                "dlq_sent"
            ).inc()

            log_event(
                "order-service",
                trace_id,
                "Sending to DLQ",
                {},
                level="ERROR"
            )

            publish_to_queue(
                ch,
                "payment_completed_dlq",
                json.loads(body),
                headers=headers
            )

        ch.basic_ack(delivery_tag=method.delivery_tag)

    finally:
        db.close()


def start_payment_consumer():

    log_event(
        "order-service",
        "SYSTEM",
        f"Payment consumer started ({ENV})"
    )

    while True:

        try:

            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=RABBITMQ_HOST)
            )

            channel = connection.channel()

            channel.queue_declare(
                queue="payment_completed",
                durable=True
            )

            channel.queue_declare(
                queue="payment_completed_dlq",
                durable=True
            )

            channel.basic_consume(
                queue="payment_completed",
                on_message_callback=callback,
                auto_ack=False
            )

            log_event(
                "order-service",
                "SYSTEM",
                "Waiting for payment events"
            )

            channel.start_consuming()

        except Exception as e:

            log_event(
                "order-service",
                "SYSTEM",
                "Retrying consumer",
                {"error": str(e)},
                level="ERROR"
            )

            time.sleep(5)


def start_inventory_consumer():

    log_event(
        "order-service",
        "SYSTEM",
        f"Inventory consumer started ({ENV})"
    )

    while True:

        try:

            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=RABBITMQ_HOST)
            )

            channel = connection.channel()

            channel.queue_declare(
                queue="inventory_reserved",
                durable=True
            )

            channel.queue_declare(
                queue="inventory_reserved_dlq",
                durable=True
            )

            channel.basic_consume(
                queue="inventory_reserved",
                on_message_callback=callback,
                auto_ack=False
            )

            log_event(
                "order-service",
                "SYSTEM",
                "Waiting for inventory_reserved events"
            )

            channel.start_consuming()

        except Exception as e:

            log_event(
                "order-service",
                "SYSTEM",
                "Retrying consumer",
                {"error": str(e)},
                level="ERROR"
            )

            time.sleep(5)