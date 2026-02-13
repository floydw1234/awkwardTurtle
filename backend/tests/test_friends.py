"""
Tests for friend management endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models import User


class TestAddFriendEndpoint:
    """Tests for POST /api/v1/friends/add/{username} endpoint."""

    def test_add_friend_success(self, client, test_db, override_get_db, create_test_user):
        """Test successfully adding a friend."""
        # Create two users
        user1 = create_test_user("user1", "password123")
        user2 = create_test_user("user2", "password123")

        # Authenticate as user1
        from app.core.security import create_access_token
        token = create_access_token(data={"sub": "user1"})
        client.cookies.set("access_token", token)

        # Add user2 as friend
        response = client.post("/api/v1/friends/add/user2")

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Added 'user2' as friend"

    def test_add_friend_self(self, client, test_db, override_get_db, create_test_user):
        """Test adding self as friend."""
        create_test_user("selfuser", "password123")

        # Authenticate as selfuser
        from app.core.security import create_access_token
        token = create_access_token(data={"sub": "selfuser"})
        client.cookies.set("access_token", token)

        # Try to add self
        response = client.post("/api/v1/friends/add/selfuser")

        assert response.status_code == 400
        assert response.json()["detail"] == "You cannot add yourself as a friend"

    def test_add_friend_nonexistent_user(self, client, test_db, override_get_db, create_test_user):
        """Test adding a non-existent user as friend."""
        # Create authenticating user first
        create_test_user("someuser", "password123")
        # Authenticate
        from app.core.security import create_access_token
        token = create_access_token(data={"sub": "someuser"})
        client.cookies.set("access_token", token)

        # Try to add non-existent user
        response = client.post("/api/v1/friends/add/nonexistent")

        assert response.status_code == 404
        assert "User 'nonexistent' not found" in response.json()["detail"]

    def test_add_friend_already_added(self, client, test_db, override_get_db, create_test_user):
        """Test adding a user who is already a friend."""
        # Create two users
        user1 = create_test_user("user1", "password123")
        user2 = create_test_user("user2", "password123")

        # Authenticate as user1
        from app.core.security import create_access_token
        token = create_access_token(data={"sub": "user1"})
        client.cookies.set("access_token", token)

        # First add
        client.post("/api/v1/friends/add/user2")

        # Try to add again
        response = client.post("/api/v1/friends/add/user2")

        assert response.status_code == 400
        assert response.json()["detail"] == "User 'user2' is already your friend"

    def test_add_friend_unauthenticated(self, client, test_db, override_get_db):
        """Test adding a friend without authentication."""
        response = client.post("/api/v1/friends/add/someuser")

        assert response.status_code == 401


class TestRemoveFriendEndpoint:
    """Tests for POST /api/v1/friends/remove/{username} endpoint."""

    def test_remove_friend_success(self, client, test_db, override_get_db, create_test_user):
        """Test successfully removing a friend."""
        # Create two users and add them as friends
        user1 = create_test_user("user1", "password123")
        user2 = create_test_user("user2", "password123")

        # Authenticate as user1
        from app.core.security import create_access_token
        token = create_access_token(data={"sub": "user1"})
        client.cookies.set("access_token", token)

        # Add friend first
        client.post("/api/v1/friends/add/user2")

        # Remove friend
        response = client.post("/api/v1/friends/remove/user2")

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == f"Removed 'user2' from friends"

    def test_remove_friend_not_friends(self, client, test_db, override_get_db, create_test_user):
        """Test removing a user who is not a friend."""
        # Create two users
        user1 = create_test_user("user1", "password123")
        user2 = create_test_user("user2", "password123")

        # Authenticate as user1
        from app.core.security import create_access_token
        token = create_access_token(data={"sub": "user1"})
        client.cookies.set("access_token", token)

        # Try to remove without being friends
        response = client.post("/api/v1/friends/remove/user2")

        assert response.status_code == 400
        assert response.json()["detail"] == "User 'user2' is not your friend"

    def test_remove_friend_nonexistent_user(self, client, test_db, override_get_db, create_test_user):
        """Test removing a non-existent user."""
        # Create authenticating user first
        create_test_user("someuser", "password123")
        # Authenticate
        from app.core.security import create_access_token
        token = create_access_token(data={"sub": "someuser"})
        client.cookies.set("access_token", token)

        # Try to remove non-existent user
        response = client.post("/api/v1/friends/remove/nonexistent")

        assert response.status_code == 404
        assert "User 'nonexistent' not found" in response.json()["detail"]

    def test_remove_friend_unauthenticated(self, client, test_db, override_get_db):
        """Test removing a friend without authentication."""
        response = client.post("/api/v1/friends/remove/someuser")

        assert response.status_code == 401


class TestGetFriendsEndpoint:
    """Tests for GET /api/v1/friends endpoint."""

    def test_get_friends_success(self, client, test_db, override_get_db, create_test_user):
        """Test getting list of friends."""
        # Create users
        user1 = create_test_user("user1", "password123")
        user2 = create_test_user("user2", "password123")
        user3 = create_test_user("user3", "password123")

        # Authenticate as user1
        from app.core.security import create_access_token
        token = create_access_token(data={"sub": "user1"})
        client.cookies.set("access_token", token)

        # Add some friends
        client.post("/api/v1/friends/add/user2")
        client.post("/api/v1/friends/add/user3")

        # Get friends list
        response = client.get("/api/v1/friends")

        assert response.status_code == 200
        data = response.json()
        assert "friends" in data
        assert "total" in data
        assert data["total"] == 2
        assert "user2" in data["friends"]
        assert "user3" in data["friends"]

    def test_get_friends_empty(self, client, test_db, override_get_db, create_test_user):
        """Test getting friends list when no friends."""
        create_test_user("nofriends", "password123")

        # Authenticate
        from app.core.security import create_access_token
        token = create_access_token(data={"sub": "nofriends"})
        client.cookies.set("access_token", token)

        # Get friends list
        response = client.get("/api/v1/friends")

        assert response.status_code == 200
        data = response.json()
        assert data["friends"] == []
        assert data["total"] == 0

    def test_get_friends_unauthenticated(self, client, test_db, override_get_db):
        """Test getting friends list without authentication."""
        response = client.get("/api/v1/friends")

        assert response.status_code == 401
