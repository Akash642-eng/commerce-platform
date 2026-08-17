import json
import time
from datetime import datetime

import pika
import pybreaker
import redis

from shared.config.settings import settings
from shared.metrics.metrics import (
    DLQ_COUNT,
    EVENTS_FAILED,
    EVENTS_PROCESSED,
    RETRY_COUNT,
    RABBITMQ_CONSUMED,
    RABBITMQ_DLQ,
    RABBITMQ_FAILED,
    RABBITMQ_RETRY,
)
from shared.resilience import payment_breaker
from shared.resilience import retry_policy
from shared.resilience.exceptions import PaymentServiceException

from .database import SessionLocal
from .logger import log_event
from .models import Order, OrderStatusHistory
from .state_machine import can_transition

ENV = settings.ENV
RABBITMQ_HOST = settings.RABBITMQ_HOST
REDIS_HOST = settings.REDIS_HOST

MAX_RETRIES = 3

PAYMENT_QUEUE = "payment_completed"
PAYMENT_DLQ = "payment_completed_dlq"

INVENTORY_QUEUE = "inventory_reserved"
INVENTORY_DLQ = "inventory_reserved_dlq"

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=6379,
    decode_responses=True,
)


def publish_to_queue(channel, queue_name, message, headers=None):
    channel.basic_publish(
        exchange="",
        routing_key=queue_name,
        body=json.dumps(message),
        properties=pika.BasicProperties(
            delivery_mode=2,
            headers=headers or {},
        ),
    )


def add_history(db, order_id, status):
    history = OrderStatusHistory(order_id=order_id, status=status)
    db.add(history)
    db.commit()


def get_trace(headers):
    return headers.get("x-trace-id", "unknown")


def get_saga(headers):
    return headers.get("x-saga-id", "unknown")


def get_version(data):
    return data.get("version", "v1")


@payment_breaker
@retry_policy
def process_event(db, order, status, trace_id, saga_id):
    old_status = order.status

    if status == "RESERVED":
        if not can_transition(order.status, "RESERVED"):
            raise PaymentServiceException(f"Invalid transition {order.status} -> RESERVED")

        order.status = "RESERVED"
        db.commit()
        add_history(db, order.id, "RESERVED")
        
        EVENTS_PROCESSED.labels("order-service", "inventory_reserved").inc()

        log_event(
            "order-service",
            trace_id,
            "Inventory reserved",
            {
                "order_id": order.id,
                "from": old_status,
                "to": "RESERVED",
                "saga_id": saga_id,
            },
        )
        return

    if status == "SUCCESS":
        if can_transition(order.status, "PAID"):
            order.status = "PAID"
            db.commit()
            add_history(db, order.id, "PAID")
            
            EVENTS_PROCESSED.labels("order-service", "payment_completed").inc()

            log_event(
                "order-service",
                trace_id,
                "Payment completed",
                {
                    "order_id": order.id,
                    "from": old_status,
                    "to": "PAID",
                    "saga_id": saga_id,
                },
            )
            return

        if order.status == "CREATED":
            log_event(
                "order-service",
                trace_id,
                "Out-of-order event detected",
                {
                    "order_id": order.id,
                    "saga_id": saga_id,
                },
                level="WARNING",
            )

            order.status = "RESERVED"
            db.commit()
            add_history(db, order.id, "RESERVED")

            order.status = "PAID"
            db.commit()
            add_history(db, order.id, "PAID")
            
            EVENTS_PROCESSED.labels("order-service", "forced_paid_transition").inc()

            log_event(
                "order-service",
                trace_id,
                "Forced state transition completed",
                {
                    "order_id": order.id,
                    "saga_id": saga_id,
                },
            )
            return

        raise PaymentServiceException(f"Invalid transition {order.status} -> PAID")

    raise PaymentServiceException(f"Unknown payment status {status}")


