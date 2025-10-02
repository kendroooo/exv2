"""
User related schemas for req-rep validation
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    """Base user schema"""
    discord_username: str
    email: Optional[str] = None

class UserCreate(UserBase):
    """Schema for creating a new user"""
    discord_id: str
    discord_avatar: Optional[str] = None

class UserUpdate(BaseModel):
    """Schema for updating a user"""
    discord_username: Optional[str] = None
    discord_avatar: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None
    is_banned: Optional[bool] = None

class UserResponse(UserBase):
    """Schema for user response"""
    id: int
    discord_id: str
    avatar_url: Optional[str] = None
    is_admin: bool
    is_active: bool
    is_banned: bool = False
    created_at: datetime
    last_login: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class UserWithStats(UserResponse):
    """User response with stats"""
    vm_count: int = 0
    active_vm_count: int = 0