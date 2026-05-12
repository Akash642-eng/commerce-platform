import json

import pika

from shared.logging.logger import log_event

from shared.messaging.rabbitmq import (
    get_rabbitmq_connection
)


def publish_event(
    queue: str,
    message: dict,
    service: str,
    trace_id: str = "unknown"
):

    connection = get_rabbitmq_connection()

    channel = connection.channel()

    channel.queue_declare(
        queue=queue,
        durable=True
    )

    channel.basic_publish(
        exchange="",
        routing_key=queue,
        body=json.dumps(message),
        properties=pika.BasicProperties(
            delivery_mode=2,
            headers={
                "x-trace-id": trace_id
            }
        )
    )

    log_event(
        service=service,
        event="event_published",
        trace_id=trace_id,
        message=f"Published to {queue}",
        data=message
    )

    connection.close()