from pydantic import BaseModel, Field
from typing import List
from datetime import datetime


class LastConversationRequest(BaseModel):
    id: str


class ConversationSummary(BaseModel):
    sender_id: str
    name: str
    img: str
    time: str
    message: str


class GetConversationRequest(BaseModel):
    id: str
    target_id: str


class Message(BaseModel):
    sender: str
    msg_content: str
    msg_type: str  # "text" | "image" | "link"
    sent_at: datetime


class ConversationResponse(BaseModel):
    status: str
    messages: List[Message]


class SendMessageRequest(BaseModel):
    from_id: str = Field(..., alias="from")
    to: str
    type: str  # "text" | "image" | "link"
    content: str


class SendMessageResponse(BaseModel):
    status: str
