from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from app.db.database import engine

# Create a factory for database sessions
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Dependency used by FastAPI endpoints
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
