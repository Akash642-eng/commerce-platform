import json

from .logger import log_event
from .rabbitmq import get_rabbitmq_connection


def publish_event(queue: str, message: dict):

    connection = get_rabbitmq_connection()

    channel = connection.channel()

    channel.queue_declare(queue=queue)

    channel.basic_publish(exchange="", routing_key=queue, body=json.dumps(message))

    log_event(
        service="notification-service",
        event="notification_published",
        trace_id="producer",
        message=f"Published message to {queue}",
        data=message,
    )

    connection.close()
