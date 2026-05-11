from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP
from sqlalchemy.sql import func

from .database import Base


class DeliveryAgent(Base):
    __tablename__ = "delivery_agents"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)

    phone = Column(String, nullable=False)

    vehicle_number = Column(String, nullable=False)

    is_active = Column(Boolean, default=True)

    created_at = Column(
        TIMESTAMP,
        server_default=func.now()
    )


class Delivery(Base):
    __tablename__ = "deliveries"

    id = Column(Integer, primary_key=True, index=True)

    order_id = Column(Integer, nullable=False)

    delivery_agent_id = Column(Integer, nullable=False)

    status = Column(String, nullable=False)

    assigned_at = Column(TIMESTAMP)

    delivered_at = Column(TIMESTAMP)