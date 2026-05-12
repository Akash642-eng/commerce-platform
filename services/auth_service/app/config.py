import os


class Settings:

    SECRET_KEY: str = os.getenv(
        "SECRET_KEY",
        "mysecretkey"
    )

    ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_HOURS: int = 2


settings = Settings()