from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session
from app.schemas.chat_schema import (
    LastConversationRequest,
    ConversationSummary,
    GetConversationRequest,
    ConversationResponse,
    SendMessageRequest,
    SendMessageResponse,
)
from typing import List

router = APIRouter(tags=["Chats"])


@router.post("/last_conversation", response_model=List[ConversationSummary])
async def last_conversation(
    request: LastConversationRequest, db: AsyncSession = Depends(get_session)
):
    # Placeholder
    return []


@router.post("/get_conversation", response_model=ConversationResponse)
async def get_conversation(
    request: GetConversationRequest, db: AsyncSession = Depends(get_session)
):
    # Placeholder
    return {"status": "success", "messages": []}


@router.post("/send_message", response_model=SendMessageResponse)
async def send_message(
    request: SendMessageRequest, db: AsyncSession = Depends(get_session)
):
    # Placeholder
    return {"status": "success"}
