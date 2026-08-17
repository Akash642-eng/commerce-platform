import json
import time

import pika

from shared.config.settings import settings

from .database import SessionLocal
from .logger import log_event
from .models import Order
from .state_machine import can_transition

RABBITMQ_HOST = settings.RABBITMQ_HOST


def callback(ch, method, properties, body):

    db = SessionLocal()

    trace_id = "unknown"

    try:

        data = json.loads(body)

        headers = properties.headers or {}

        trace_id = headers.get("x-trace-id", "unknown")

        saga_id = headers.get("x-saga-id", data.get("saga_id"))

        correlation_id = headers.get(
            "x-correlation-id",
            data.get("correlation_id"),
        )

        event_version = headers.get(
            "x-event-version",
            data.get("event_version", "v1"),
        )

        log_event(
            service="order-service",
            event="inventory_reserved",
            trace_id=trace_id,
            message="Inventory reservation event received",
            data={
                "payload": data,
                "saga_id": saga_id,
                "correlation_id": correlation_id,
                "event_version": event_version,
            },
        )

        order = (
            db.query(Order)
            .filter(Order.id == data["order_id"])
            .first()
        )

        if order is None:

            log_event(
                service="order-service",
                event="order_not_found",
                trace_id=trace_id,
                message="Order not found",
                data=data,
                level="WARNING",
            )

            ch.basic_ack(delivery_tag=method.delivery_tag)

            return

        if can_transition(order.status, "RESERVED"):

            old_status = order.status

            order.status = "RESERVED"

            order.saga_id = saga_id

            order.correlation_id = correlation_id

            order.event_version = event_version

            db.commit()

            log_event(
                service="order-service",
                event="state_transition",
                trace_id=trace_id,
                message="Inventory reserved",
                data={
                    "order_id": order.id,
                    "from": old_status,
                    "to": "RESERVED",
                    "saga_id": saga_id,
                },
            )

        else:

            log_event(
                service="order-service",
                event="invalid_transition",
                trace_id=trace_id,
                message=f"Cannot transition {order.status} -> RESERVED",
                data={
                    "order_id": order.id,
                    "current_status": order.status,
                },
                level="WARNING",
            )

        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:

        log_event(
            service="order-service",
            event="inventory_consumer_error",
            trace_id=trace_id,
            message="Inventory consumer failed",
            data={"error": str(e)},
            level="ERROR",
        )

        ch.basic_ack(delivery_tag=method.delivery_tag)

    finally:

        db.close()


def start_inventory_consumer():

    log_event(
        service="order-service",
        event="consumer_started",
        trace_id="SYSTEM",
        message="Inventory consumer started",
        data={},
    )

    while True:

        try:

            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=RABBITMQ_HOST
                )
            )

            channel = connection.channel()

            channel.queue_declare(
                queue="inventory_reserved_order",
                durable=True,
            )

            channel.basic_qos(
                prefetch_count=1,
            )

            channel.basic_consume(
                queue="inventory_reserved_order",
                on_message_callback=callback,
                auto_ack=False,
            )

            log_event(
                service="order-service",
                event="consumer_waiting",
                trace_id="SYSTEM",
                message="Waiting for inventory events",
                data={},
            )

            channel.start_consuming()

        except Exception as e:

            log_event(
                service="order-service",
                event="consumer_restart",
                trace_id="SYSTEM",
                message="Restarting inventory consumer",
                data={"error": str(e)},
                level="ERROR",
            )

            time.sleep(5)