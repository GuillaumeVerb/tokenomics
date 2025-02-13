"""Root conftest.py for pytest configuration."""
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock

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

# Set the env file path for testing
os.environ["ENV_FILE"] = str(ROOT_DIR / ".env.test")

# Mock MongoDB before importing app
sys.modules["pymongo"] = MagicMock()
sys.modules["pymongo.collection"] = MagicMock()
sys.modules["pymongo.database"] = MagicMock()
sys.modules["pymongo.mongo_client"] = MagicMock()

# Import app and settings after mocking
from app.core.config import Settings  # noqa: E402
from app.main import app  # noqa: E402

@pytest.fixture
def test_settings():
    """Test settings with a test database and JWT secret."""
    return Settings(
        _env_file=".env.test",
        ENVIRONMENT="test",
        DEBUG=True,
        JWT_SECRET="test-secret",
        JWT_ALGORITHM="HS256",
        JWT_EXPIRATION_MINUTES=30,
        MONGODB_URL="mongodb://localhost:27017",
        MONGODB_DB_NAME="tokenomics_test"
    )

@pytest.fixture
def mock_mongodb():
    """Create a mock MongoDB client."""
    mock_client = MagicMock()
    mock_db = MagicMock()
    mock_collection = MagicMock()
    
    mock_client.__getitem__.return_value = mock_db
    mock_db.__getitem__.return_value = mock_collection
    
    return mock_client

@pytest.fixture
def app(test_settings, mock_mongodb):
    """Create a test FastAPI application with mocked MongoDB."""
    from app import create_app
    app = create_app()
    app.state.settings = test_settings
    app.state.mongodb = mock_mongodb
    return app

@pytest.fixture
def client(app):
    """Create test client."""
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
