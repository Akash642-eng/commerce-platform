from sqlalchemy import TIMESTAMP, Column, Integer, String
from sqlalchemy.sql import func

from .database import Base


class Inventory(Base):

    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)

    product_id = Column(Integer, nullable=False)

    quantity = Column(Integer, nullable=False)

    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


class StockMovement(Base):

    __tablename__ = "stock_movements"

    id = Column(Integer, primary_key=True, index=True)

    product_id = Column(Integer, nullable=False)

    change = Column(Integer, nullable=False)

    reason = Column(String, nullable=False)

    created_at = Column(TIMESTAMP, server_default=func.now())
