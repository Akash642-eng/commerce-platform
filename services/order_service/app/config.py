import os


class Settings:

    def __init__(self):

        self.ENV = os.getenv(
            "ENV",
            "dev"
        )

        self.DATABASE_URL = os.getenv(
            "DATABASE_URL",
            "postgresql://commerce:commerce@postgres:5432/commerce_db"
        )

        self.RABBITMQ_HOST = os.getenv(
            "RABBITMQ_HOST",
            "rabbitmq"
        )

        self.REDIS_HOST = os.getenv(
            "REDIS_HOST",
            "redis"
        )

        self.JWT_SECRET = os.getenv(
            "JWT_SECRET",
            "dev-secret"
        )


settings = Settings()