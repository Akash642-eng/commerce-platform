import os


class Settings:
    def __init__(self):
        # ENV
        self.ENV = os.getenv("ENV", "dev")

        # DATABASE
        self.DATABASE_URL = os.getenv(
            "DATABASE_URL",
            "postgresql://commerce:commerce@postgres:5432/commerce_db"
        )

        # RABBITMQ
        self.RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")

        # REDIS
        self.REDIS_HOST = os.getenv("REDIS_HOST", "redis")

        # JWT (for future use)
        self.JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret")


# single instance (important)
settings = Settings()