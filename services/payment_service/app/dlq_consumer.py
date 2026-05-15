import json
import time

import pika

from shared.config.settings import settings

from .logger import log_event

RABBITMQ_HOST = settings.RABBITMQ_HOST

DLQ = "payment_dlq"


def callback(ch, method, properties, body):

    try:

        data = json.loads(body)

        trace_id = (
            properties.headers.get("x-trace-id")
            if properties and properties.headers
            else "unknown"
        )

        log_event(
            service="payment-service",
            event="dlq_message",
            trace_id=trace_id,
            message="MESSAGE IN DLQ",
            data=data,
            level="ERROR",
        )

        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:

        log_event(
            service="payment-service",
            event="dlq_error",
            trace_id="system",
            message="DLQ processing error",
            data={"error": str(e)},
            level="ERROR",
        )


def start_dlq_consumer():

    log_event(
        service="payment-service",
        event="dlq_consumer_start",
        trace_id="system",
        message="DLQ consumer started",
    )

    while True:

        try:

            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=RABBITMQ_HOST)
            )

            channel = connection.channel()

            channel.queue_declare(queue=DLQ, durable=True)

            channel.basic_consume(
                queue=DLQ, on_message_callback=callback, auto_ack=False
            )

            log_event(
                service="payment-service",
                event="dlq_waiting",
                trace_id="system",
                message="Waiting for DLQ messages",
            )

            channel.start_consuming()

        except Exception as e:

            log_event(
                service="payment-service",
                event="dlq_retry",
                trace_id="system",
                message="DLQ consumer retry",
                data={"error": str(e)},
                level="ERROR",
            )

            time.sleep(5)
