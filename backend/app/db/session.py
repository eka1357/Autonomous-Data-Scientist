from typing import AsyncGenerator
import os
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

# Determine DB host: if running locally outside docker, fallback to localhost
default_url = "postgresql+asyncpg://autods_user:autods_password@localhost:5432/autods_db"
db_url = settings.DATABASE_URL or default_url

# If configured with docker host 'postgres' but running locally outside docker, use localhost
if "postgres:5432" in db_url and not os.path.exists("/.dockerenv"):
    db_url = db_url.replace("postgres:5432", "localhost:5432")

engine = create_async_engine(
    db_url,
    echo=settings.ENVIRONMENT == "development",
    future=True,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
