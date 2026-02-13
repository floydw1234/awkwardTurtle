"""
Tests to verify PostgreSQL database setup and schema.
These tests verify the actual PostgreSQL database (not SQLite) is running
and has the expected tables after migration/schema creation.

Run these tests AFTER:
1. Starting postgres container: docker-compose up -d postgres
2. Running migrations: alembic upgrade head
   OR: Starting the backend (which creates tables on startup)
"""

import pytest
from sqlalchemy import inspect, create_engine, text
from sqlalchemy.orm import sessionmaker

# PostgreSQL connection - same as docker-compose.yml
POSTGRES_HOST = "localhost"
POSTGRES_PORT = 5432
POSTGRES_USER = "awkward_turtle"
POSTGRES_PASSWORD = "awkward_turtle"
POSTGRES_DB = "awkward_turtle_db"

# SQLite for comparison/testing
SYNC_TEST_DB_URL = "sqlite:///./test_awkward_turtle_sync.db"


@pytest.fixture(scope="module")
def pg_engine():
    """Create PostgreSQL engine for schema testing."""
    from sqlalchemy.exc import OperationalError
    
    pg_url = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    
    # Use sync driver for inspection
    sync_pg_url = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    
    engine = create_engine(sync_pg_url)
    
    # Test connection
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        yield engine
    except OperationalError as e:
        pytest.fail(f"Cannot connect to PostgreSQL at {POSTGRES_HOST}:{POSTGRES_PORT}: {e}")
    finally:
        engine.dispose()


class TestPostgreSQLConnection:
    """Tests that verify PostgreSQL is running and accessible."""

    def test_postgres_server_responds(self):
        """Test that PostgreSQL server is reachable."""
        import psycopg2
        
        try:
            conn = psycopg2.connect(
                host=POSTGRES_HOST,
                port=POSTGRES_PORT,
                user=POSTGRES_USER,
                password=POSTGRES_PASSWORD,
                database="postgres",  # Connect to default DB first
            )
            conn.close()
        except psycopg2.OperationalError as e:
            pytest.fail(f"PostgreSQL server at {POSTGRES_HOST}:{POSTGRES_PORT} is not responding: {e}")
        except Exception as e:
            pytest.fail(f"Unexpected error connecting to PostgreSQL: {e}")

    def test_awkward_turtle_database_exists(self, pg_engine):
        """Test that awkward_turtle_db database exists and is accessible."""
        with pg_engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            assert result.scalar() == 1, "Should be able to execute query on awkward_turtle_db"


