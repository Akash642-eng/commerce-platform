from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import TIMESTAMP

from sqlalchemy.sql import func

from .database import Base


class SupportTicket(Base):

    __tablename__ = "support_tickets"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        String,
        nullable=False
    )

    subject = Column(
        String,
        nullable=False
    )

    description = Column(
        String,
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


class SupportMessage(Base):

    __tablename__ = "support_messages"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    ticket_id = Column(
        Integer,
        nullable=False
    )

    sender_id = Column(
        String,
        nullable=False
    )

    message = Column(
        String,
        nullable=False
    )

    created_at = Column(
        TIMESTAMP,
        server_default=func.now()
    )