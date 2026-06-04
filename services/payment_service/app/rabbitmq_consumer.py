import json
import random
import time

import pika
import pybreaker
import redis as redis_lib

from shared.config.settings import settings
from shared.metrics.metrics import (
    DLQ_COUNT,
    EVENTS_FAILED,
    EVENTS_PROCESSED,
    PAYMENT_FAILURE,
    PAYMENT_SUCCESS,
    RABBITMQ_CONSUMED,
    RABBITMQ_DLQ,
    RABBITMQ_FAILED,
    RABBITMQ_PUBLISHED,
    RABBITMQ_RETRY,
    RETRY_COUNT,
)
from shared.metrics.metrics_server import start_metrics_server
from shared.resilience import payment_breaker
from shared.resilience.exceptions import PaymentServiceException
from shared.resilience.retry import retry_policy

from .logger import log_event


ENV = settings.ENV

RABBITMQ_HOST = settings.RABBITMQ_HOST

REDIS_HOST = settings.REDIS_HOST


redis_client = redis_lib.Redis(
    host=REDIS_HOST,
    port=6379,
    decode_responses=True,
)


MAX_RETRIES = 3

MAIN_QUEUE = "inventory_reserved_payment"
RETRY_QUEUE = "payment_retry"
DLQ = "payment_dlq"


def get_connection():

    return pika.BlockingConnection(
        pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            heartbeat=600,
            blocked_connection_timeout=300,
        )
    )


def setup_queues(channel):

    channel.queue_declare(
        queue=MAIN_QUEUE,
        durable=True,
    )

    channel.queue_declare(
        queue=RETRY_QUEUE,
        durable=True,
        arguments={
            "x-message-ttl": 5000,
            "x-dead-letter-exchange": "",
            "x-dead-letter-routing-key": MAIN_QUEUE,
        },
    )

    channel.queue_declare(
        queue=DLQ,
        durable=True,
    )

    channel.queue_declare(
        queue="payment_completed",
        durable=True,
    )

    channel.queue_declare(
        queue="payment_failed",
        durable=True,
    )


def publish(queue, message, trace_id, headers=None):

    connection = get_connection()

    channel = connection.channel()

    final_headers = headers.copy() if headers else {}

    final_headers["x-trace-id"] = trace_id

    RABBITMQ_PUBLISHED.labels(
        service="payment-service",
        queue=queue,
    ).inc()

    channel.basic_publish(
        exchange="",
        routing_key=queue,
        body=json.dumps(message),
        properties=pika.BasicProperties(
            delivery_mode=2,
            headers=final_headers,
        ),
    )

    connection.close()


def publish_payment_event(data, trace_id):

    is_success = random.choice([True, False])

    if is_success:

        event = {
            "version": "v1",
            "order_id": data["order_id"],
            "status": "SUCCESS",
        }

        queue = "payment_completed"

    else:

        event = {
            "version": "v1",
            "order_id": data["order_id"],
            "status": "FAILED",
        }

        queue = "payment_failed"

    publish(queue, event, trace_id)

    log_event(
        "payment-service",
        trace_id,
        f"Sent {queue}",
        event,
    )


@payment_breaker
@retry_policy
def process_payment(data):

    if data["order_id"] % 5 == 0:

        raise PaymentServiceException(
            "Simulated payment failure"
        )

    time.sleep(
        1 if ENV == "dev"
        else 0.5
    )

    return True


def callback(ch, method, properties, body):

    trace_id = "unknown"

    try:

        data = json.loads(body)

        headers = properties.headers or {}

        trace_id = headers.get(
            "x-trace-id",
            "unknown",
        )

        retry_count = headers.get(
            "x-retry",
            0,
        )

        RABBITMQ_CONSUMED.labels(
            service="payment-service",
            queue=MAIN_QUEUE,
        ).inc()

        event_id = f"payment:{data['order_id']}"

        if redis_client.get(event_id):

            EVENTS_FAILED.labels(
                service="payment-service",
                event="duplicate_event",
            ).inc()

            log_event(
                "payment-service",
                trace_id,
                "Duplicate payment event skipped",
                data,
            )

            ch.basic_ack(
                delivery_tag=method.delivery_tag
            )

            return

        log_event(
            "payment-service",
            trace_id,
            f"Processing payment retry={retry_count}",
            data,
        )

        process_payment(data)

        redis_client.set(
            event_id,
            "1",
            ex=3600,
        )

        publish_payment_event(
            data,
            trace_id,
        )

        PAYMENT_SUCCESS.labels(
            service="payment-service",
        ).inc()

        EVENTS_PROCESSED.labels(
            service="payment-service",
            event="payment_success",
        ).inc()

        log_event(
            "payment-service",
            trace_id,
            "Payment processed successfully",
            data,
        )

        ch.basic_ack(
            delivery_tag=method.delivery_tag
        )

    except pybreaker.CircuitBreakerError:

        EVENTS_FAILED.labels(
            service="payment-service",
            event="circuit_open",
        ).inc()

        log_event(
            "payment-service",
            trace_id,
            "Circuit breaker OPEN",
            {},
            level="ERROR",
        )

        ch.basic_ack(
            delivery_tag=method.delivery_tag
        )

    except Exception as e:

        PAYMENT_FAILURE.labels(
            service="payment-service",
        ).inc()

        EVENTS_FAILED.labels(
            service="payment-service",
            event="payment_failed",
        ).inc()

        RABBITMQ_FAILED.labels(
            service="payment-service",
            queue=MAIN_QUEUE,
        ).inc()

        log_event(
            "payment-service",
            trace_id,
            "Payment processing failed",
            {"error": str(e)},
            level="ERROR",
        )

        headers = properties.headers or {}

        retry_count = headers.get(
            "x-retry",
            0,
        )

        if retry_count < MAX_RETRIES:

            RETRY_COUNT.labels(
                service="payment-service",
                event="payment_retry",
            ).inc()

            RABBITMQ_RETRY.labels(
                service="payment-service",
                queue=RETRY_QUEUE,
            ).inc()

            new_headers = headers.copy()

            new_headers["x-retry"] = (
                retry_count + 1
            )

            new_headers["x-trace-id"] = trace_id

            publish(
                RETRY_QUEUE,
                json.loads(body),
                trace_id,
                headers=new_headers,
            )

        else:

            DLQ_COUNT.labels(
                service="payment-service",
                event="payment_dlq",
            ).inc()

            RABBITMQ_DLQ.labels(
                service="payment-service",
                queue=DLQ,
            ).inc()

            publish(
                DLQ,
                json.loads(body),
                trace_id,
                headers=headers,
            )

        ch.basic_ack(
            delivery_tag=method.delivery_tag
        )


def start_consumer():

    start_metrics_server(8011)

    log_event(
        "payment-service",
        "SYSTEM",
        "Payment consumer started with Prometheus metrics on port 8011",
    )

    while True:

        try:

            connection = get_connection()

            channel = connection.channel()

            setup_queues(channel)

            channel.basic_qos(
                prefetch_count=1
            )

            channel.basic_consume(
                queue=MAIN_QUEUE,
                on_message_callback=callback,
                auto_ack=False,
            )

            log_event(
                "payment-service",
                "SYSTEM",
                "Waiting for payment events",
            )

            channel.start_consuming()

        except Exception as e:

            log_event(
                "payment-service",
                "SYSTEM",
                "Consumer crashed",
                {"error": str(e)},
                level="ERROR",
            )

            time.sleep(5)