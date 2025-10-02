"""
Common schemas that will be used amongst the other schemas and application
"""

from pydantic import BaseModel, Field
from typing import Generic, TypeVar, List, Optional

T = TypeVar('T')

class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    success: bool = True

class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated resp"""
    items: List[T]
    total: int
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=100)
    pages: int

    @classmethod
    def create(
            cls,
            items: List[T],
            total: int,
            page: int,
            page_size: int
    ):
        """Create paginated response"""

        pages = (
            total + page_size - 1
        ) // page_size

        return cls(
            items=items, total=total, page=page, page_size=page_size, pages=pages
        )

class ErrorResponse(BaseModel):
    """Error response"""

    error: str
    detail: Optional[str] = None
    success: bool = False # i guess