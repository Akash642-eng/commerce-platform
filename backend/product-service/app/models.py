from sqlalchemy import Column, Integer, String, Text, DECIMAL, ForeignKey
from .database import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    description = Column(Text)


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200))
    description = Column(Text)
    price = Column(DECIMAL)
    category_id = Column(Integer, ForeignKey("categories.id"))