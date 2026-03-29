from sqlalchemy import Column, Integer, String, DECIMAL, TIMESTAMP
from sqlalchemy.sql import func
from .database import Base

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer)
    payment_method = Column(String)
    payment_status = Column(String)
    amount = Column(DECIMAL)
    transaction_id = Column(String)
    created_at = Column(TIMESTAMP, server_default=func.now())


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(Integer)
    gateway = Column(String)
    gateway_response = Column(String)
    created_at = Column(TIMESTAMP, server_default=func.now())