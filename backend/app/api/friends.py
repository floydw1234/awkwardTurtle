"""
Friend management API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.security import get_current_user
from app.db.database import get_db
from app.models import User, friendships

router = APIRouter(prefix="/friends", tags=["friends"])


@router.post("/add/{username}")
async def add_friend(
    username: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a friend by username."""
    # Find the user to add as friend
    result = await db.execute(select(User).where(User.username == username))
    friend_user = result.scalar_one_or_none()

    if not friend_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{username}' not found"
        )

    # Prevent adding self as friend
    if friend_user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot add yourself as a friend"
        )

    # Check if already friends
    if friend_user in current_user.friends:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User '{username}' is already your friend"
        )

    # Add friendship (bidirectional)
    current_user.friends.append(friend_user)
    await db.commit()

    return {"message": f"Added '{username}' as friend"}


@router.post("/remove/{username}")
async def remove_friend(
    username: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove a friend by username."""
    # Find the user to remove
    result = await db.execute(select(User).where(User.username == username))
    friend_user = result.scalar_one_or_none()

    if not friend_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{username}' not found"
        )

    # Check if actually friends
    if friend_user not in current_user.friends:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User '{username}' is not your friend"
        )

    # Remove friendship (bidirectional)
    current_user.friends.remove(friend_user)
    await db.commit()

    return {"message": f"Removed '{username}' from friends"}


@router.get("", response_model=dict)
async def get_friends(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of friends."""
    return {
        "friends": [user.username for user in current_user.friends],
        "total": len(current_user.friends)
    }
