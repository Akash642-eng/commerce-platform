from pydantic import BaseModel

class PaymentCreate(BaseModel):
    order_id: int
    payment_method: str
    amount: float


class TransactionCreate(BaseModel):
    payment_id: int
    gateway: str
    gateway_response: str