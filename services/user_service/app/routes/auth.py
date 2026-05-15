from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..security import create_access_token, verify_password

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=schemas.TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):

    user = db.query(models.User).filter(models.User.email == form_data.username).first()

    if not user:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )

    valid_password = verify_password(form_data.password, user.hashed_password)

    if not valid_password:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )

    access_token = create_access_token(data={"sub": user.email, "user_id": user.id})

    return {"access_token": access_token, "token_type": "bearer"}
