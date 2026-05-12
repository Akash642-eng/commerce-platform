import os

DATABASE_URL = os.getenv(
    "DATABASE_URL"
)

RABBITMQ_HOST = os.getenv(
    "RABBITMQ_HOST",
    "rabbitmq"
)

RABBITMQ_PORT = int(
    os.getenv(
        "RABBITMQ_PORT",
        5672
    )
)

RABBITMQ_QUEUE = os.getenv(
    "RABBITMQ_QUEUE",
    "notifications"
)