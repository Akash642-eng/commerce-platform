from typing import Optional

from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import Field


class UserBase(BaseModel):

    name: str = Field(
        min_length=2,
        max_length=100
    )

    email: EmailStr


class UserCreate(UserBase):

    password: str = Field(
        min_length=8,
        max_length=128
    )


class UserUpdate(BaseModel):

    name: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=100
    )

    email: Optional[EmailStr] = None

    password: Optional[str] = Field(
        default=None,
        min_length=8,
        max_length=128
    )


class UserLogin(BaseModel):

    email: EmailStr

    password: str


class UserResponse(UserBase):

    id: int

    is_active: bool

    is_admin: bool

    class Config:

        from_attributes = True


class TokenResponse(BaseModel):

    access_token: str

    token_type: str = "bearer"


class HealthResponse(BaseModel):

    status: str