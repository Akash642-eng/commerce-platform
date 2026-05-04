import pika
import json
import os
import time

from .logger import log_event

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
DLQ = "payment_dlq"


def callback(ch, method, properties, body):
    try:
        data = json.loads(body)

        trace_id = (
            properties.headers.get("x-trace-id")
            if properties and properties.headers
            else "N/A"
        )

        log_event(
            "payment-service",
            trace_id,
            "💀 MESSAGE IN DLQ",
            data,
            level="ERROR"
        )

        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        log_event(
            "payment-service",
            "SYSTEM",
            "DLQ processing error",
            {"error": str(e)},
            level="ERROR"
        )


def start_dlq_consumer():
    log_event("payment-service", "SYSTEM", "DLQ consumer started")

    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=RABBITMQ_HOST)
            )

            channel = connection.channel()
            channel.queue_declare(queue=DLQ, durable=True)

            channel.basic_consume(
                queue=DLQ,
                on_message_callback=callback,
                auto_ack=False
            )

            log_event("payment-service", "SYSTEM", "Waiting for DLQ messages")

            channel.start_consuming()

        except Exception as e:
            log_event(
                "payment-service",
                "SYSTEM",
                "DLQ consumer retry",
                {"error": str(e)},
                level="ERROR"
            )
            time.sleep(5)