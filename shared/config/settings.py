import os

from dotenv import load_dotenv

load_dotenv()


class Settings:

    # ENVIRONMENT
    ENV = os.getenv("ENV", "dev")

    # DATABASE
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://commerce:commerce@postgres.database.svc.cluster.local:5432/commerce_db",
    )

    # REDIS
    REDIS_HOST = os.getenv("REDIS_HOST", "redis.cache.svc.cluster.local")

    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

    # RABBITMQ

    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq.messaging.svc.cluster.local")

    RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))

    # JWT
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")

    ALGORITHM = os.getenv("ALGORITHM", "HS256")

    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))


settings = Settings()
