# Schemas module
"""
Pydantic schemas for API request/response validation.
"""

from app.schemas.user import UserCreate, UserLogin, UserOut, Token
from app.schemas.message import MessageCreate, MessageOut, InboxOut, OutboxOut, ReadReceipt
from app.schemas.friend import FriendAdd, FriendRemove, FriendsList
from app.schemas.notification import NotificationOut, NotificationsList

__all__ = [
    "UserCreate",
    "UserLogin",
    "UserOut",
    "Token",
    "MessageCreate",
    "MessageOut",
    "InboxOut",
    "OutboxOut",
    "ReadReceipt",
    "FriendAdd",
    "FriendRemove",
    "FriendsList",
    "NotificationOut",
    "NotificationsList",
]
