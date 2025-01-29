import os
import sys
import pytest
import jwt
from pathlib import Path
from datetime import datetime, timedelta

# Add the project root directory to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import common test fixtures
from fastapi.testclient import TestClient
from app.main import app

# Import and configure the test app
from app import create_app
from app.config import Settings

@pytest.fixture
def test_settings():
    """Test settings with a test database and JWT secret."""
    return Settings(
        ENVIRONMENT="test",
        JWT_SECRET="test-secret",
        JWT_ALGORITHM="HS256",
        JWT_EXPIRATION_MINUTES=30
    )

@pytest.fixture
def app(test_settings):
    """Create a test FastAPI application."""
    app = create_app()
    app.state.settings = test_settings
    return app

@pytest.fixture
def client():
    """Create a test client fixture."""
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