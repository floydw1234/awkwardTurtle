"""
Awkward Turtle - FastAPI Backend
Main application entry point
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api import router as api_router
from app.db import engine, Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    # Startup: Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown: Cleanup if needed
    await engine.dispose()


app = FastAPI(
    title="Awkward Turtle API",
    description="Backend API for awkward messaging app with read receipts",
    version="1.0.0",
    lifespan=lifespan,
)

# Include API router
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Awkward Turtle API",
        "version": "1.0.0",
        "docs": "/docs",
    }
