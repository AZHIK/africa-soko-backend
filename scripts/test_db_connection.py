import asyncio
import sys
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.config import settings

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


async def test_connection():
    print("🔍 Testing database connection...")
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            print("Database connection successful:", result.scalar_one())
    except Exception as e:
        print(" Database connection failed:", e)
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(test_connection())
