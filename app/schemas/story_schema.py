from pydantic import BaseModel
from datetime import datetime
from typing import List


class StoryData(BaseModel):
    story_url: str
    post_date: datetime
    caption: str


class PostStoryRequest(BaseModel):
    id: str
    data: StoryData


class StoryResponse(BaseModel):
    user_id: str
    profile_pic: str
    story_list: List[StoryData]


class GetStoryRequest(BaseModel):
    id: str
