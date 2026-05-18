from datetime import datetime
from datetime import timedelta

import jwt

from ..config import settings


SECRET_KEY = settings.SECRET_KEY

ALGORITHM = settings.ALGORITHM


def create_token(
    user_id: str
):

    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow()
        + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        ),
    }

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    return token


def decode_token(
    token: str
):

    payload = jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM],
    )

    return payload