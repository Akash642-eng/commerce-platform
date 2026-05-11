from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import func

from .database import Base


class User(Base):

    __tablename__ = "users"


    # --------------------------------
    # PRIMARY KEY
    # --------------------------------
    id = Column(
        Integer,
        primary_key=True,
        index=True
    )


    # --------------------------------
    # USER DETAILS
    # --------------------------------
    name = Column(
        String(100),
        nullable=False
    )

    email = Column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )

    hashed_password = Column(
        String(255),
        nullable=False
    )


    # --------------------------------
    # USER STATUS
    # --------------------------------
    is_active = Column(
        Boolean,
        default=True
    )

    is_admin = Column(
        Boolean,
        default=False
    )


    # --------------------------------
    # TIMESTAMPS
    # --------------------------------
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )