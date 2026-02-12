"""
Message-related Pydantic schemas.
"""

from datetime import datetime
from pydantic import BaseModel, Field


class MessageBase(BaseModel):
    """Base message schema."""
    content: str = Field(..., min_length=1, max_length=1000)


class MessageCreate(MessageBase):
    """Schema for sending a message."""
    to_user_id: int = Field(..., gt=0)


class MessageOut(BaseModel):
    """Schema for message response."""
    id: int
    sender_id: int
    receiver_id: int
    content: str
    is_read: bool
    read_at: datetime | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class InboxOut(BaseModel):
    """Schema for inbox response."""
    messages: list[MessageOut]
    total: int


class OutboxOut(BaseModel):
    """Schema for outbox response."""
    messages: list[MessageOut]
    total: int


class ReadReceipt(BaseModel):
    """Schema for read receipt confirmation."""
    message_id: int
    read_at: datetime
