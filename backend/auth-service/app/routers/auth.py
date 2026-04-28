from fastapi import APIRouter
from ..utils.jwt import create_token
from ..utils.security import verify_token
from fastapi import Depends

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login")
def login(user_id: str):
    token = create_token(user_id)
    return {"access_token": token}


@router.get("/me")
def me(user=Depends(verify_token)):
    return {"user": user}