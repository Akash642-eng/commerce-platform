from pydantic import BaseModel

class DeliveryAgentCreate(BaseModel):
    name: str
    phone: str
    vehicle_number: str


class DeliveryCreate(BaseModel):
    order_id: int
    delivery_agent_id: int