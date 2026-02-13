"""
Message API endpoints.
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.security import get_current_user
from app.db.database import get_db
from app.models import User, Message, Notification
from app.schemas.message import MessageCreate, MessageOut, InboxOut, OutboxOut, ReadReceipt

router = APIRouter(prefix="/messages", tags=["messages"])


@router.post("/send")
async def send_message(
    message: MessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Send a message to another user."""
    # Find the recipient
    result = await db.execute(select(User).where(User.id == message.to_user_id))
    receiver = result.scalar_one_or_none()

    if not receiver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipient not found"
        )

    # Create the message
    new_message = Message(
        sender_id=current_user.id,
        receiver_id=message.to_user_id,
        content=message.content
    )

    db.add(new_message)
    await db.commit()
    await db.refresh(new_message)

    # Create notification for the receiver (new message alert)
    notification = Notification(
        user_id=receiver.id,
        notification_type="new_message",
        title="New Message",
        message=f"{current_user.username} sent you a message",
        related_id=new_message.id
    )
    db.add(notification)
    await db.commit()

    return MessageOut.model_validate(new_message)


@router.get("/inbox")
async def get_inbox(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get received messages (inbox)."""
    result = await db.execute(
        select(Message)
        .where(Message.receiver_id == current_user.id)
        .order_by(Message.created_at.desc())
    )
    messages = result.scalars().all()

    return InboxOut(
        messages=[MessageOut.model_validate(msg) for msg in messages],
        total=len(messages)
    )


@router.get("/outbox")
async def get_outbox(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get sent messages (outbox)."""
    result = await db.execute(
        select(Message)
        .where(Message.sender_id == current_user.id)
        .order_by(Message.created_at.desc())
    )
    messages = result.scalars().all()

    return OutboxOut(
        messages=[MessageOut.model_validate(msg) for msg in messages],
        total=len(messages)
    )


@router.post("/{message_id}/read", response_model=ReadReceipt)
async def mark_message_as_read(
    message_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark a message as read and notify the sender."""
    result = await db.execute(
        select(Message).where(Message.id == message_id)
    )
    message = result.scalar_one_or_none()

    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )

    # Check if user is the receiver
    if message.receiver_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only mark your own messages as read"
        )

    # Mark as read
    message.is_read = True
    message.read_at = datetime.utcnow()
    await db.commit()
    await db.refresh(message)

    # Create notification for the sender (read receipt alert)
    notification = Notification(
        user_id=message.sender_id,
        notification_type="message_read",
        title="Message Read",
        message=f"{current_user.username} read your message",
        related_id=message.id
    )
    db.add(notification)
    await db.commit()

    return ReadReceipt(message_id=message.id, read_at=message.read_at)
