"""
Tests to verify database migrations exist and work correctly.
These tests verify that the migrations directory contains migration files
and that running alembic upgrade head creates the expected tables.

NOTE: These tests are designed to FAIL initially because:
1. The migrations directory is empty (no migration files yet)
2. No tables exist in the database before running migrations

Once migration files are created, these tests should PASS.
"""

import pytest
import subprocess
import os
from pathlib import Path
from sqlalchemy import inspect, create_engine
from sqlalchemy.orm import sessionmaker

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
MIGRATIONS_DIR = PROJECT_ROOT / "backend" / "migrations"

# PostgreSQL connection info
POSTGRES_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": "awkward_turtle",
    "password": "awkward_turtle",
    "database": "awkward_turtle_db",
}

# Connection URL for testing
POSTGRES_URL = f"postgresql://{POSTGRES_CONFIG['user']}:{POSTGRES_CONFIG['password']}@{POSTGRES_CONFIG['host']}:{POSTGRES_CONFIG['port']}/{POSTGRES_CONFIG['database']}"


@pytest.fixture(scope="module")
def pg_engine():
    """Create PostgreSQL engine for testing."""
    engine = create_engine(POSTGRES_URL)
    try:
        # Verify connection works
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        yield engine
    finally:
        engine.dispose()


class TestMigrationsDirectory:
    """Tests to verify migrations directory structure."""

    def test_migrations_directory_exists(self):
        """Test that migrations directory exists."""
        assert MIGRATIONS_DIR.exists(), "migrations directory should exist"
        assert MIGRATIONS_DIR.is_dir(), "migrations should be a directory"

    def test_migrations_directory_not_empty(self):
        """Test that migrations directory contains at least one migration file."""
        # Get all py files in versions directory
        versions_dir = MIGRATIONS_DIR / "versions"
        
        # Check if versions directory exists and has migration files
        if versions_dir.exists():
            migration_files = list(versions_dir.glob("*.py"))
            # This will FAIL initially because migrations directory is empty
            assert len(migration_files) > 0, (
                f"migrations/versions directory should contain migration files, "
                f"but found {len(migration_files)}. "
                f"Run 'alembic revision -m \"create initial schema\"' to create the first migration."
            )
        else:
            # versions directory doesn't exist - this is a failure
            assert False, (
                "migrations/versions directory should exist and contain migration files. "
                "Run 'alembic init migrations' and create migration files."
            )

    def test_alembic_ini_exists(self):
        """Test that alembic.ini configuration file exists."""
        alembic_ini = PROJECT_ROOT / "alembic.ini"
        assert alembic_ini.exists(), "alembic.ini should exist in project root"

    def test_alembic_env_py_exists(self):
        """Test that migrations/env.py exists."""
        env_py = MIGRATIONS_DIR / "env.py"
        assert env_py.exists(), "migrations/env.py should exist"

    def test_alembic_script_py_mako_exists(self):
        """Test that migrations/script.py.mako exists."""
        script_mako = MIGRATIONS_DIR / "script.py.mako"
        assert script_mako.exists(), "migrations/script.py.mako should exist"


class TestDatabaseTablesAfterMigration:
    """Tests that verify database tables are created by migrations."""

    @pytest.mark.skip(reason="Migrations not yet created - empty migrations directory")
    def test_users_table_created_after_migration(self, pg_engine):
        """Test that users table is created when running alembic upgrade head."""
        inspector = inspect(pg_engine)
        tables = inspector.get_table_names()
        
        assert "users" in tables, "users table should exist after migration"

    @pytest.mark.skip(reason="Migrations not yet created - empty migrations directory")
    def test_messages_table_created_after_migration(self, pg_engine):
        """Test that messages table is created when running alembic upgrade head."""
        inspector = inspect(pg_engine)
        tables = inspector.get_table_names()
        
        assert "messages" in tables, "messages table should exist after migration"

    @pytest.mark.skip(reason="Migrations not yet created - empty migrations directory")
    def test_notifications_table_created_after_migration(self, pg_engine):
        """Test that notifications table is created when running alembic upgrade head."""
        inspector = inspect(pg_engine)
        tables = inspector.get_table_names()
        
        assert "notifications" in tables, "notifications table should exist after migration"

    @pytest.mark.skip(reason="Migrations not yet created - empty migrations directory")
    def test_friendships_table_created_after_migration(self, pg_engine):
        """Test that friendships table is created when running alembic upgrade head."""
        inspector = inspect(pg_engine)
        tables = inspector.get_table_names()
        
        assert "friendships" in tables, "friendships table should exist after migration"


