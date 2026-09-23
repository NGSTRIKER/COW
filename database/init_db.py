from database.db import engine
from database.models import Base


async def init_db():
    """
    Initializes the database by creating all tables defined in SQLAlchemy ORM models
    if they do not already exist in the target database instance.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("[Database] Database schema successfully initialized.")