import json

from .rabbitmq import get_rabbitmq_connection

def publish_event(queue: str, message: dict):

    connection = get_rabbitmq_connection()

    channel = connection.channel()

    channel.queue_declare(queue=queue)

    channel.basic_publish(
        exchange="",
        routing_key=queue,
        body=json.dumps(message)
    )

    print(f"Published message to {queue}")

    connection.close()