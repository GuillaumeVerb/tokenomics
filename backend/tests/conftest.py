"""Common test fixtures."""
import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from app import create_app

# Add root directory to Python path
root_dir = str(Path(__file__).parent.parent)
if root_dir not in sys.path:
    sys.path.append(root_dir)

@pytest.fixture
def app():
    """Create test app instance."""
    return create_app()

@pytest.fixture
def auth_headers():
    """Return authentication headers for testing."""
    return {
        "Authorization": "Bearer test_token",
        "Content-Type": "application/json"
    }

@pytest.fixture
def client(app, auth_headers):
    """Create test client with auth headers."""
    with TestClient(app) as client:
        client.headers.update(auth_headers)
        return client 