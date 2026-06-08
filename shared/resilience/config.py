import os

HTTP_TIMEOUT = int(
    os.getenv("HTTP_TIMEOUT", "5")
)

DB_TIMEOUT = int(
    os.getenv("DB_TIMEOUT", "10")
)

RABBITMQ_TIMEOUT = int(
    os.getenv("RABBITMQ_TIMEOUT", "5")
)

EXTERNAL_API_TIMEOUT = int(
    os.getenv("EXTERNAL_API_TIMEOUT", "10")
)

CIRCUIT_BREAKER_FAILURE_THRESHOLD = int(
    os.getenv("CB_FAILURE_THRESHOLD", "5")
)

CIRCUIT_BREAKER_RESET_TIMEOUT = int(
    os.getenv("CB_RESET_TIMEOUT", "60")
)

RETRY_ATTEMPTS = int(
    os.getenv("RETRY_ATTEMPTS", "3")
)

RETRY_BACKOFF_SECONDS = int(
    os.getenv("RETRY_BACKOFF_SECONDS", "2")
)