class TestPostgreSQLSchema:
    """Tests that verify the database schema matches backend models."""

    def test_users_table_exists(self, pg_engine):
        """Test that users table exists in PostgreSQL."""
        inspector = inspect(pg_engine)
        tables = inspector.get_table_names()
        
        assert "users" in tables, "users table should exist in PostgreSQL database"

    def test_messages_table_exists(self, pg_engine):
        """Test that messages table exists in PostgreSQL."""
        inspector = inspect(pg_engine)
        tables = inspector.get_table_names()
        
        assert "messages" in tables, "messages table should exist in PostgreSQL database"

    def test_notifications_table_exists(self, pg_engine):
        """Test that notifications table exists in PostgreSQL."""
        inspector = inspect(pg_engine)
        tables = inspector.get_table_names()
        
        assert "notifications" in tables, "notifications table should exist in PostgreSQL database"

    def test_friendships_table_exists(self, pg_engine):
        """Test that friendships association table exists in PostgreSQL."""
        inspector = inspect(pg_engine)
        tables = inspector.get_table_names()
        
        assert "friendships" in tables, "friendships table should exist in PostgreSQL database"

    def test_users_table_columns(self, pg_engine):
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

    def test_messages_table_columns(self, pg_engine):
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

    def test_notifications_table_columns(self, pg_engine):
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

    def test_users_table_primary_key(self, pg_engine):
        """Test that users table has correct primary key."""
        inspector = inspect(pg_engine)
        pk = inspector.get_pk_constraint("users")
        
        assert pk is not None, "users table should have a primary key"
        assert pk["constrained_columns"] == ["id"], "users primary key should be on 'id' column"

    def test_messages_table_primary_key(self, pg_engine):
        """Test that messages table has correct primary key."""
        inspector = inspect(pg_engine)
        pk = inspector.get_pk_constraint("messages")
        
        assert pk is not None, "messages table should have a primary key"
        assert pk["constrained_columns"] == ["id"], "messages primary key should be on 'id' column"

    def test_notifications_table_primary_key(self, pg_engine):
        """Test that notifications table has correct primary key."""
        inspector = inspect(pg_engine)
        pk = inspector.get_pk_constraint("notifications")
        
        assert pk is not None, "notifications table should have a primary key"
        assert pk["constrained_columns"] == ["id"], "notifications primary key should be on 'id' column"

    def test_users_table_unique_constraint_username(self, pg_engine):
        """Test that users table has unique constraint on username."""
        inspector = inspect(pg_engine)
        constraints = inspector.get_unique_constraints("users")
        constraint_names = [c["name"] for c in constraints]
        
        # Either the constraint exists by name or column is unique
        assert any("username" in str(c.get("column_names", [])) for c in constraints), \
            "users table should have unique constraint on username column"

    def test_users_table_index_username(self, pg_engine):
        """Test that users table has index on username."""
        inspector = inspect(pg_engine)
        indexes = inspector.get_indexes("users")
        index_names = [idx["name"] for idx in indexes]
        
        assert "ix_users_username" in index_names, "users table should have index on username"

    def test_messages_table_foreign_keys(self, pg_engine):
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
        
        assert sender_fk_found, "messages table should have foreign key from sender_id to users.id"
        assert receiver_fk_found, "messages table should have foreign key from receiver_id to users.id"

    def test_notifications_table_foreign_key(self, pg_engine):
        """Test that notifications table has correct foreign key."""
        inspector = inspect(pg_engine)
        fks = inspector.get_foreign_keys("notifications")
        fk_names = [(fk["constrained_columns"], fk["referred_columns"]) for fk in fks]
        
        user_fk_found = False
        
        for constrained, referred in fk_names:
            if constrained == ["user_id"] and referred == ["id"]:
                user_fk_found = True
        
        assert user_fk_found, "notifications table should have foreign key from user_id to users.id"

    def test_friendships_table_columns(self, pg_engine):
        """Test that friendships table has correct columns."""
        inspector = inspect(pg_engine)
        columns = inspector.get_columns("friendships")
        column_names = [col["name"] for col in columns]
        
        assert "user_id" in column_names, "friendships table should have user_id column"
        assert "friend_id" in column_names, "friendships table should have friend_id column"

    def test_friendships_table_primary_key_composite(self, pg_engine):
        """Test that friendships table has composite primary key."""
        inspector = inspect(pg_engine)
        pk = inspector.get_pk_constraint("friendships")
        
        pk_columns = pk["constrained_columns"]
        assert len(pk_columns) == 2, "friendships table should have composite primary key"
        assert "user_id" in pk_columns, "friendships primary key should include user_id"
        assert "friend_id" in pk_columns, "friendships primary key should include friend_id"

    def test_friendships_table_foreign_keys(self, pg_engine):
        """Test that friendships table has correct foreign keys."""
        inspector = inspect(pg_engine)
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

    def test_users_table_nullable_constraints(self, pg_engine):
        """Test that users table has correct nullable constraints."""
        inspector = inspect(pg_engine)
        columns = inspector.get_columns("users")
        column_map = {col["name"]: col for col in columns}
        
        assert column_map["username"]["nullable"] is False, "username should NOT be nullable"
        assert column_map["hashed_password"]["nullable"] is False, "hashed_password should NOT be nullable"
        assert column_map["is_active"]["nullable"] is True, "is_active should be nullable (has default)"
        assert column_map["created_at"]["nullable"] is True, "created_at should be nullable (has default)"
        assert column_map["updated_at"]["nullable"] is True, "updated_at should be nullable (has default)"

    def test_messages_table_nullable_constraints(self, pg_engine):
        """Test that messages table has correct nullable constraints."""
        inspector = inspect(pg_engine)
        columns = inspector.get_columns("messages")
        column_map = {col["name"]: col for col in columns}
        
        assert column_map["sender_id"]["nullable"] is False, "sender_id should NOT be nullable"
        assert column_map["receiver_id"]["nullable"] is False, "receiver_id should NOT be nullable"
        assert column_map["content"]["nullable"] is False, "content should NOT be nullable"
        assert column_map["is_read"]["nullable"] is True, "is_read should be nullable (has default)"
        assert column_map["read_at"]["nullable"] is True, "read_at should be nullable (can be None)"

    def test_notifications_table_nullable_constraints(self, pg_engine):
        """Test that notifications table has correct nullable constraints."""
        inspector = inspect(pg_engine)
        columns = inspector.get_columns("notifications")
        column_map = {col["name"]: col for col in columns}
        
        assert column_map["user_id"]["nullable"] is False, "user_id should NOT be nullable"
        assert column_map["notification_type"]["nullable"] is False, "notification_type should NOT be nullable"
        assert column_map["title"]["nullable"] is False, "title should NOT be nullable"
        assert column_map["message"]["nullable"] is True, "message should be nullable"
        assert column_map["related_id"]["nullable"] is True, "related_id should be nullable"