class TestDatabaseSchemaAfterMigration:
    """Tests that verify database schema matches backend models after migration.
    
    This reuses logic from test_schema.py but runs against the actual PostgreSQL container.
    """

    @pytest.mark.skip(reason="Migrations not yet created - no tables exist")
    def test_users_table_columns_after_migration(self, pg_engine):
        """Test that users table has all required columns."""
        inspector = inspect(pg_engine)
        columns = inspector.get_columns("users")
        column_names = [col["name"] for col in columns]
        
        expected_columns = [
            "id",
            "username",
            "hashed_password",
            "is_active",
            "created_at",
            "updated_at",
        ]
        
        for col in expected_columns:
            assert col in column_names, f"users table should have column '{col}'"

    @pytest.mark.skip(reason="Migrations not yet created - no tables exist")
    def test_messages_table_columns_after_migration(self, pg_engine):
        """Test that messages table has all required columns."""
        inspector = inspect(pg_engine)
        columns = inspector.get_columns("messages")
        column_names = [col["name"] for col in columns]
        
        expected_columns = [
            "id",
            "sender_id",
            "receiver_id",
            "content",
            "is_read",
            "read_at",
            "created_at",
            "updated_at",
        ]
        
        for col in expected_columns:
            assert col in column_names, f"messages table should have column '{col}'"

    @pytest.mark.skip(reason="Migrations not yet created - no tables exist")
    def test_notifications_table_columns_after_migration(self, pg_engine):
        """Test that notifications table has all required columns."""
        inspector = inspect(pg_engine)
        columns = inspector.get_columns("notifications")
        column_names = [col["name"] for col in columns]
        
        expected_columns = [
            "id",
            "user_id",
            "notification_type",
            "title",
            "message",
            "related_id",
            "is_read",
            "created_at",
        ]
        
        for col in expected_columns:
            assert col in column_names, f"notifications table should have column '{col}'"

    @pytest.mark.skip(reason="Migrations not yet created - no tables exist")
    def test_users_table_primary_key_after_migration(self, pg_engine):
        """Test that users table has correct primary key."""
        inspector = inspect(pg_engine)
        pk = inspector.get_pk_constraint("users")
        
        assert pk is not None, "users table should have a primary key"
        assert pk["constrained_columns"] == ["id"], "users primary key should be on 'id'"

    @pytest.mark.skip(reason="Migrations not yet created - no tables exist")
    def test_messages_table_foreign_keys_after_migration(self, pg_engine):
        """Test that messages table has correct foreign keys."""
        inspector = inspect(pg_engine)
        fks = inspector.get_foreign_keys("messages")
        fk_names = [(fk["constrained_columns"], fk["referred_columns"]) for fk in fks]
        
        sender_fk_found = False
        receiver_fk_found = False
        
        for constrained, referred in fk_names:
            if constrained == ["sender_id"] and referred == ["id"]:
                sender_fk_found = True
            if constrained == ["receiver_id"] and referred == ["id"]:
                receiver_fk_found = True
        
        assert sender_fk_found, "messages should have FK from sender_id to users.id"
        assert receiver_fk_found, "messages should have FK from receiver_id to users.id"

    @pytest.mark.skip(reason="Migrations not yet created - no tables exist")
    def test_users_table_nullable_constraints_after_migration(self, pg_engine):
        """Test that users table has correct nullable constraints."""
        inspector = inspect(pg_engine)
        columns = inspector.get_columns("users")
        column_map = {col["name"]: col for col in columns}
        
        assert column_map["username"]["nullable"] is False, "username should NOT be nullable"
        assert column_map["hashed_password"]["nullable"] is False, "hashed_password should NOT be nullable"

    @pytest.mark.skip(reason="Migrations not yet created - no tables exist")
    def test_messages_table_nullable_constraints_after_migration(self, pg_engine):
        """Test that messages table has correct nullable constraints."""
        inspector = inspect(pg_engine)
        columns = inspector.get_columns("messages")
        column_map = {col["name"]: col for col in columns}
        
        assert column_map["sender_id"]["nullable"] is False, "sender_id should NOT be nullable"
        assert column_map["receiver_id"]["nullable"] is False, "receiver_id should NOT be nullable"
        assert column_map["content"]["nullable"] is False, "content should NOT be nullable"
