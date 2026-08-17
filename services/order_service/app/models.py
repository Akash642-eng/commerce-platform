from sqlalchemy import DECIMAL, TIMESTAMP, Column, Integer, String, Text
from sqlalchemy.sql import func

from .database import Base


class Order(Base):

    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(String, nullable=False)

    total_amount = Column(DECIMAL, nullable=False)

    status = Column(String, nullable=False)

    payment_status = Column(
        String,
        default="PENDING",
        nullable=False,
    )

    saga_id = Column(
        String(36),
        nullable=True,
        index=True,
    )

    correlation_id = Column(
        String(36),
        nullable=True,
        index=True,
    )

    event_version = Column(
        String(20),
        default="v1",
        nullable=False,
    )

    failure_reason = Column(
        Text,
        nullable=True,
    )

    compensation_status = Column(
        String(50),
        nullable=True,
    )

    created_at = Column(
        TIMESTAMP,
        server_default=func.now(),
    )

    updated_at = Column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now(),
    )


class OrderItem(Base):

    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)

    order_id = Column(Integer, nullable=False)

    product_id = Column(Integer, nullable=False)

    quantity = Column(Integer, nullable=False)

    price = Column(DECIMAL, nullable=False)


class OrderStatusHistory(Base):

    __tablename__ = "order_status_history"

    id = Column(Integer, primary_key=True, index=True)

    order_id = Column(Integer, nullable=False)

    status = Column(String, nullable=False)

    changed_at = Column(
        TIMESTAMP,
        server_default=func.now(),
    )