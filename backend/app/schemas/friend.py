"""
Friend-related Pydantic schemas.
"""

from pydantic import BaseModel


class FriendAdd(BaseModel):
    """Schema for adding a friend."""
    message: str
    friend_username: str


class FriendRemove(BaseModel):
    """Schema for removing a friend."""
    message: str
    friend_username: str


class FriendsList(BaseModel):
    """Schema for friends list response."""
    friends: list[str]
    total: int
