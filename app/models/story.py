from typing import List, Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from .user import User


class Story(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    story_url: str = Field(nullable=False)
    caption: Optional[str] = None
    post_date: datetime = Field(default_factory=datetime.now)
    created_at: datetime = Field(default_factory=datetime.now)

    user: Optional[User] = Relationship()


class Conversation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user1_id: int = Field(foreign_key="user.id")
    user2_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.now)

    messages: List["Message"] = Relationship(back_populates="conversation")
    user1: Optional[User] = Relationship(sa_relationship_kwargs={"lazy": "joined"})
    user2: Optional[User] = Relationship(sa_relationship_kwargs={"lazy": "joined"})


class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversation.id")
    sender_id: int = Field(foreign_key="user.id")
    msg_content: str = Field(nullable=False)
    msg_type: str = Field(default="text")  # "text" | "image" | "link"
    sent_at: datetime = Field(default_factory=datetime.now)

    conversation: Optional[Conversation] = Relationship(back_populates="messages")
    sender: Optional[User] = Relationship()
