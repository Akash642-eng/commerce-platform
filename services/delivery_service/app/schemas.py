from pydantic import BaseModel

from datetime import datetime

from typing import Optional


class DeliveryAgentCreate(BaseModel):

    name: str

    phone: str

    vehicle_number: str


class DeliveryAgentResponse(
    DeliveryAgentCreate
):

    id: int

    is_active: bool

    created_at: datetime

    class Config:

        from_attributes = True


class DeliveryCreate(BaseModel):

    order_id: int

    delivery_agent_id: int


class DeliveryResponse(BaseModel):

    id: int

    order_id: int

    delivery_agent_id: int

    status: str

    assigned_at: Optional[datetime]

    delivered_at: Optional[datetime]

    class Config:

        from_attributes = True