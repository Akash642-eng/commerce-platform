from pydantic import BaseModel

class CartCreate(BaseModel):
    user_id: str


class CartItemCreate(BaseModel):
    cart_id: int
    product_id: int
    quantity: int