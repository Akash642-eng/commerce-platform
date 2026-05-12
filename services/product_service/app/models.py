from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import DECIMAL
from sqlalchemy import ForeignKey
from sqlalchemy import Boolean

from .database import Base


class Category(Base):

    __tablename__ = "categories"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(100),
        nullable=False,
        unique=True
    )

    description = Column(Text)


class Product(Base):

    __tablename__ = "products"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(200),
        nullable=False,
        index=True
    )

    description = Column(Text)

    price = Column(
        DECIMAL,
        nullable=False
    )

    stock = Column(
        Integer,
        default=0
    )

    is_active = Column(
        Boolean,
        default=True
    )

    category_id = Column(
        Integer,
        ForeignKey("categories.id"),
        nullable=False
    )