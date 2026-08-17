from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int
    price: float


class OrderCreate(BaseModel):
    user_id: str
    items: List[OrderItemCreate]
    total_amount: float


class OrderResponse(BaseModel):
    id: int
    user_id: str
    total_amount: float
    status: str

    payment_status: Optional[str] = "PENDING"

    saga_id: Optional[UUID] = None

    correlation_id: Optional[UUID] = None

    event_version: str = "v1"

    failure_reason: Optional[str] = None

    compensation_status: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True