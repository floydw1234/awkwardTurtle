"""
Tests for authentication endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models import User
from app.core.security import verify_password, get_password_hash

from tests.conftest import SyncTestingSessionLocal


class TestRegisterEndpoint:
    """Tests for POST /api/v1/auth/register endpoint."""

    def test_register_user_success(self, client, test_db, override_get_db):
        """Test successful user registration."""
        payload = {"username": "newuser", "password": "securepassword123"}

        response = client.post("/api/v1/auth/register", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert data["is_active"] is True
        assert "id" in data
        assert "created_at" in data

    def test_register_user_duplicate_username(
        self, client, test_db, override_get_db, create_test_user
    ):
        """Test registration with existing username."""
        # Create existing user
        create_test_user("existinguser", "password123")

        payload = {"username": "existinguser", "password": "newpassword123"}

        response = client.post("/api/v1/auth/register", json=payload)

        assert response.status_code == 400
        assert response.json()["detail"] == "Username already registered"

    def test_register_user_missing_username(self, client, test_db, override_get_db):
        """Test registration with missing username."""
        payload = {"password": "password123"}

        response = client.post("/api/v1/auth/register", json=payload)

        assert response.status_code == 422

    def test_register_user_missing_password(self, client, test_db, override_get_db):
        """Test registration with missing password."""
        payload = {"username": "newuser"}

        response = client.post("/api/v1/auth/register", json=payload)

        assert response.status_code == 422

    def test_register_user_short_password(self, client, test_db, override_get_db):
        """Test registration with password less than 6 characters."""
        payload = {"username": "newuser", "password": "short"}

        response = client.post("/api/v1/auth/register", json=payload)

        assert response.status_code == 422


class TestLoginEndpoint:
    """Tests for POST /api/v1/auth/login endpoint."""

    def test_login_user_success(
        self, client, test_db, override_get_db, create_test_user
    ):
        """Test successful user login."""
        create_test_user("loginuser", "testpass123")

        payload = {"username": "loginuser", "password": "testpass123"}

        response = client.post("/api/v1/auth/login", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Login successful"
        assert data["user"]["username"] == "loginuser"
        assert "access_token" in client.cookies

    def test_login_user_invalid_username(
        self, client, test_db, override_get_db, create_test_user
    ):
        """Test login with non-existent username."""
        create_test_user("existinguser", "password123")

        payload = {"username": "nonexistent", "password": "password123"}

        response = client.post("/api/v1/auth/login", json=payload)

        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid username or password"

    def test_login_user_invalid_password(
        self, client, test_db, override_get_db, create_test_user
    ):
        """Test login with incorrect password."""
        create_test_user("passworduser", "correctpassword")

        payload = {"username": "passworduser", "password": "wrongpassword"}

        response = client.post("/api/v1/auth/login", json=payload)

        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid username or password"

    def test_login_user_sets_cookie(
        self, client, test_db, override_get_db, create_test_user
    ):
        """Test that login sets the access_token cookie."""
        create_test_user("cookietest", "testpass123")

        payload = {"username": "cookietest", "password": "testpass123"}

        response = client.post("/api/v1/auth/login", json=payload)

        assert response.status_code == 200
        assert "access_token" in client.cookies
        cookie = client.cookies["access_token"]
        assert len(cookie) > 0


class TestLogoutEndpoint:
    """Tests for POST /api/v1/auth/logout endpoint."""

    def test_logout_user_success(
        self, client, test_db, override_get_db, create_test_user
    ):
        """Test successful user logout."""
        create_test_user("logoutuser", "testpass123")

        # First login to set cookie
        login_payload = {"username": "logoutuser", "password": "testpass123"}
        client.post("/api/v1/auth/login", json=login_payload)

        # Verify cookie is set
        assert "access_token" in client.cookies

        # Logout
        response = client.post("/api/v1/auth/logout")

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Logged out successfully"

        # Verify cookie is deleted
        assert (
            "access_token" not in client.cookies or client.cookies["access_token"] == ""
        )

    def test_logout_without_login(self, client, test_db, override_get_db):
        """Test logout without being logged in returns 401."""
        response = client.post("/api/v1/auth/logout")

        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Not authenticated"


class TestHealthCheck:
    """Tests for health check endpoint."""

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestRootEndpoint:
    """Tests for root endpoint."""

    def test_root_endpoint(self, client):
        """Test root endpoint returns API info."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert data["version"] == "1.0.0"
        assert "docs" in data


class TestUserIsActiveOnAuthEvents:
    """Tests for is_active field sync during authentication events."""

    def test_login_sets_is_active_to_true(
        self, client, test_db, override_get_db, create_test_user
    ):
        """Test that login sets is_active=True for the user."""
        create_test_user("activeuser", "testpass123", is_active=False)

        payload = {"username": "activeuser", "password": "testpass123"}

        response = client.post("/api/v1/auth/login", json=payload)

        assert response.status_code == 200

        session = SyncTestingSessionLocal()
        try:
            db_user = session.query(User).filter(User.username == "activeuser").first()
            assert db_user.is_active is True
        finally:
            session.close()

    def test_logout_sets_is_active_to_false(
        self, client, test_db, override_get_db, create_test_user
    ):
        """Test that logout sets is_active=False for the user."""
        create_test_user("logoutuser", "testpass123", is_active=True)

        login_payload = {"username": "logoutuser", "password": "testpass123"}
        client.post("/api/v1/auth/login", json=login_payload)

        response = client.post("/api/v1/auth/logout")

        assert response.status_code == 200

        session = SyncTestingSessionLocal()
        try:
            db_user = session.query(User).filter(User.username == "logoutuser").first()
            assert db_user.is_active is False
        finally:
            session.close()
