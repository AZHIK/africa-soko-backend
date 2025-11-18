from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import User


async def get_all_usernames(session: AsyncSession):
    """
    Fetches all usernames from the database.
    """
    result = await session.execute(select(User.username))
    return [row[0] for row in result.fetchall() if row[0] is not None]
