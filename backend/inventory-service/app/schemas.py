from pydantic import BaseModel

class InventoryCreate(BaseModel):
    product_id: int
    quantity: int


class StockMovementCreate(BaseModel):
    product_id: int
    change: int
    reason: str