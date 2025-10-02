"""
Authentication and authorization schemas
"""

from pydantic import BaseModel, Field
from typing import Optional

class TokenResponse(BaseModel):
    """Oauth token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: Optional[int] = None
    user: "UserResponse"

class DiscordUser(BaseModel):
    """Discord user information from OAuth"""
    id: str
    username: str
    avatar: Optional[str] = None
    email: Optional[str] = None
    verified: Optional[bool] = None

class DiscordTokenResponse(BaseModel):
    """Discord Oauth token response"""
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str
    scope: str

from app.schemas.user import UserResponse
TokenResponse.model_rebuild()