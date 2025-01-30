"""Test package initialization."""
import os
import sys
from pathlib import Path

# Add the project root to Python path
root_dir = Path(__file__).parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

"""Tests package.""" 