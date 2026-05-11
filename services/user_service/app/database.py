import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

from .logger import logger


DATABASE_URL = os.getenv("DATABASE_URL")


if not DATABASE_URL:

    raise ValueError("DATABASE_URL environment variable is missing")


# --------------------------------
# DATABASE ENGINE
# --------------------------------
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    future=True
)


# --------------------------------
# SESSION FACTORY
# --------------------------------
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# --------------------------------
# BASE MODEL
# --------------------------------
Base = declarative_base()


# --------------------------------
# DATABASE DEPENDENCY
# --------------------------------
def get_db():

    db = SessionLocal()

    try:

        yield db

    except Exception as e:

        logger.error(f"Database session error: {str(e)}")
        db.rollback()
        raise

    finally:

        db.close()