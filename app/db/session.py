from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# async engine using the DATABASE_URL from config
engine = create_async_engine(settings.DATABASE_URL, echo=True, future=True)

# async session factory
AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)


# Dependency for FastAPI routes
async def get_session() -> AsyncSession:  # type: ignore
    """
    Yields a database session that automatically closes after use.
    Example:
        async def endpoint(session: AsyncSession = Depends(get_session)):
            ...
    """
    async with AsyncSessionLocal() as session:
        yield session
