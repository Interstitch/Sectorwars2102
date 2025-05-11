from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from src.core.config import settings

# Create SQLAlchemy engine instance
# Use the appropriate database URL based on environment
engine = create_engine(
    settings.get_db_url(),
    pool_size=settings.SQLALCHEMY_POOL_SIZE,
    max_overflow=settings.SQLALCHEMY_MAX_OVERFLOW,
    pool_pre_ping=True,
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()


# Dependency to get DB session
def get_db() -> Generator:
    """
    Dependency function that yields db session and ensures
    it's closed after request is processed.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()