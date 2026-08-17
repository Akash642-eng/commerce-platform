import json
import uuid

import pika

from shared.config.settings import settings

from .logger import log_event

RABBITMQ_HOST = settings.RABBITMQ_HOST


def publish_event(
    queue,
    data,
    trace_id=None,
    saga_id=None,
    correlation_id=None,
    event_version="v1",
    headers=None,
):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=RABBITMQ_HOST
        )
    )

    channel = connection.channel()

    channel.queue_declare(
        queue=queue,
        durable=True,
    )

    trace_id = trace_id or str(uuid.uuid4())

    saga_id = saga_id or str(uuid.uuid4())

    correlation_id = correlation_id or trace_id

    final_headers = headers.copy() if headers else {}

    final_headers.update(
        {
            "x-trace-id": trace_id,
            "x-saga-id": saga_id,
            "x-correlation-id": correlation_id,
            "x-event-version": event_version,
        }
    )

    if "event_version" not in data:
        data["event_version"] = event_version

    if "trace_id" not in data:
        data["trace_id"] = trace_id

    if "saga_id" not in data:
        data["saga_id"] = saga_id

    if "correlation_id" not in data:
        data["correlation_id"] = correlation_id

    channel.basic_publish(
        exchange="",
        routing_key=queue,
        body=json.dumps(data),
        properties=pika.BasicProperties(
            delivery_mode=2,
            headers=final_headers,
        ),
    )

    log_event(
        service="order-service",
        event="event_published",
        trace_id=trace_id,
        message=f"Published {queue}",
        data={
            "queue": queue,
            "payload": data,
            "headers": final_headers,
        },
    )

    connection.close()