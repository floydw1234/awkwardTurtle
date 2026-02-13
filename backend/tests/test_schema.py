"""
Tests for database schema validation.
Verifies that the database schema matches the FastAPI backend models.
"""

import pytest
from sqlalchemy import inspect, create_engine

from app.models import Base

SYNC_TEST_DB_URL = "sqlite:///./test_awkward_turtle_sync.db"

sync_test_engine = create_engine(
    SYNC_TEST_DB_URL,
    connect_args={"check_same_thread": False},
)


class TestDatabaseSchema:
    """Tests to verify database schema matches backend models."""

    @pytest.fixture(scope="class")
    def test_schema_db(self):
        """Create a fresh database schema for schema tests."""
        Base.metadata.create_all(bind=sync_test_engine)
        yield sync_test_engine
        Base.metadata.drop_all(bind=sync_test_engine)

    def test_users_table_exists(self, test_schema_db):
        """Test that users table exists in database."""
        inspector = inspect(test_schema_db)
        tables = inspector.get_table_names()
        
        assert "users" in tables, "users table should exist in database"

    def test_messages_table_exists(self, test_schema_db):
        """Test that messages table exists in database."""
        inspector = inspect(test_schema_db)
        tables = inspector.get_table_names()
        
        assert "messages" in tables, "messages table should exist in database"

    def test_notifications_table_exists(self, test_schema_db):
        """Test that notifications table exists in database."""
        inspector = inspect(test_schema_db)
        tables = inspector.get_table_names()
        
        assert "notifications" in tables, "notifications table should exist in database"

    def test_friendships_table_exists(self, test_schema_db):
        """Test that friendships association table exists in database."""
        inspector = inspect(test_schema_db)
        tables = inspector.get_table_names()
        
        assert "friendships" in tables, "friendships table should exist in database"

    def test_users_table_columns(self, test_schema_db):
        """Test that users table has all required columns matching User model."""
        inspector = inspect(test_schema_db)
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

    def test_messages_table_columns(self, test_schema_db):
        """Test that messages table has all required columns matching Message model."""
        inspector = inspect(test_schema_db)
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

    def test_notifications_table_columns(self, test_schema_db):
        """Test that notifications table has all required columns matching Notification model."""
        inspector = inspect(test_schema_db)
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

    def test_users_table_primary_key(self, test_schema_db):
        """Test that users table has correct primary key."""
        inspector = inspect(test_schema_db)
        pk = inspector.get_pk_constraint("users")
        
        assert pk["name"] == "users_pkey", "users table should have primary key 'users_pkey'"
        assert pk["constrained_columns"] == ["id"], "users primary key should be on 'id' column"

    def test_messages_table_primary_key(self, test_schema_db):
        """Test that messages table has correct primary key."""
        inspector = inspect(test_schema_db)
        pk = inspector.get_pk_constraint("messages")
        
        assert pk["name"] == "messages_pkey", "messages table should have primary key 'messages_pkey'"
        assert pk["constrained_columns"] == ["id"], "messages primary key should be on 'id' column"

    def test_notifications_table_primary_key(self, test_schema_db):
        """Test that notifications table has correct primary key."""
        inspector = inspect(test_schema_db)
        pk = inspector.get_pk_constraint("notifications")
        
        assert pk["name"] == "notifications_pkey", "notifications table should have primary key 'notifications_pkey'"
        assert pk["constrained_columns"] == ["id"], "notifications primary key should be on 'id' column"

    def test_users_table_unique_constraint_username(self, test_schema_db):
        """Test that users table has unique constraint on username."""
        inspector = inspect(test_schema_db)
        constraints = inspector.get_unique_constraints("users")
        constraint_names = [c["name"] for c in constraints]
        
        assert "ix_users_username" in constraint_names or any(
            "username" in str(c.get("column_names", [])) for c in constraints
        ), "users table should have unique constraint on username"

    def test_users_table_index_username(self, test_schema_db):
        """Test that users table has index on username."""
        inspector = inspect(test_schema_db)
        indexes = inspector.get_indexes("users")
        index_names = [idx["name"] for idx in indexes]
        
        assert "ix_users_username" in index_names, "users table should have index on username"

    def test_messages_table_foreign_keys(self, test_schema_db):
        """Test that messages table has correct foreign keys."""
        inspector = inspect(test_schema_db)
        fks = inspector.get_foreign_keys("messages")
        fk_names = [(fk["constrained_columns"], fk["referred_columns"]) for fk in fks]
        
        sender_fk_found = False
        receiver_fk_found = False
        
        for constrained, referred in fk_names:
            if constrained == ["sender_id"] and referred == ["id"]:
                sender_fk_found = True
            if constrained == ["receiver_id"] and referred == ["id"]:
                receiver_fk_found = True
        
        assert sender_fk_found, "messages table should have foreign key from sender_id to users.id"
        assert receiver_fk_found, "messages table should have foreign key from receiver_id to users.id"

    def test_notifications_table_foreign_key(self, test_schema_db):
        """Test that notifications table has correct foreign key."""
        inspector = inspect(test_schema_db)
        fks = inspector.get_foreign_keys("notifications")
        fk_names = [(fk["constrained_columns"], fk["referred_columns"]) for fk in fks]
        
        user_fk_found = False
        
        for constrained, referred in fk_names:
            if constrained == ["user_id"] and referred == ["id"]:
                user_fk_found = True
        
        assert user_fk_found, "notifications table should have foreign key from user_id to users.id"

    def test_friendships_table_columns(self, test_schema_db):
        """Test that friendships table has correct columns for many-to-many relationship."""
        inspector = inspect(test_schema_db)
        columns = inspector.get_columns("friendships")
        column_names = [col["name"] for col in columns]
        
        assert "user_id" in column_names, "friendships table should have user_id column"
        assert "friend_id" in column_names, "friendships table should have friend_id column"

    def test_friendships_table_primary_key_composite(self, test_schema_db):
        """Test that friendships table has composite primary key."""
        inspector = inspect(test_schema_db)
        pk = inspector.get_pk_constraint("friendships")
        
        pk_columns = pk["constrained_columns"]
        assert len(pk_columns) == 2, "friendships table should have composite primary key"
        assert "user_id" in pk_columns, "friendships primary key should include user_id"
        assert "friend_id" in pk_columns, "friendships primary key should include friend_id"

    def test_friendships_table_foreign_keys(self, test_schema_db):
        """Test that friendships table has correct foreign keys for both columns."""
        inspector = inspect(test_schema_db)
        fks = inspector.get_foreign_keys("friendships")
        fk_names = [(fk["constrained_columns"], fk["referred_columns"]) for fk in fks]
        
        user_fk_found = False
        friend_fk_found = False
        
        for constrained, referred in fk_names:
            if constrained == ["user_id"] and referred == ["id"]:
                user_fk_found = True
            if constrained == ["friend_id"] and referred == ["id"]:
                friend_fk_found = True
        
        assert user_fk_found, "friendships table should have foreign key from user_id to users.id"
        assert friend_fk_found, "friendships table should have foreign key from friend_id to users.id"

    def test_users_table_nullable_constraints(self, test_schema_db):
        """Test that users table has correct nullable constraints."""
        inspector = inspect(test_schema_db)
        columns = inspector.get_columns("users")
        column_map = {col["name"]: col for col in columns}
        
        assert column_map["username"]["nullable"] is False, "username column should not be nullable"
        assert column_map["hashed_password"]["nullable"] is False, "hashed_password column should not be nullable"
        assert column_map["is_active"]["nullable"] is True, "is_active column should be nullable (has default)"
        assert column_map["created_at"]["nullable"] is True, "created_at column should be nullable (has default)"
        assert column_map["updated_at"]["nullable"] is True, "updated_at column should be nullable (has default)"

    def test_messages_table_nullable_constraints(self, test_schema_db):
        """Test that messages table has correct nullable constraints."""
        inspector = inspect(test_schema_db)
        columns = inspector.get_columns("messages")
        column_map = {col["name"]: col for col in columns}
        
        assert column_map["sender_id"]["nullable"] is False, "sender_id should not be nullable"
        assert column_map["receiver_id"]["nullable"] is False, "receiver_id should not be nullable"
        assert column_map["content"]["nullable"] is False, "content should not be nullable"
        assert column_map["is_read"]["nullable"] is True, "is_read should be nullable (has default)"
        assert column_map["read_at"]["nullable"] is True, "read_at should be nullable (can be None)"

    def test_notifications_table_nullable_constraints(self, test_schema_db):
        """Test that notifications table has correct nullable constraints."""
        inspector = inspect(test_schema_db)
        columns = inspector.get_columns("notifications")
        column_map = {col["name"]: col for col in columns}
        
        assert column_map["user_id"]["nullable"] is False, "user_id should not be nullable"
        assert column_map["notification_type"]["nullable"] is False, "notification_type should not be nullable"
        assert column_map["title"]["nullable"] is False, "title should not be nullable"
        assert column_map["message"]["nullable"] is True, "message should be nullable"
        assert column_map["related_id"]["nullable"] is True, "related_id should be nullable"
