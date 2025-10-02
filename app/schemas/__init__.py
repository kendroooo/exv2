"""
Pydantic schemas for req-rep validation
Type-safe data transfer objs
"""

from app.schemas.user import UserResponse, UserCreate, UserUpdate, UserWithStats
from app.schemas.vm import (
    VMResponse,
    VMCreate,
    VMUpdate,
    VMAction,
    VMStats
)
from app.schemas.ports import PortForwardResponse, PortForwardCreate, PortForwardUpdate
from app.schemas.auth import TokenResponse, DiscordTokenResponse, DiscordUser
from app.schemas.common import MessageResponse, PaginatedResponse, ErrorResponse

__all__ = (
    "UserResponse",
    "UserWithStats",
    "UserCreate",
    "UserUpdate",
    "VMStats",
    "VMUpdate",
    "VMAction",
    "VMCreate",
    "VMResponse",
    "PortForwardCreate",
    "PortForwardResponse",
    "PortForwardUpdate",
    "TokenResponse",
    "DiscordUser",
    "DiscordTokenResponse",
    "MessageResponse",
    "PaginatedResponse",
    "ErrorResponse"
)