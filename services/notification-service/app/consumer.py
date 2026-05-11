import json

from .rabbitmq import get_rabbitmq_connection

def callback(ch, method, properties, body):

    data = json.loads(body)

    print("Received event:")
    print(data)

def start_consumer():

    connection = get_rabbitmq_connection()

    channel = connection.channel()

    channel.queue_declare(queue="notifications")

    channel.basic_consume(
        queue="notifications",
        on_message_callback=callback,
        auto_ack=True
    )

    print("Waiting for messages...")

    channel.start_consuming()