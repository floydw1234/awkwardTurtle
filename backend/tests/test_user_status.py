"""
Tests for user status management (is_active field).
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models import User


class TestUserStatusEndpoint:
    """Tests for PUT /api/v1/users/{user_id}/status endpoint."""

    def test_update_user_status_activate(
        self, client, test_db, override_get_db, create_test_user
    ):
        """Test activating a deactivated user."""
        create_test_user("inactiveuser", "password123")

        payload = {"is_active": True}

        response = client.put("/api/v1/users/1/status", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is True

    def test_update_user_status_deactivate(
        self, client, test_db, override_get_db, create_test_user
    ):
        """Test deactivating an active user."""
        create_test_user("activeuser", "password123")

        payload = {"is_active": False}

        response = client.put("/api/v1/users/1/status", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is False

    def test_update_user_status_user_not_found(self, client, test_db, override_get_db):
        """Test updating status for non-existent user."""
        payload = {"is_active": False}

        response = client.put("/api/v1/users/999/status", json=payload)

        assert response.status_code == 404
        assert "detail" in response.json()

    def test_update_user_status_invalid_value(
        self, client, test_db, override_get_db, create_test_user
    ):
        """Test updating status with invalid value."""
        create_test_user("testuser", "password123")

        payload = {"is_active": "invalid"}

        response = client.put("/api/v1/users/1/status", json=payload)

        assert response.status_code == 422

    def test_update_user_status_missing_field(
        self, client, test_db, override_get_db, create_test_user
    ):
        """Test updating status without providing is_active field."""
        create_test_user("testuser", "password123")

        payload = {}

        response = client.put("/api/v1/users/1/status", json=payload)

        assert response.status_code == 422
