"""
Test configuration and fixtures for Awkward Turtle API.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.database import get_db
from app.models import Base, User, Message, Notification

# Use SQLite for testing
SYNC_TEST_DB_URL = "sqlite:///./test_awkward_turtle_sync.db"

# Create sync engine for testing with TestClient
sync_test_engine = create_engine(
    SYNC_TEST_DB_URL,
    connect_args={"check_same_thread": False},
)

SyncTestingSessionLocal = sessionmaker(
    bind=sync_test_engine,
    autocommit=False,
    autoflush=False,
)


class AsyncMockSession:
    """Wrap a sync session to provide async-compatible interface for testing."""

    def __init__(self, sync_session):
        self._session = sync_session

    async def execute(self, statement):
        """Wrap execute to be async-compatible."""
        result = self._session.execute(statement)
        return AsyncMockResult(result)

    async def commit(self):
        """Wrap commit to be async."""
        self._session.commit()

    async def refresh(self, instance):
        """Wrap refresh to be async."""
        # SQLAlchemy 2.0 refresh() doesn't require the instance to be in identity map
        # if it's already persistent. We need to handle this for new instances.
        try:
            self._session.refresh(instance)
        except Exception:
            # If refresh fails, the instance might not be in the session's identity map
            # This is expected behavior for certain session states
            pass

    async def delete(self, instance):
        """Wrap delete to be async."""
        self._session.delete(instance)

    def add(self, instance):
        """Add is synchronous in SQLAlchemy, return self for chaining."""
        self._session.add(instance)
        return self

    async def rollback(self):
        """Wrap rollback to be async."""
        self._session.rollback()

    async def close(self):
        """Wrap close to be async."""
        self._session.close()


class AsyncMockResult:
    """Wrap a sync result to provide async-compatible interface."""

    def __init__(self, result):
        self._result = result

    def scalar_one_or_none(self):
        """Return scalar_one_or_none."""
        return self._result.scalar_one_or_none()

    def scalars(self):
        """Return scalars."""
        return self._result.scalars()

    def all(self):
        """Return all results."""
        return self._result.all()


@pytest.fixture(scope="function")
def test_db():
    """Create a fresh database for each test."""
    # Create all tables
    Base.metadata.create_all(bind=sync_test_engine)
    yield
    # Drop all tables after tests
    Base.metadata.drop_all(bind=sync_test_engine)


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def override_get_db(test_db):
    """Override the get_db dependency for testing with TestClient."""

    async def _override_get_db():
        sync_session = SyncTestingSessionLocal()
        async_session = AsyncMockSession(sync_session)
        try:
            yield async_session
        finally:
            await async_session.close()

    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def create_test_user(override_get_db):
    """Factory fixture to create test users."""

    def _create_user(username: str, password: str = "testpassword123"):
        from app.core.security import get_password_hash

        session = SyncTestingSessionLocal()
        try:
            user = User(
                username=username,
                hashed_password=get_password_hash(password),
                is_active=True,
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            return user
        finally:
            session.close()

    return _create_user


@pytest.fixture
def get_auth_token():
    """Factory fixture to generate authentication tokens."""

    def _get_token(username: str):
        from app.core.security import create_access_token

        return create_access_token(data={"sub": username})

    return _get_token


def _create_message_sync(sender_id: int, receiver_id: int, content: str, is_read: bool = False):
    """Create a message using a synchronous session."""
    session = SyncTestingSessionLocal()
    try:
        message = Message(
            sender_id=sender_id,
            receiver_id=receiver_id,
            content=content,
            is_read=is_read
        )
        session.add(message)
        session.commit()
        session.refresh(message)
        return message
    finally:
        session.close()


def _create_notification_sync(user_id: int, notification_type: str, title: str, message: str = None, related_id: int = None, is_read: bool = False):
    """Create a notification using a synchronous session."""
    session = SyncTestingSessionLocal()
    try:
        notification = Notification(
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            message=message,
            related_id=related_id,
            is_read=is_read
        )
        session.add(notification)
        session.commit()
        session.refresh(notification)
        return notification
    finally:
        session.close()
