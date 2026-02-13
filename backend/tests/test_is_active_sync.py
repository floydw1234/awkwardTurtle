"""
Tests for is_active field synchronization during authentication events.
This test file verifies the backend actively updates is_active to keep it in sync.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.models import User
from tests.conftest import SyncTestingSessionLocal


class TestIsActiveSync:
    """Tests to verify is_active is actively updated on the backend."""

    def test_registration_sets_is_active_to_true(
        self, client, test_db, override_get_db
    ):
        """Test that registration sets is_active=True for new users."""
        payload = {"username": "newuser", "password": "securepassword123"}

        response = client.post("/api/v1/auth/register", json=payload)

        assert response.status_code == 201

        session = SyncTestingSessionLocal()
        try:
            db_user = session.execute(
                select(User).where(User.username == "newuser")
            ).scalar_one()
            assert db_user.is_active is True, (
                f"Expected is_active=True after registration, got {db_user.is_active}"
            )
        finally:
            session.close()

    def test_login_sets_is_active_to_true(
        self, client, test_db, override_get_db, create_test_user
    ):
        """Test that login sets is_active=True even if user was deactivated."""
        create_test_user("deactivateduser", "testpass123", is_active=False)

        session = SyncTestingSessionLocal()
        try:
            db_user_before = session.execute(
                select(User).where(User.username == "deactivateduser")
            ).scalar_one()
            assert db_user_before.is_active is False, (
                "Prerequisite: user should start as inactive"
            )
        finally:
            session.close()

        payload = {"username": "deactivateduser", "password": "testpass123"}
        response = client.post("/api/v1/auth/login", json=payload)

        assert response.status_code == 200

        session = SyncTestingSessionLocal()
        try:
            db_user_after = session.execute(
                select(User).where(User.username == "deactivateduser")
            ).scalar_one()
            assert db_user_after.is_active is True, (
                f"Expected is_active=True after login, got {db_user_after.is_active}"
            )
        finally:
            session.close()

    def test_logout_sets_is_active_to_false(
        self, client, test_db, override_get_db, create_test_user
    ):
        """Test that logout sets is_active=False."""
        create_test_user("logoutuser", "testpass123", is_active=True)

        session = SyncTestingSessionLocal()
        try:
            db_user_before = session.execute(
                select(User).where(User.username == "logoutuser")
            ).scalar_one()
            assert db_user_before.is_active is True, (
                "Prerequisite: user should start as active"
            )
        finally:
            session.close()

        login_payload = {"username": "logoutuser", "password": "testpass123"}
        client.post("/api/v1/auth/login", json=login_payload)

        response = client.post("/api/v1/auth/logout")

        assert response.status_code == 200

        session = SyncTestingSessionLocal()
        try:
            db_user_after = session.execute(
                select(User).where(User.username == "logoutuser")
            ).scalar_one()
            assert db_user_after.is_active is False, (
                f"Expected is_active=False after logout, got {db_user_after.is_active}"
            )
        finally:
            session.close()

    def test_status_endpoint_can_toggle_is_active(
        self, client, test_db, override_get_db, create_test_user
    ):
        """Test that the status endpoint can toggle is_active field."""
        create_test_user("toggleuser", "testpass123", is_active=True)

        session = SyncTestingSessionLocal()
        try:
            db_user = session.execute(
                select(User).where(User.username == "toggleuser")
            ).scalar_one()
            assert db_user.is_active is True, (
                "Prerequisite: user should start as active"
            )
        finally:
            session.close()

        payload = {"is_active": False}
        response = client.put("/api/v1/users/1/status", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is False

        session = SyncTestingSessionLocal()
        try:
            db_user = session.execute(
                select(User).where(User.username == "toggleuser")
            ).scalar_one()
            assert db_user.is_active is False, (
                f"Expected is_active=False after toggle, got {db_user.is_active}"
            )
        finally:
            session.close()

    def test_status_endpoint_can_activate_user(
        self, client, test_db, override_get_db, create_test_user
    ):
        """Test that the status endpoint can activate a deactivated user."""
        create_test_user("reactivateuser", "testpass123", is_active=False)

        payload = {"is_active": True}
        response = client.put("/api/v1/users/1/status", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is True

        session = SyncTestingSessionLocal()
        try:
            db_user = session.execute(
                select(User).where(User.username == "reactivateuser")
            ).scalar_one()
            assert db_user.is_active is True, (
                f"Expected is_active=True after activation, got {db_user.is_active}"
            )
        finally:
            session.close()
