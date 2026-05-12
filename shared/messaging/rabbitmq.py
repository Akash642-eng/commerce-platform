import pika

from shared.config.settings import settings


def get_rabbitmq_connection():

    credentials = pika.PlainCredentials(
        "guest",
        "guest"
    )

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=settings.RABBITMQ_HOST,
            port=settings.RABBITMQ_PORT,
            credentials=credentials,
            heartbeat=600,
            blocked_connection_timeout=300
        )
    )

    return connection