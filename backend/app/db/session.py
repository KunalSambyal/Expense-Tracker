from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from collections.abc import AsyncGenerator

from app.core.config import settings

async_engine = create_async_engine(settings.DATABASE_URL)
AsyncSessionFactory = async_sessionmaker(bind=async_engine, autoflush=False, expire_on_commit=False)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionFactory() as session:
        yield session
