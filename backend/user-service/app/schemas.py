from pydantic import BaseModel
from uuid import UUID


class UserCreate(BaseModel):
    name: str
    email: str
    phone: str


class AddressCreate(BaseModel):
    user_id: UUID
    address_line1: str
    address_line2: str
    city: str
    state: str
    postal_code: str
    country: str