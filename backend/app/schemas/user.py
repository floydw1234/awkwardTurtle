"""
User-related Pydantic schemas.
"""

from datetime import datetime
from pydantic import BaseModel, Field


class UserBase(BaseModel):
    """Base user schema."""

    username: str = Field(..., min_length=3, max_length=50)


class UserCreate(UserBase):
    """Schema for user registration."""

    password: str = Field(..., min_length=6)


class UserOut(UserBase):
    """Schema for user response."""

    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema for authentication token response."""

    access_token: str
    token_type: str = "bearer"


class LoginOut(BaseModel):
    """Schema for login success response."""

    message: str
    user: UserOut


class UserLogin(BaseModel):
    """Schema for user login request."""

    username: str
    password: str


class UserStatusUpdate(BaseModel):
    """Schema for user status update."""

    is_active: bool
