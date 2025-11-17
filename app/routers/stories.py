from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session
from app.schemas.story_schema import PostStoryRequest, GetStoryRequest, StoryResponse
from typing import List

router = APIRouter(tags=["Stories"])


@router.post("/post_story")
async def post_story(
    request: PostStoryRequest, db: AsyncSession = Depends(get_session)
):
    # Server Logic:
    # 1. Authenticate the user.
    # 2. Add the story data to the user's story list in the database.
    # 3. Return a success confirmation.
    # This is a placeholder implementation
    return {"status": "success", "message": "Story posted"}


@router.post("/get_story", response_model=List[StoryResponse])
async def get_story(request: GetStoryRequest, db: AsyncSession = Depends(get_session)):
    # Server Logic:
    # 1. Find the user and the list of users they follow.
    # 2. Aggregate all recent (e.g., last 24 hours) stories from these users.
    # 3. Return a list of story objects, grouped by user.
    # This is a placeholder implementation
    return []
