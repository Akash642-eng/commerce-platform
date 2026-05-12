from pydantic import BaseModel
from pydantic import Field

from typing import List

from datetime import datetime


class CartItemCreate(BaseModel):

    product_id: int

    quantity: int = Field(gt=0)


class CartItemResponse(BaseModel):

    id: int

    product_id: int

    quantity: int

    class Config:

        from_attributes = True


class CartCreate(BaseModel):

    user_id: int


class CartResponse(BaseModel):

    id: int

    user_id: int

    created_at: datetime

    items: List[CartItemResponse] = []

    class Config:

        from_attributes = True