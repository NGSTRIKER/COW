from database.db import engine
from database.leveling_db import init_leveling_db
from database.models import Base


async def init_db():
    """
    Initializes the database by creating all tables defined in SQLAlchemy ORM models
    if they do not already exist in the target database instance.
    Also initializes the dedicated leveling database.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await init_leveling_db()
    print("[Database] All database schemas successfully initialized.")