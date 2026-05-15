import pika

from .config import RABBITMQ_HOST, RABBITMQ_PORT


def get_rabbitmq_connection():

    credentials = pika.PlainCredentials("guest", "guest")

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=RABBITMQ_HOST, port=RABBITMQ_PORT, credentials=credentials
        )
    )

    return connection
