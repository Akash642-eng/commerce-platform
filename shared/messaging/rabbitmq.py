import pika

from shared.config.settings import settings
from shared.resilience.config import RABBITMQ_TIMEOUT


def get_rabbitmq_connection():

    credentials = pika.PlainCredentials("guest", "guest")

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=settings.RABBITMQ_HOST,
            port=settings.RABBITMQ_PORT,
            credentials=credentials,

            heartbeat=600,
            
            socket_timeout=RABBITMQ_TIMEOUT,

            blocked_connection_timeout=RABBITMQ_TIMEOUT,
            connection_attempts=3,
            retry_delay=2,
        )
    )

    return connection
