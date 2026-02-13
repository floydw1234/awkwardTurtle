"""
Notification API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.security import get_current_user
from app.db.database import get_db
from app.models import Notification, User
from app.schemas.notification import NotificationOut, NotificationsList

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=NotificationsList)
async def get_notifications(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all notifications for the current user."""
    result = await db.execute(
        select(Notification)
        .where(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
    )
    notifications = result.scalars().all()

    return NotificationsList(
        notifications=[NotificationOut.model_validate(notif) for notif in notifications],
        total=len(notifications)
    )


@router.get("/{notification_id}", response_model=NotificationOut)
async def get_notification(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific notification."""
    result = await db.execute(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == current_user.id
        )
    )
    notification = result.scalar_one_or_none()

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    return NotificationOut.model_validate(notification)


@router.post("/{notification_id}/read")
async def mark_notification_as_read(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark a notification as read."""
    result = await db.execute(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == current_user.id
        )
    )
    notification = result.scalar_one_or_none()

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    notification.is_read = True
    await db.commit()
    await db.refresh(notification)

    return {"message": "Notification marked as read", "notification_id": notification_id}


@router.delete("")
async def delete_all_notifications(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete all notifications for the current user."""
    result = await db.execute(
        select(Notification).where(Notification.user_id == current_user.id)
    )
    notifications = result.scalars().all()

    for notification in notifications:
        await db.delete(notification)
    await db.commit()

    return {"message": "All notifications deleted"}
