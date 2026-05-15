from typing import List

from pydantic import BaseModel


class OrderItemCreate(BaseModel):

    product_id: int

    quantity: int

    price: float


class OrderCreate(BaseModel):

    user_id: str

    items: List[OrderItemCreate]

    total_amount: float
