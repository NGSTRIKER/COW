import os
from collections.abc import AsyncIterator

from dotenv import load_dotenv
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from database.leveling_models import LevelingBase

# Load environment configuration
load_dotenv()

# Read leveling database URL from environment variable, defaulting to a dedicated local SQLite database file
LEVELING_DATABASE_URL = os.getenv("LEVELING_DATABASE_URL", "sqlite+aiosqlite:///leveling.db")

# Normalize database connection scheme for SQLAlchemy asynchronous drivers
if LEVELING_DATABASE_URL.startswith("sqlite://"):
    LEVELING_DATABASE_URL = LEVELING_DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://", 1)
elif LEVELING_DATABASE_URL.startswith("postgres://"):
    LEVELING_DATABASE_URL = LEVELING_DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
elif LEVELING_DATABASE_URL.startswith("postgresql://") and not LEVELING_DATABASE_URL.startswith("postgresql+asyncpg://"):
    LEVELING_DATABASE_URL = LEVELING_DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# Create asynchronous database engine instance for leveling data
leveling_engine = create_async_engine(LEVELING_DATABASE_URL, echo=False, pool_pre_ping=True)


# Configure SQLite connection PRAGMAs for durability and performance:
# - WAL (Write-Ahead Logging) eliminates read/write contention and guarantees zero data loss on restarts/crashes
# - synchronous=NORMAL balances high performance with strong durability
# - foreign_keys=ON enforces referential integrity
@event.listens_for(leveling_engine.sync_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


# Session factory producing AsyncSession instances for leveling database transactions
LevelingSessionLocal = async_sessionmaker(bind=leveling_engine, class_=AsyncSession, expire_on_commit=False)


async def get_leveling_session() -> AsyncIterator[AsyncSession]:
    """
    Dependency generator for acquiring an asynchronous leveling database session context.
    """
    async with LevelingSessionLocal() as session:
        yield session


async def init_leveling_db():
    """
    Initializes the dedicated leveling database by creating all tables defined in LevelingBase
    if they do not already exist.
    """
    async with leveling_engine.begin() as conn:
        await conn.run_sync(LevelingBase.metadata.create_all)
    print("[Leveling Database] Dedicated leveling schema initialized (WAL mode active).")
