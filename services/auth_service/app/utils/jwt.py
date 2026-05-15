from datetime import datetime, timedelta

import jwt

from ..config import settings

SECRET_KEY = settings.SECRET_KEY

ALGORITHM = settings.ALGORITHM


def create_token(user_id: str):

    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS),
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str):

    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
