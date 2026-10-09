"""
Pytest fixtures for GeoMeasure test suite.
Configures temporary isolated test database and FastAPI TestClient.
"""
import os
import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ensure backend root is on sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.config import settings
from app.db.session import Base, get_db
from app.main import app

# Isolated SQLite in-memory / file database for testing
TEST_DB_URL = "sqlite:///./test_geomeasure.db"
test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Create all tables before tests run, tear down afterwards."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)
    test_db_file = Path("test_geomeasure.db")
    if test_db_file.exists():
        try:
            test_db_file.unlink()
        except Exception:
            pass


@pytest.fixture
def db_session():
    """Yield an isolated database session per test."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def client(db_session):
    """FastAPI TestClient overriding database session dependency."""
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def sample_kml_path() -> Path:
    sample_path = Path(__file__).resolve().parent.parent.parent / "sample_data" / "campus_survey.kml"
    return sample_path


@pytest.fixture
def sample_shapefile_path() -> Path:
    sample_path = Path(__file__).resolve().parent.parent.parent / "sample_data" / "parcels_shapefile.zip"
    return sample_path
