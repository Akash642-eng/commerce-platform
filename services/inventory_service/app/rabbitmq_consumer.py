import pika
import json
import os
import time

from .logger import log_event
from .metrics import EVENTS_PROCESSED
from .metrics import EVENTS_FAILED

from shared.config.settings import settings

RABBITMQ_HOST = settings.RABBITMQ_HOST

MAX_RETRIES = 3


def get_connection():

    while True:

        try:

            return pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=RABBITMQ_HOST,
                    heartbeat=600,
                    blocked_connection_timeout=300
                )
            )

        except Exception:

            EVENTS_FAILED.labels(
                "inventory-service",
                "rabbitmq_connection"
            ).inc()

            log_event(
                "inventory-service",
                "SYSTEM",
                "RabbitMQ connection failed",
                {},
                level="WARNING"
            )

            time.sleep(5)


def publish_to_queue(
    queue_name,
    message,
    trace_id,
    headers=None
):

    connection = get_connection()

    channel = connection.channel()

    channel.queue_declare(
        queue=queue_name,
        durable=True
    )

    final_headers = headers.copy() if headers else {}

    final_headers["x-trace-id"] = trace_id

    channel.basic_publish(
        exchange='',
        routing_key=queue_name,
        body=json.dumps(message),
        properties=pika.BasicProperties(
            delivery_mode=2,
            headers=final_headers
        )
    )

    log_event(
        "inventory-service",
        trace_id,
        f"Published to {queue_name}",
        message
    )

    connection.close()


def publish_inventory_event(
    data,
    trace_id
):

    event = {
        "version": "v1",
        "order_id": data["order_id"],
        "status": "RESERVED"
    }

    publish_to_queue(
        "inventory_reserved_order",
        event,
        trace_id
    )

    publish_to_queue(
        "inventory_reserved_payment",
        event,
        trace_id
    )

    EVENTS_PROCESSED.labels(
        "inventory-service",
        "inventory_reserved"
    ).inc()

    log_event(
        "inventory-service",
        trace_id,
        "Inventory reserved",
        event
    )


def callback(
    ch,
    method,
    properties,
    body
):

    trace_id = "unknown"

    try:

        data = json.loads(body)

        headers = properties.headers or {}

        trace_id = headers.get(
            "x-trace-id",
            "unknown"
        )

        log_event(
            "inventory-service",
            trace_id,
            "Inventory received",
            data
        )

        time.sleep(1)

        publish_inventory_event(
            data,
            trace_id
        )

        ch.basic_ack(
            delivery_tag=method.delivery_tag
        )

    except Exception as e:

        EVENTS_FAILED.labels(
            "inventory-service",
            "inventory_failed"
        ).inc()

        log_event(
            "inventory-service",
            trace_id,
            "Inventory error",
            {
                "error": str(e)
            },
            level="ERROR"
        )

        ch.basic_ack(
            delivery_tag=method.delivery_tag
        )


def start_consumer():

    log_event(
        "inventory-service",
        "SYSTEM",
        "Inventory consumer started"
    )

    while True:

        try:

            connection = get_connection()

            channel = connection.channel()

            channel.queue_declare(
                queue="order_created",
                durable=True
            )

            channel.queue_declare(
                queue="inventory_reserved_order",
                durable=True
            )

            channel.queue_declare(
                queue="inventory_reserved_payment",
                durable=True
            )

            channel.basic_qos(
                prefetch_count=1
            )

            channel.basic_consume(
                queue="order_created",
                on_message_callback=callback,
                auto_ack=False
            )

            log_event(
                "inventory-service",
                "SYSTEM",
                "Waiting for order_created"
            )

            channel.start_consuming()

        except Exception as e:

            EVENTS_FAILED.labels(
                "inventory-service",
                "consumer_crash"
            ).inc()

            log_event(
                "inventory-service",
                "SYSTEM",
                "Consumer crash",
                {
                    "error": str(e)
                },
                level="ERROR"
            )

            time.sleep(5)