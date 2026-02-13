"""
User API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.schemas.user import UserOut, UserStatusUpdate
from app.db.database import get_db
from app.models import User

router = APIRouter(prefix="/users", tags=["users"])


@router.put("/{user_id}/status", response_model=UserOut)
async def update_user_status(
    user_id: int, status_update: UserStatusUpdate, db: AsyncSession = Depends(get_db)
):
    """Update user active status."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )

    user.is_active = status_update.is_active
    await db.commit()
    await db.refresh(user)

    return user