def callback(ch, method, properties, body):
    db = SessionLocal()
    trace_id = "unknown"
    saga_id = "unknown"

    try:
        data = json.loads(body)
        headers = properties.headers or {}
        trace_id = get_trace(headers)
        saga_id = get_saga(headers)
        retry_count = headers.get("x-retry", 0)
        version = get_version(data)

        if version != "v1":
            raise PaymentServiceException(f"Unsupported event version: {version}")

        RABBITMQ_CONSUMED.labels(service="order-service", queue=method.routing_key).inc()

        log_event(
            "order-service",
            trace_id,
            "Event received",
            {
                "event": data,
                "retry": retry_count,
                "saga_id": saga_id,
                "version": version,
            },
        )

        order = db.query(Order).filter(Order.id == data["order_id"]).first()

        if not order:
            EVENTS_FAILED.labels("order-service", "order_not_found").inc()
            log_event(
                "order-service",
                trace_id,
                "Order not found",
                data,
                level="WARNING",
            )
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        status = data.get("status")
        event_key = f"{order.id}:{status}"

        if redis_client.get(event_key):
            EVENTS_FAILED.labels("order-service", "duplicate_event").inc()
            log_event(
                "order-service",
                trace_id,
                "Duplicate event ignored",
                {
                    "event": event_key,
                    "saga_id": saga_id,
                },
                level="WARNING",
            )
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        redis_client.set(event_key, "1", ex=3600)

        process_event(
            db=db,
            order=order,
            status=status,
            trace_id=trace_id,
            saga_id=saga_id,
        )

        ch.basic_ack(delivery_tag=method.delivery_tag)

    except pybreaker.CircuitBreakerError:
        EVENTS_FAILED.labels("order-service", "circuit_open").inc()
        log_event(
            "order-service",
            trace_id,
            "Circuit breaker OPEN",
            {"saga_id": saga_id},
            level="ERROR",
        )
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        EVENTS_FAILED.labels("order-service", "processing_failed").inc()
        RABBITMQ_FAILED.labels(service="order-service", queue=method.routing_key).inc()

        log_event(
            "order-service",
            trace_id,
            "Consumer failed",
            {
                "error": str(e),
                "saga_id": saga_id,
            },
            level="ERROR",
        )

        headers = properties.headers or {}
        retry_count = headers.get("x-retry", 0)

        if retry_count < MAX_RETRIES:
            RETRY_COUNT.labels("order-service", "consumer_retry").inc()
            RABBITMQ_RETRY.labels(service="order-service", queue=method.routing_key).inc()

            retry_headers = headers.copy()
            retry_headers["x-retry"] = retry_count + 1
            retry_headers["x-trace-id"] = trace_id
            retry_headers["x-saga-id"] = saga_id

            publish_to_queue(
                ch,
                method.routing_key,
                json.loads(body),
                retry_headers,
            )
        else:
            EVENTS_FAILED.labels("order-service", "dlq_sent").inc()
            DLQ_COUNT.labels("order-service", "consumer_dlq").inc()
            RABBITMQ_DLQ.labels(service="order-service", queue=f"{method.routing_key}_dlq").inc()

            publish_to_queue(
                ch,
                f"{method.routing_key}_dlq",
                json.loads(body),
                headers,
            )

        ch.basic_ack(delivery_tag=method.delivery_tag)

    finally:
        db.close()


def start_payment_consumer():
    log_event("order-service", "SYSTEM", f"Payment consumer started ({ENV})")

    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=RABBITMQ_HOST,
                    heartbeat=600,
                    blocked_connection_timeout=300,
                )
            )
            channel = connection.channel()

            channel.queue_declare(queue=PAYMENT_QUEUE, durable=True)
            channel.queue_declare(queue=PAYMENT_DLQ, durable=True)
            channel.basic_qos(prefetch_count=1)

            channel.basic_consume(
                queue=PAYMENT_QUEUE,
                on_message_callback=callback,
                auto_ack=False,
            )

            log_event("order-service", "SYSTEM", "Waiting for payment events")
            channel.start_consuming()

        except Exception as e:
            log_event(
                "order-service",
                "SYSTEM",
                "Payment consumer crashed",
                {"error": str(e)},
                level="ERROR",
            )
            time.sleep(5)


def start_inventory_consumer():
    log_event("order-service", "SYSTEM", f"Inventory consumer started ({ENV})")

    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=RABBITMQ_HOST,
                    heartbeat=600,
                    blocked_connection_timeout=300,
                )
            )
            channel = connection.channel()

            channel.queue_declare(queue=INVENTORY_QUEUE, durable=True)
            channel.queue_declare(queue=INVENTORY_DLQ, durable=True)
            channel.basic_qos(prefetch_count=1)

            channel.basic_consume(
                queue=INVENTORY_QUEUE,
                on_message_callback=callback,
                auto_ack=False,
            )

            log_event("order-service", "SYSTEM", "Waiting for inventory events")
            channel.start_consuming()

        except Exception as e:
            log_event(
                "order-service",
                "SYSTEM",
                "Inventory consumer crashed",
                {"error": str(e)},
                level="ERROR",
            )
            time.sleep(5)