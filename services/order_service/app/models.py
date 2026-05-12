from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DECIMAL
from sqlalchemy import TIMESTAMP

from sqlalchemy.sql import func

from .database import Base


class Order(Base):

    __tablename__ = "orders"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        String,
        nullable=False
    )

    total_amount = Column(
        DECIMAL,
        nullable=False
    )

    status = Column(
        String,
        nullable=False
    )

    created_at = Column(
        TIMESTAMP,
        server_default=func.now()
    )


class OrderItem(Base):

    __tablename__ = "order_items"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    order_id = Column(
        Integer,
        nullable=False
    )

    product_id = Column(
        Integer,
        nullable=False
    )

    quantity = Column(
        Integer,
        nullable=False
    )

    price = Column(
        DECIMAL,
        nullable=False
    )


class OrderStatusHistory(Base):

    __tablename__ = "order_status_history"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    order_id = Column(
        Integer,
        nullable=False
    )

    status = Column(
        String,
        nullable=False
    )

    changed_at = Column(
        TIMESTAMP,
        server_default=func.now()
    )