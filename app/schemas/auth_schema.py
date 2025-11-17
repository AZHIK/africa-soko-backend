from pydantic import BaseModel, Field
from typing import Optional


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., alias="___refresh_token")


class RefreshTokenResponse(BaseModel):
    access_token: str = Field(..., alias="___access_token")
    refresh_token: Optional[str] = Field(None, alias="___refresh_token")
