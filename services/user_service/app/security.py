from datetime import datetime, timedelta

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from shared.config.settings import settings

from . import models
from .database import get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


SECRET_KEY = settings.SECRET_KEY

ALGORITHM = settings.ALGORITHM

ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


def hash_password(password: str):

    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):

    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict):

    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def verify_token(token: str):

    try:

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        user_id = payload.get("user_id")

        if user_id is None:

            return None

        return user_id

    except JWTError:

        return None


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):

    user_id = verify_token(token)

    if not user_id:

        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:

        raise HTTPException(status_code=401, detail="User not found")

    return user
