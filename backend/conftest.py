"""Root conftest.py for pytest configuration."""
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

import jwt
import pytest
from fastapi.testclient import TestClient

# Get the absolute path of the project root
ROOT_DIR = Path(__file__).resolve().parent
APP_DIR = ROOT_DIR / "app"
TESTS_DIR = ROOT_DIR / "tests"

# Add directories to Python path
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(APP_DIR))
sys.path.insert(0, str(TESTS_DIR))

# Add the virtual environment site-packages to Python path
VENV_DIR = ROOT_DIR / "venv"
if VENV_DIR.exists():
    SITE_PACKAGES = list(VENV_DIR.glob("lib/python3.*/site-packages"))[0]
    sys.path.insert(0, str(SITE_PACKAGES))

# Set environment variables for testing
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("TESTING", "True")

# Import app and settings after path setup
from app import create_app  # noqa: E402
from app.core.config import Settings  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture
def test_settings():
    """Test settings with a test database and JWT secret."""
    return Settings(
        ENVIRONMENT="test",
        DEBUG=True,
        JWT_SECRET="test-secret",
        JWT_ALGORITHM="HS256",
        JWT_EXPIRATION_MINUTES=30,
        MONGODB_URL="mongodb://localhost:27017",
        MONGODB_DB_NAME="tokenomics_test"
    )

@pytest.fixture
def app(test_settings):
    """Create a test FastAPI application."""
    app = create_app()
    app.state.settings = test_settings
    return app

@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)

@pytest.fixture
def auth_headers(test_settings):
    """Create authentication headers with a valid JWT token."""
    token = jwt.encode(
        {
            'sub': 'test@example.com',
            'exp': datetime.utcnow() + timedelta(hours=1)
        },
        test_settings.JWT_SECRET,
        algorithm=test_settings.JWT_ALGORITHM
    )
    return {'Authorization': f'Bearer {token}'}

@pytest.fixture
def test_app():
    """Return the FastAPI application instance."""
    return app
