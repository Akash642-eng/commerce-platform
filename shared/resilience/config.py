import os

HTTP_TIMEOUT = int(os.getenv("HTTP_TIMEOUT", 5))

DB_TIMEOUT = int(os.getenv("DB_TIMEOUT", 10))

RABBITMQ_TIMEOUT = int(os.getenv("RABBITMQ_TIMEOUT", 5))

EXTERNAL_API_TIMEOUT = int(os.getenv("EXTERNAL_API_TIMEOUT", 10))