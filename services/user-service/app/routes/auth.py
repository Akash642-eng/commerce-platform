from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.orm import Session

from app.database import get_db

from app import models
from app import schemas

from app.security import create_access_token
from app.security import verify_password


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# --------------------------------
# LOGIN
# --------------------------------
@router.post(
    "/login",
    response_model=schemas.TokenResponse
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    # --------------------------------
    # FIND USER
    # --------------------------------
    user = db.query(
        models.User
    ).filter(
        models.User.email == form_data.username
    ).first()


    # --------------------------------
    # USER NOT FOUND
    # --------------------------------
    if not user:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )


    # --------------------------------
    # PASSWORD VALIDATION
    # --------------------------------
    valid_password = verify_password(
        form_data.password,
        user.hashed_password
    )

    if not valid_password:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )


    # --------------------------------
    # CREATE JWT TOKEN
    # --------------------------------
    access_token = create_access_token(
        data={
            "sub": user.email,
            "user_id": user.id
        }
    )


    # --------------------------------
    # RESPONSE
    # --------------------------------
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }