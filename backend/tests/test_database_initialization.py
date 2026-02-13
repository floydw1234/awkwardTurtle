"""
Test database initialization - Verify database schema exists with expected tables.
This test validates tables exist after migration.

TDD Approach: After running migrations, tests verify tables exist.
If tables are missing, tests will fail.
"""

import pytest
from sqlalchemy import inspect, create_engine, text
from sqlalchemy.exc import ProgrammingError


POSTGRES_HOST = "localhost"
POSTGRES_PORT = 5432
POSTGRES_USER = "awkward_turtle"
POSTGRES_PASSWORD = "awkward_turtle"
POSTGRES_DB = "awkward_turtle_db"


class TestDatabaseInitialization:
    """Tests to verify database tables are properly initialized."""

    def test_users_table_exists_after_migration(self):
        """Test that users table exists after database migration."""
        pg_url = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
        engine = create_engine(pg_url)

        with engine.connect() as conn:
            try:
                result = conn.execute(text("SELECT * FROM users LIMIT 1"))
                assert result.fetchone() is not None or True
            except ProgrammingError as e:
                pytest.fail(f"users table should exist after migration. Error: {e}")

    def test_messages_table_exists_after_migration(self):
        """Test that messages table exists after database migration."""
        pg_url = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
        engine = create_engine(pg_url)

        with engine.connect() as conn:
            try:
                conn.execute(text("SELECT * FROM messages LIMIT 1"))
            except ProgrammingError as e:
                pytest.fail(f"messages table should exist after migration. Error: {e}")

    def test_notifications_table_exists_after_migration(self):
        """Test that notifications table exists after database migration."""
        pg_url = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
        engine = create_engine(pg_url)

        with engine.connect() as conn:
            try:
                conn.execute(text("SELECT * FROM notifications LIMIT 1"))
            except ProgrammingError as e:
                pytest.fail(f"notifications table should exist after migration. Error: {e}")

    def test_friendships_table_exists_after_migration(self):
        """Test that friendships table exists after database migration."""
        pg_url = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
        engine = create_engine(pg_url)

        with engine.connect() as conn:
            try:
                conn.execute(text("SELECT * FROM friendships LIMIT 1"))
            except ProgrammingError as e:
                pytest.fail(f"friendships table should exist after migration. Error: {e}")
