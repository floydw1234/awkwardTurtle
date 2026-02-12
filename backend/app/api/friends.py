"""
Friend management API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.database import get_db
from app.models import User, friendships

router = APIRouter(prefix="/friends", tags=["friends"])


@router.post("/add/{username}")
async def add_friend(
    username: str,
    db: AsyncSession = Depends(get_db)
):
    """Add a friend by username."""
    # Find the current user (from auth cookie - to be implemented with dependency)
    # For now, we'll need an auth dependency
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Authentication dependency not yet implemented"
    )


@router.post("/remove/{username}")
async def remove_friend(
    username: str,
    db: AsyncSession = Depends(get_db)
):
    """Remove a friend by username."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Authentication dependency not yet implemented"
    )


@router.get("")
async def get_friends(
    db: AsyncSession = Depends(get_db)
):
    """Get list of friends."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Authentication dependency not yet implemented"
    )
