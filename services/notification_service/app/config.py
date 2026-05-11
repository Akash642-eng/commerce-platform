import os

DATABASE_URL = os.getenv("DATABASE_URL")

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")

rabbitmq_port = os.getenv("RABBITMQ_PORT", "5672")

# Fix Kubernetes injected tcp:// issue
if "://" in rabbitmq_port:
    rabbitmq_port = rabbitmq_port.split(":")[-1]

RABBITMQ_PORT = int(rabbitmq_port)

RABBITMQ_QUEUE = os.getenv(
    "RABBITMQ_QUEUE",
    "notifications"
)

