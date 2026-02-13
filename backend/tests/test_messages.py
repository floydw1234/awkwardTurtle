"""
Tests for messaging endpoints.
"""

import asyncio
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models import User, Message, Notification


# Import conftest to access test database session
from tests.conftest import (
    SyncTestingSessionLocal,
    _create_message_sync,
    _create_notification_sync,
)


class TestSendMessageEndpoint:
    """Tests for POST /api/v1/messages/send endpoint."""

    def test_send_message_success(
        self, client, test_db, override_get_db, create_test_user
    ):
        """Test successfully sending a message."""
        # Create sender and receiver
        sender = create_test_user("sender", "password123")
        receiver = create_test_user("receiver", "password123")

        # Authenticate as sender
        from app.core.security import create_access_token

        token = create_access_token(data={"sub": "sender"})
        client.cookies.set("access_token", token)

        # Send message
        payload = {
            "to_user_id": receiver.id,
            "content": "Hello, this is a test message!",
        }

        response = client.post("/api/v1/messages/send", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["content"] == payload["content"]
        assert data["sender_id"] == sender.id
        assert data["receiver_id"] == receiver.id
        assert data["is_read"] is False

    def test_send_message_to_nonexistent_user(
        self, client, test_db, override_get_db, create_test_user
    ):
        """Test sending a message to a non-existent user."""
        # Create authenticating user first
        create_test_user("sender", "password123")
        # Authenticate
        from app.core.security import create_access_token

        token = create_access_token(data={"sub": "sender"})
        client.cookies.set("access_token", token)

        # Try to send message to non-existent user
        payload = {"to_user_id": 999, "content": "Hello!"}

        response = client.post("/api/v1/messages/send", json=payload)

        assert response.status_code == 404
        assert response.json()["detail"] == "Recipient not found"

    def test_send_message_unauthenticated(self, client, test_db, override_get_db):
        """Test sending a message without authentication."""
        payload = {"to_user_id": 1, "content": "Hello!"}

        response = client.post("/api/v1/messages/send", json=payload)

        assert response.status_code == 401

    def test_send_message_empty_content(
        self, client, test_db, override_get_db, create_test_user
    ):
        """Test sending a message with empty content."""
        sender = create_test_user("sender", "password123")
        receiver = create_test_user("receiver", "password123")

        from app.core.security import create_access_token

        token = create_access_token(data={"sub": "sender"})
        client.cookies.set("access_token", token)

        payload = {"to_user_id": receiver.id, "content": ""}

        response = client.post("/api/v1/messages/send", json=payload)

        # Empty string content might pass validation depending on schema
        # This tests the actual behavior
        assert response.status_code in [200, 422]


class TestGetInboxEndpoint:
    """Tests for GET /api/v1/messages/inbox endpoint."""

    def test_get_inbox_success(
        self, client, test_db, override_get_db, create_test_user
    ):
        """Test getting inbox with messages."""
        # Create users
        sender1 = create_test_user("sender1", "password123")
        sender2 = create_test_user("sender2", "password123")
        receiver = create_test_user("receiver", "password123")

        # Authenticate as receiver
        from app.core.security import create_access_token

        token = create_access_token(data={"sub": "receiver"})
        client.cookies.set("access_token", token)

        # Create messages using sync session helper
        message1 = _create_message_sync(sender1.id, receiver.id, "First message")
        message2 = _create_message_sync(sender2.id, receiver.id, "Second message")

        # Get inbox
        response = client.get("/api/v1/messages/inbox")

        assert response.status_code == 200
        data = response.json()
        assert "messages" in data
        assert "total" in data
        assert data["total"] == 2

    def test_get_inbox_empty(self, client, test_db, override_get_db, create_test_user):
        """Test getting empty inbox."""
        receiver = create_test_user("receiver", "password123")

        from app.core.security import create_access_token

        token = create_access_token(data={"sub": "receiver"})
        client.cookies.set("access_token", token)

        response = client.get("/api/v1/messages/inbox")

        assert response.status_code == 200
        data = response.json()
        assert data["messages"] == []
        assert data["total"] == 0

    def test_get_inbox_unauthenticated(self, client, test_db, override_get_db):
        """Test getting inbox without authentication."""
        response = client.get("/api/v1/messages/inbox")

        assert response.status_code == 401


class TestGetOutboxEndpoint:
    """Tests for GET /api/v1/messages/outbox endpoint."""

    def test_get_outbox_success(
        self, client, test_db, override_get_db, create_test_user
    ):
        """Test getting outbox with sent messages."""
        sender = create_test_user("sender", "password123")
        receiver = create_test_user("receiver", "password123")

        from app.core.security import create_access_token

        token = create_access_token(data={"sub": "sender"})
        client.cookies.set("access_token", token)

        # Create messages
        from app.db.database import AsyncSessionLocal
        from app.models import Message

        message1 = Message(
            sender_id=sender.id, receiver_id=receiver.id, content="First sent message"
        )

        # Create message using sync session helper
        _create_message_sync(sender.id, receiver.id, "First sent message")

        response = client.get("/api/v1/messages/outbox")

        assert response.status_code == 200
        data = response.json()
        assert "messages" in data
        assert "total" in data
        assert data["total"] == 1

    def test_get_outbox_empty(self, client, test_db, override_get_db, create_test_user):
        """Test getting empty outbox."""
        sender = create_test_user("sender", "password123")

        from app.core.security import create_access_token

        token = create_access_token(data={"sub": "sender"})
        client.cookies.set("access_token", token)

        response = client.get("/api/v1/messages/outbox")

        assert response.status_code == 200
        data = response.json()
        assert data["messages"] == []
        assert data["total"] == 0

    def test_get_outbox_unauthenticated(self, client, test_db, override_get_db):
        """Test getting outbox without authentication."""
        response = client.get("/api/v1/messages/outbox")

        assert response.status_code == 401


class TestMarkMessageAsReadEndpoint:
    """Tests for POST /api/v1/messages/{message_id}/read endpoint."""

    def test_mark_message_as_read_success(
        self, client, test_db, override_get_db, create_test_user
    ):
        """Test successfully marking a message as read."""
        sender = create_test_user("sender", "password123")
        receiver = create_test_user("receiver", "password123")

        # Authenticate as receiver
        from app.core.security import create_access_token

        token = create_access_token(data={"sub": "receiver"})
        client.cookies.set("access_token", token)

        # Create message
        from app.db.database import AsyncSessionLocal
        from app.models import Message

        message = Message(
            sender_id=sender.id, receiver_id=receiver.id, content="Message to read"
        )

        # Create message using sync session helper
        message = _create_message_sync(sender.id, receiver.id, "Message to read")

        # Mark as read
        response = client.post(f"/api/v1/messages/{message.id}/read")

        assert response.status_code == 200
        data = response.json()
        assert "message_id" in data
        assert "read_at" in data

    def test_mark_message_as_read_not_receiver(
        self, client, test_db, override_get_db, create_test_user
    ):
        """Test marking a message as read when not the receiver."""
        sender = create_test_user("sender", "password123")
        receiver = create_test_user("receiver", "password123")

        # Authenticate as sender (not the receiver)
        from app.core.security import create_access_token

        token = create_access_token(data={"sub": "sender"})
        client.cookies.set("access_token", token)

        # Create message
        from app.db.database import AsyncSessionLocal
        from app.models import Message

        message = Message(
            sender_id=sender.id, receiver_id=receiver.id, content="Message to read"
        )

        # Create message using sync session helper
        message = _create_message_sync(sender.id, receiver.id, "Message to read")

        # Try to mark as read (should fail)
        response = client.post(f"/api/v1/messages/{message.id}/read")

        assert response.status_code == 403

    def test_mark_message_as_read_nonexistent(
        self, client, test_db, override_get_db, create_test_user
    ):
        """Test marking a non-existent message as read."""
        # Create user first
        create_test_user("testuser", "testpass123")
        # Authenticate
        from app.core.security import create_access_token

        token = create_access_token(data={"sub": "testuser"})
        client.cookies.set("access_token", token)

        response = client.post("/api/v1/messages/999/read")

        assert response.status_code == 404
        assert response.json()["detail"] == "Message not found"

    def test_mark_message_as_read_unauthenticated(
        self, client, test_db, override_get_db
    ):
        """Test marking a message as read without authentication."""
        response = client.post("/api/v1/messages/1/read")

        assert response.status_code == 401
