from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.sql import func
from .database import Base

class SupportTicket(Base):
    __tablename__ = "support_tickets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String)
    subject = Column(String)
    description = Column(String)
    status = Column(String)
    created_at = Column(TIMESTAMP, server_default=func.now())


class SupportMessage(Base):
    __tablename__ = "support_messages"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer)
    sender_id = Column(String)
    message = Column(String)
    created_at = Column(TIMESTAMP, server_default=func.now())