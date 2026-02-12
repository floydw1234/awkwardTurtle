"""
Notification-related Pydantic schemas.
"""

from datetime import datetime
from pydantic import BaseModel


class NotificationBase(BaseModel):
    """Base notification schema."""
    notification_type: str
    title: str
    message: str | None = None
    related_id: int | None = None


class NotificationOut(NotificationBase):
    """Schema for notification response."""
    id: int
    user_id: int
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationsList(BaseModel):
    """Schema for notifications list response."""
    notifications: list[NotificationOut]
    total: int
