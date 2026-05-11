from sqlalchemy import Column, Integer, ForeignKey, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from .database import Base


class Cart(Base):
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)

    created_at = Column(
        TIMESTAMP,
        server_default=func.now()
    )

    items = relationship(
        "CartItem",
        back_populates="cart",
        cascade="all, delete"
    )


class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)

    cart_id = Column(
        Integer,
        ForeignKey("carts.id"),
        nullable=False
    )

    product_id = Column(Integer, nullable=False)

    quantity = Column(
        Integer,
        nullable=False,
        default=1
    )

    cart = relationship(
        "Cart",
        back_populates="items"
    )