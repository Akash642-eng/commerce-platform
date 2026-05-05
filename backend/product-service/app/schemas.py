from pydantic import BaseModel

#Category
class CategoryCreate(BaseModel):
    name: str
    description: str


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: str

    class Config:
        from_attributes = True


#Product
class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    category_id: int


class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    price: float
    category_id: int

    class Config:
        from_attributes = True