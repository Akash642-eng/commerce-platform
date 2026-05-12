import pika
import json
import os
import uuid

from .logger import log_event


RABBITMQ_HOST = os.getenv(
    "RABBITMQ_HOST",
    "rabbitmq"
)


def publish_event(
    queue,
    data,
    trace_id=None
):

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=RABBITMQ_HOST
        )
    )

    channel = connection.channel()

    channel.queue_declare(
        queue=queue,
        durable=True
    )

    trace_id = trace_id or str(uuid.uuid4())

    channel.basic_publish(
        exchange='',
        routing_key=queue,
        body=json.dumps(data),
        properties=pika.BasicProperties(
            delivery_mode=2,
            headers={
                "x-trace-id": trace_id
            }
        )
    )

    log_event(
        service="order-service",
        event="event_published",
        trace_id=trace_id,
        message=f"Published {queue}",
        data=data
    )

    connection.close()