import json
import time

import pika

from shared.config.settings import settings
from shared.metrics.metrics import (
    DLQ_COUNT,
    RABBITMQ_CONSUMED,
    RABBITMQ_DLQ,
)
from shared.metrics.metrics_server import start_metrics_server

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

        RABBITMQ_CONSUMED.labels(
            service="payment-service",
            queue=DLQ,
        ).inc()

        RABBITMQ_DLQ.labels(
            service="payment-service",
            queue=DLQ,
        ).inc()

        DLQ_COUNT.labels(
            service="payment-service",
            event="payment_dlq_message",
        ).inc()

        log_event(
            service="payment-service",
            event="dlq_message",
            trace_id=trace_id,
            message="Message received in DLQ",
            data=data,
            level="ERROR",
        )

        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:

        log_event(
            service="payment-service",
            event="dlq_processing_failed",
            trace_id="SYSTEM",
            message="DLQ consumer failed",
            data={"error": str(e)},
            level="ERROR",
        )


def start_dlq_consumer():

    start_metrics_server(8012)

    log_event(
        service="payment-service",
        event="dlq_consumer_started",
        trace_id="SYSTEM",
        message="DLQ consumer started with metrics on port 8012",
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
                queue=DLQ,
                durable=True,
            )

            channel.basic_consume(
                queue=DLQ,
                on_message_callback=callback,
                auto_ack=False,
            )

            log_event(
                service="payment-service",
                event="dlq_waiting",
                trace_id="SYSTEM",
                message="Waiting for DLQ messages",
            )

            channel.start_consuming()

        except Exception as e:

            log_event(
                service="payment-service",
                event="dlq_consumer_crashed",
                trace_id="SYSTEM",
                message="DLQ consumer crashed",
                data={"error": str(e)},
                level="ERROR",
            )

            time.sleep(5)