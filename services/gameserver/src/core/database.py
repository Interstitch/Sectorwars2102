from typing import Generator, AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, declarative_base

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

# Create async engine and session
async_engine = create_async_engine(
    settings.get_db_url().replace("postgresql://", "postgresql+asyncpg://"),
    pool_size=settings.SQLALCHEMY_POOL_SIZE,
    max_overflow=settings.SQLALCHEMY_MAX_OVERFLOW,
    pool_pre_ping=True,
)

# Create async session maker
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
)

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


# Async dependency to get DB session
async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Async dependency function that yields async db session and ensures
    it's closed after request is processed.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()