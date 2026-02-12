"""
API Router - Main entry point for all API endpoints.
"""

from fastapi import APIRouter

from app.api import auth
from app.api import friends
from app.api import messages
from app.api import notifications

router = APIRouter()

# Include all API routers
router.include_router(auth.router, prefix="/api/v1")
router.include_router(friends.router, prefix="/api/v1")
router.include_router(messages.router, prefix="/api/v1")
router.include_router(notifications.router, prefix="/api/v1")


@router.get("/")
async def api_root():
    """API root endpoint."""
    return {"message": "Awkward Turtle API v1"}
