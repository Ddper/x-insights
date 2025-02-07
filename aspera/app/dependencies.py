from typing import Generator
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import AsyncSessionLocal


async def get_db() -> Generator[AsyncSession, None, None]:
    async with AsyncSessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()
