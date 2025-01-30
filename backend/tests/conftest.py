"""Common test fixtures."""
import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Add root directory to Python path
root_dir = str(Path(__file__).parent.parent)
if root_dir not in sys.path:
    sys.path.append(root_dir)

from app.main import app

@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI application."""
    return TestClient(app) 