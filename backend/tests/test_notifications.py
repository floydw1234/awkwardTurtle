"""
Tests for notification endpoints.
"""

import asyncio

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models import User, Notification


class TestGetNotificationsEndpoint:
    """Tests for GET /api/v1/notifications endpoint."""

    def test_get_notifications_success(
        self, client, test_db, override_get_db, create_test_user
    ):
        """Test getting notifications."""
        user = create_test_user("user", "password123")

        from app.core.security import create_access_token

        token = create_access_token(data={"sub": "user"})
        client.cookies.set("access_token", token)

        # Create some notifications
        from app.db.database import AsyncSessionLocal
        from app.models import Notification

        notif1 = Notification(
            user_id=user.id,
            notification_type="new_message",
            title="New Message",
            message="You have a new message",
        )
        notif2 = Notification(
            user_id=user.id,
            notification_type="message_read",
            title="Message Read",
            message="Your message was read",
        )

        # Create notifications using sync session helper
        from tests.conftest import _create_notification_sync

        _create_notification_sync(
            user.id, "new_message", "New Message", "You have a new message"
        )
        _create_notification_sync(
            user.id, "message_read", "Message Read", "Your message was read"
        )

        response = client.get("/api/v1/notifications")

        assert response.status_code == 200
        data = response.json()
        assert "notifications" in data
        assert "total" in data
        assert data["total"] == 2

    def test_get_notifications_empty(
        self, client, test_db, override_get_db, create_test_user
    ):
        """Test getting empty notifications list."""
        user = create_test_user("user", "password123")

        from app.core.security import create_access_token

        token = create_access_token(data={"sub": "user"})
        client.cookies.set("access_token", token)

        response = client.get("/api/v1/notifications")

        assert response.status_code == 200
        data = response.json()
        assert data["notifications"] == []
        assert data["total"] == 0

    def test_get_notifications_unauthenticated(self, client, test_db, override_get_db):
        """Test getting notifications without authentication."""
        response = client.get("/api/v1/notifications")

        assert response.status_code == 401


class TestGetNotificationEndpoint:
    """Tests for GET /api/v1/notifications/{notification_id} endpoint."""

    def test_get_notification_success(
        self, client, test_db, override_get_db, create_test_user
    ):
        """Test getting a specific notification."""
        user = create_test_user("user", "password123")

        from app.core.security import create_access_token

        token = create_access_token(data={"sub": "user"})
        client.cookies.set("access_token", token)

        # Create a notification
        from app.db.database import AsyncSessionLocal
        from app.models import Notification

        notif = Notification(
            user_id=user.id,
            notification_type="new_message",
            title="New Message",
            message="You have a new message",
        )

        # Create notification using sync session helper
        from tests.conftest import _create_notification_sync

        notif = _create_notification_sync(
            user.id, "new_message", "New Message", "You have a new message"
        )

        response = client.get(f"/api/v1/notifications/{notif.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == notif.id
        assert data["notification_type"] == "new_message"

    def test_get_notification_not_found(
        self, client, test_db, override_get_db, create_test_user
    ):
        """Test getting a non-existent notification."""
        user = create_test_user("user", "password123")

        from app.core.security import create_access_token

        token = create_access_token(data={"sub": "user"})
        client.cookies.set("access_token", token)

        response = client.get("/api/v1/notifications/999")

        assert response.status_code == 404
        assert response.json()["detail"] == "Notification not found"

    def test_get_notification_unauthenticated(self, client, test_db, override_get_db):
        """Test getting a notification without authentication."""
        response = client.get("/api/v1/notifications/1")

        assert response.status_code == 401


class TestMarkNotificationAsReadEndpoint:
    """Tests for POST /api/v1/notifications/{notification_id}/read endpoint."""

    def test_mark_notification_as_read_success(
        self, client, test_db, override_get_db, create_test_user
    ):
        """Test marking a notification as read."""
        user = create_test_user("user", "password123")

        from app.core.security import create_access_token

        token = create_access_token(data={"sub": "user"})
        client.cookies.set("access_token", token)

        # Create a notification
        from app.db.database import AsyncSessionLocal
        from app.models import Notification

        notif = Notification(
            user_id=user.id,
            notification_type="new_message",
            title="New Message",
            message="You have a new message",
        )

        # Create notification using sync session helper
        from tests.conftest import _create_notification_sync

        notif = _create_notification_sync(
            user.id, "new_message", "New Message", "You have a new message"
        )

        response = client.post(f"/api/v1/notifications/{notif.id}/read")

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Notification marked as read"
        assert data["notification_id"] == notif.id

    def test_mark_notification_as_read_not_found(
        self, client, test_db, override_get_db, create_test_user
    ):
        """Test marking a non-existent notification as read."""
        user = create_test_user("user", "password123")

        from app.core.security import create_access_token

        token = create_access_token(data={"sub": "user"})
        client.cookies.set("access_token", token)

        response = client.post("/api/v1/notifications/999/read")

        assert response.status_code == 404
        assert response.json()["detail"] == "Notification not found"

    def test_mark_notification_as_read_unauthenticated(
        self, client, test_db, override_get_db
    ):
        """Test marking a notification as read without authentication."""
        response = client.post("/api/v1/notifications/1/read")

        assert response.status_code == 401


class TestDeleteAllNotificationsEndpoint:
    """Tests for DELETE /api/v1/notifications endpoint."""

    def test_delete_all_notifications_success(
        self, client, test_db, override_get_db, create_test_user
    ):
        """Test deleting all notifications."""
        user = create_test_user("user", "password123")

        from app.core.security import create_access_token

        token = create_access_token(data={"sub": "user"})
        client.cookies.set("access_token", token)

        # Create some notifications
        from app.db.database import AsyncSessionLocal
        from app.models import Notification

        notif1 = Notification(
            user_id=user.id,
            notification_type="new_message",
            title="New Message",
            message="You have a new message",
        )
        notif2 = Notification(
            user_id=user.id,
            notification_type="message_read",
            title="Message Read",
            message="Your message was read",
        )

        # Create notifications using sync session helper
        from tests.conftest import _create_notification_sync

        _create_notification_sync(
            user.id, "new_message", "New Message", "You have a new message"
        )
        _create_notification_sync(
            user.id, "message_read", "Message Read", "Your message was read"
        )

        # Verify notifications exist
        response = client.get("/api/v1/notifications")
        assert response.json()["total"] == 2

        # Delete all notifications
        response = client.delete("/api/v1/notifications")

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "All notifications deleted"

        # Verify notifications are deleted
        response = client.get("/api/v1/notifications")
        assert response.json()["total"] == 0

    def test_delete_all_notifications_empty(
        self, client, test_db, override_get_db, create_test_user
    ):
        """Test deleting all notifications when none exist."""
        user = create_test_user("user", "password123")

        from app.core.security import create_access_token

        token = create_access_token(data={"sub": "user"})
        client.cookies.set("access_token", token)

        response = client.delete("/api/v1/notifications")

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "All notifications deleted"

    def test_delete_all_notifications_unauthenticated(
        self, client, test_db, override_get_db
    ):
        """Test deleting notifications without authentication."""
        response = client.delete("/api/v1/notifications")

        assert response.status_code == 401
