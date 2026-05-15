from sqlalchemy import TIMESTAMP, Boolean, Column, Integer, String
from sqlalchemy.sql import func

from .database import Base


class Notification(Base):

    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(String, nullable=False)

    message = Column(String, nullable=False)

    type = Column(String, nullable=False)

    is_read = Column(Boolean, default=False)

    created_at = Column(TIMESTAMP, server_default=func.now())
