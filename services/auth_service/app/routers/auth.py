from fastapi import APIRouter, Depends, HTTPException

from ..schemas.user import UserLogin
from ..utils.jwt import create_token
from ..utils.security import verify_token

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login")
def login(user: UserLogin):

    if not user.email or not user.password:

        raise HTTPException(status_code=400, detail="Missing credentials")

    token = create_token(user.email)

    return {"access_token": token, "token_type": "bearer"}


@router.get("/me")
def me(user=Depends(verify_token)):

    return {"user": user}
