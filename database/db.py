import os
from collections.abc import AsyncIterator

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Load environment configuration
load_dotenv()

# Read database URL from environment variable
# Defaults to a local SQLite database file (cow.db) if DATABASE_URL is not provided
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///cow.db")

# Normalize database connection scheme for SQLAlchemy asynchronous drivers:
# - SQLite requires the 'sqlite+aiosqlite://' prefix for async I/O
# - PostgreSQL requires the 'postgresql+asyncpg://' prefix for async I/O
if DATABASE_URL.startswith("sqlite://"):
    DATABASE_URL = DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://", 1)
elif DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
elif DATABASE_URL.startswith("postgresql://") and not DATABASE_URL.startswith("postgresql+asyncpg://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# Create asynchronous database engine instance
engine = create_async_engine(DATABASE_URL, echo=False, pool_pre_ping=True)

# Session factory producing AsyncSession instances for database queries and transactions
SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    """
    Dependency generator for acquiring an asynchronous database session context.
    """
    async with SessionLocal() as session:
        yield session
