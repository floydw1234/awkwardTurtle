"""
Authentication API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user,
)
from app.schemas.user import UserCreate, UserLogin, UserOut, Token, LoginOut
from app.db.database import get_db
from app.models import User

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user."""
    # Check if user already exists
    result = await db.execute(select(User).where(User.username == user.username))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    # Create new user with hashed password
    new_user = User(
        username=user.username,
        hashed_password=get_password_hash(user.password),
        is_active=True,
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


@router.post("/login", response_model=LoginOut)
async def login_user(
    response: Response, user: UserLogin, db: AsyncSession = Depends(get_db)
):
    """Authenticate user and set secure cookie."""
    # Find user by username
    result = await db.execute(select(User).where(User.username == user.username))
    db_user = result.scalar_one_or_none()

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    # Verify password
    if not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    # Update is_active to True on login
    db_user.is_active = True

    # Create access token
    access_token = create_access_token(data={"sub": db_user.username})

    # Set cookie (HTTP-only, secure)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        max_age=60 * 60 * 24,  # 24 hours
    )

    await db.commit()
    await db.refresh(db_user)

    return LoginOut(message="Login successful", user=UserOut.model_validate(db_user))


@router.post("/logout")
async def logout_user(
    response: Response,
    db_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    db_user.is_active = False
    await db.commit()
    await db.refresh(db_user)

    response.delete_cookie(key="access_token")
    return {"message": "Logged out successfully"}
