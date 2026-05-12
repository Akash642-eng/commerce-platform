import json

from .rabbitmq import get_rabbitmq_connection

from .logger import log_event

from .metrics import notifications_sent


def callback(
    ch,
    method,
    properties,
    body
):

    data = json.loads(body)

    notifications_sent.inc()

    log_event(
        service="notification-service",
        event="notification_received",
        trace_id="consumer",
        message="Notification received",
        data=data
    )


def start_consumer():

    connection = get_rabbitmq_connection()

    channel = connection.channel()

    channel.queue_declare(
        queue="notifications"
    )

    channel.basic_consume(
        queue="notifications",
        on_message_callback=callback,
        auto_ack=True
    )

    log_event(
        service="notification-service",
        event="consumer_started",
        trace_id="consumer",
        message="Waiting for messages..."
    )

    channel.start_consuming()