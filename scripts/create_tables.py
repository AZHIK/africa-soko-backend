# scripts/create_tables.py
import asyncio
from app.db.session import engine
from sqlmodel import SQLModel
from app.db.base import Base  # all models imported here  # noqa: F401


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


asyncio.run(create_tables())
