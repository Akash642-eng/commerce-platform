from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.sql import func
from .database import Base

class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer)
    quantity = Column(Integer)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


class StockMovement(Base):
    __tablename__ = "stock_movements"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer)
    change = Column(Integer)
    reason = Column(String)
    created_at = Column(TIMESTAMP, server_default=func.now())