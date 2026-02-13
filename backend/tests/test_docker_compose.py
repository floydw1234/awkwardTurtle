"""
Tests to verify docker-compose setup and container configuration.
These tests verify that docker-compose.yml and Dockerfile are properly configured
and that services can be started successfully.

NOTE: These tests require Docker to be running and the backend/.env file to be present.
They should be run AFTER: docker-compose up -d

TODO: The backend service currently doesn't mount the .env file, so it won't have
access to the DATABASE_URL. This needs to be fixed in docker-compose.yml.
"""

import pytest
import subprocess
import time
from pathlib import Path


# Project root path
PROJECT_ROOT = Path(__file__).parent.parent.parent


class TestDockerComposeConfiguration:
    """Tests to verify docker-compose.yml and Dockerfile are properly configured."""

    def test_docker_compose_file_exists(self):
        """Test that docker-compose.yml file exists in project root."""
        docker_compose_path = PROJECT_ROOT / "docker-compose.yml"
        assert docker_compose_path.exists(), "docker-compose.yml should exist in project root"

    def test_backend_dockerfile_exists(self):
        """Test that Dockerfile exists in backend directory."""
        dockerfile_path = PROJECT_ROOT / "backend" / "Dockerfile"
        assert dockerfile_path.exists(), "Dockerfile should exist in backend directory"

    def test_backend_env_file_exists(self):
        """Test that .env file exists in backend directory."""
        env_path = PROJECT_ROOT / "backend" / ".env"
        assert env_path.exists(), ".env file should exist in backend directory"

    def test_docker_compose_has_postgres_service(self):
        """Test that docker-compose.yml defines the postgres service."""
        docker_compose_path = PROJECT_ROOT / "docker-compose.yml"
        content = docker_compose_path.read_text()
        assert "postgres:" in content, "docker-compose.yml should define postgres service"

    def test_docker_compose_has_backend_service(self):
        """Test that docker-compose.yml defines the backend service."""
        docker_compose_path = PROJECT_ROOT / "docker-compose.yml"
        content = docker_compose_path.read_text()
        assert "backend:" in content, "docker-compose.yml should define backend service"

    def test_postgres_service_has_correct_env_vars(self):
        """Test that postgres service has correct environment variables."""
        docker_compose_path = PROJECT_ROOT / "docker-compose.yml"
        content = docker_compose_path.read_text()
        
        assert "POSTGRES_USER:" in content, "postgres service should define POSTGRES_USER"
        assert "POSTGRES_PASSWORD:" in content, "postgres service should define POSTGRES_PASSWORD"
        assert "POSTGRES_DB:" in content, "postgres service should define POSTGRES_DB"

    def test_postgres_service_exposes_port_5432(self):
        """Test that postgres service exposes port 5432."""
        docker_compose_path = PROJECT_ROOT / "docker-compose.yml"
        content = docker_compose_path.read_text()
        
        assert "5432:5432" in content, "postgres service should expose port 5432"

    def test_backend_service_builds_from_dockerfile(self):
        """Test that backend service builds from Dockerfile."""
        docker_compose_path = PROJECT_ROOT / "docker-compose.yml"
        content = docker_compose_path.read_text()
        
        assert "Dockerfile" in content, "backend service should specify Dockerfile"
        assert "./backend" in content, "backend service should use ./backend context"

    def test_backend_service_exposes_port_8050(self):
        """Test that backend service exposes port 8050."""
        docker_compose_path = PROJECT_ROOT / "docker-compose.yml"
        content = docker_compose_path.read_text()
        
        assert "8050:8050" in content, "backend service should expose port 8050"

    def test_backend_depends_on_postgres(self):
        """Test that backend service depends on postgres."""
        docker_compose_path = PROJECT_ROOT / "docker-compose.yml"
        content = docker_compose_path.read_text()
        
        assert "depends_on:" in content, "backend service should depend_on postgres"
        assert "postgres:" in content, "postgres should be listed as dependency"


class TestDockerComposeStartup:
    """Tests to verify docker-compose can start services successfully.
    
    NOTE: These tests require Docker to be running and will only pass
    after running: docker-compose up -d
    """

    @pytest.fixture(scope="class")
    def docker_compose_up(self):
        """Start docker-compose services (class-scoped for sharing)."""
        # This fixture would run: docker-compose up -d
        # We skip it to avoid actually running it during test discovery
        pass

    @pytest.mark.skip(reason="Docker not available or services not running")
    def test_docker_compose_up_starts_both_services(self, docker_compose_up):
        """Test that docker-compose up -d starts both postgres and backend services."""
        # This test would:
        # 1. Run: docker-compose up -d
        # 2. Wait for services to be healthy
        # 3. Verify both containers are running
        # 4. Verify postgres is healthy
        
        # For now: skipped because services aren't running
        assert False, "docker-compose up -d not yet executed"

    @pytest.mark.skip(reason="Docker not available or services not running")
    def test_postgres_container_is_healthy(self, docker_compose_up):
        """Test that postgres container is healthy after startup."""
        # This test would check: docker ps | grep awkward_turtle_postgres
        # and verify HEALTH status is healthy
        
        assert False, "postgres container not yet started"

    @pytest.mark.skip(reason="Docker not available or services not running")
    def test_backend_container_is_running(self, docker_compose_up):
        """Test that backend container is running after startup."""
        # This test would check: docker ps | grep awkward_turtle_backend
        
        assert False, "backend container not yet started"


class TestPostgreSQLAfterDockerStartup:
    """Tests to verify PostgreSQL database is accessible after docker-compose startup.
    
    These tests verify that:
    1. The awkward_turtle_db database exists
    2. The awkward_turtle user can connect
    3. The expected tables are created by the backend (on startup or migration)
    """

    @pytest.fixture(scope="class")
    def postgres_connection_info(self):
        """Get PostgreSQL connection info from docker-compose."""
        return {
            "host": "localhost",
            "port": 5432,
            "user": "awkward_turtle",
            "password": "awkward_turtle",
            "database": "awkward_turtle_db",
        }

    @pytest.mark.skip(reason="Docker not available or services not running")
    def test_awkward_turtle_db_exists_after_startup(self, docker_compose_up, postgres_connection_info):
        """Test that awkward_turtle_db database is accessible after docker-compose startup."""
        import psycopg2
        
        # This test would connect to PostgreSQL and verify the database exists
        # After docker-compose up -d, the POSTGRES_DB environment variable
        # should have created the awkward_turtle_db database
        
        conn = psycopg2.connect(**postgres_connection_info)
        assert conn is not None, "Should be able to connect to awkward_turtle_db"
        conn.close()

    @pytest.mark.skip(reason="Docker not available or services not running")
    def test_expected_tables_exist_after_backend_starts(self, docker_compose_up, postgres_connection_info):
        """Test that backend creates expected tables after starting up.
        
        The backend app.main:lifespan function runs Base.metadata.create_all()
        on startup, which should create:
        - users
        - messages  
        - notifications
        - friendships
        """
        from sqlalchemy import inspect, create_engine
        
        # Build connection URL from connection info
        pg_url = f"postgresql://{postgres_connection_info['user']}:{postgres_connection_info['password']}@{postgres_connection_info['host']}:{postgres_connection_info['port']}/{postgres_connection_info['database']}"
        engine = create_engine(pg_url)
        
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        # Verify all expected tables exist
        expected_tables = ["users", "messages", "notifications", "friendships"]
        for table in expected_tables:
            assert table in tables, f"Table '{table}' should exist after backend starts"
