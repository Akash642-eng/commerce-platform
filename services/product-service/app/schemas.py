from pydantic import BaseModel
from pydantic import Field


# --------------------------------
# CATEGORY
# --------------------------------

class CategoryCreate(BaseModel):

    name: str = Field(min_length=2)

    description: str


class CategoryResponse(BaseModel):

    id: int

    name: str

    description: str

    class Config:
        from_attributes = True


# --------------------------------
# PRODUCT
# --------------------------------

class ProductCreate(BaseModel):

    name: str = Field(min_length=2)

    description: str

    price: float

    stock: int

    category_id: int


class ProductUpdate(BaseModel):

    name: str

    description: str

    price: float

    stock: int

    category_id: int

    is_active: bool


class ProductResponse(BaseModel):

    id: int

    name: str

    description: str

    price: float

    stock: int

    is_active: bool

    category_id: int

    class Config:
        from_attributes = True