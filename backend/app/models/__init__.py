"""
Models module - Database models (ORM).
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

# Association table for friendships (many-to-many)
friendships = Table(
    "friendships",
    Base.metadata,
    Column("user1_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("user2_id", Integer, ForeignKey("users.id"), primary_key=True),
)


class User(Base):
    """User model for authentication and friend management."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    sent_messages = relationship(
        "Message", foreign_keys="Message.sender_id", back_populates="sender"
    )
    received_messages = relationship(
        "Message", foreign_keys="Message.receiver_id", back_populates="receiver"
    )
    friends = relationship(
        "User",
        secondary=friendships,
        primaryjoin=id == friendships.c.user1_id,
        secondaryjoin=id == friendships.c.user2_id,
        backref="friend_of",
    )

    def __repr__(self):
        return f"<User(username='{self.username}')>"


class Message(Base):
    """Message model with read receipt tracking."""

    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(String, nullable=False)
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    sender = relationship(
        "User", foreign_keys=[sender_id], back_populates="sent_messages"
    )
    receiver = relationship(
        "User", foreign_keys=[receiver_id], back_populates="received_messages"
    )

    def __repr__(self):
        return f"<Message(id={self.id}, sender_id={self.sender_id}, receiver_id={self.receiver_id})>"


class Notification(Base):
    """Notification model for alerts (new messages, read receipts)."""

    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    notification_type = Column(
        String, nullable=False
    )  # 'new_message', 'message_read', 'friend_request'
    title = Column(String, nullable=False)
    message = Column(String, nullable=True)
    related_id = Column(Integer, nullable=True)  # ID of related message/user
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    user = relationship("User", backref="notifications")

    def __repr__(self):
        return (
            f"<Notification(type='{self.notification_type}', user_id={self.user_id})>"
        )
