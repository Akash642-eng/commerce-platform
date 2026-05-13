import pika
import json
import os
import time

from .logger import log_event


from shared.config.settings import settings

RABBITMQ_HOST = settings.RABBITMQ_HOST


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

            log_event(
                "inventory-service",
                "SYSTEM",
                "RabbitMQ release connection failed",
                {},
                level="ERROR"
            )

            time.sleep(5)


def callback(
    ch,
    method,
    properties,
    body
):

    try:

        data = json.loads(body)

        log_event(
            "inventory-service",
            "SYSTEM",
            "Inventory release received",
            data
        )

        time.sleep(1)

        log_event(
            "inventory-service",
            "SYSTEM",
            f"Stock released for order {data['order_id']}",
            {}
        )

        ch.basic_ack(
            delivery_tag=method.delivery_tag
        )

    except Exception as e:

        log_event(
            "inventory-service",
            "SYSTEM",
            "Release consumer error",
            {
                "error": str(e)
            },
            level="ERROR"
        )


def start_release_consumer():

    log_event(
        "inventory-service",
        "SYSTEM",
        "Inventory release consumer started",
        {}
    )

    while True:

        try:

            connection = get_connection()

            channel = connection.channel()

            channel.queue_declare(
                queue="inventory_release",
                durable=True
            )

            channel.basic_consume(
                queue="inventory_release",
                on_message_callback=callback,
                auto_ack=False
            )

            log_event(
                "inventory-service",
                "SYSTEM",
                "Waiting for inventory_release",
                {}
            )

            channel.start_consuming()

        except Exception as e:

            log_event(
                "inventory-service",
                "SYSTEM",
                "Release consumer crash",
                {
                    "error": str(e)
                },
                level="ERROR"
            )

            time.sleep(5)