from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DECIMAL
from sqlalchemy import TIMESTAMP

from sqlalchemy.sql import func

from .database import Base


class Payment(Base):

    __tablename__ = "payments"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    order_id = Column(
        Integer,
        nullable=False
    )

    payment_method = Column(
        String,
        nullable=False
    )

    payment_status = Column(
        String,
        nullable=False
    )

    amount = Column(
        DECIMAL,
        nullable=False
    )

    transaction_id = Column(
        String,
        nullable=False
    )

    created_at = Column(
        TIMESTAMP,
        server_default=func.now()
    )


class Transaction(Base):

    __tablename__ = "transactions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    payment_id = Column(
        Integer,
        nullable=False
    )

    gateway = Column(
        String,
        nullable=False
    )

    gateway_response = Column(
        String,
        nullable=False
    )

    created_at = Column(
        TIMESTAMP,
        server_default=func.now()
    )