"""
API Router - Main entry point for all API endpoints.
"""

from fastapi import APIRouter

from app.api import auth
from app.api import friends
from app.api import messages
from app.api import notifications
from app.api import users

router = APIRouter()

# Include all API routers (without extra prefix - it's added in main.py)
router.include_router(auth.router)
router.include_router(friends.router)
router.include_router(messages.router)
router.include_router(notifications.router)
router.include_router(users.router)


@router.get("/")
async def api_root():
    """API root endpoint."""
    return {"message": "Awkward Turtle API v1"}
