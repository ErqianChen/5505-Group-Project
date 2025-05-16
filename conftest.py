import os
import sys
import pytest

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

@pytest.fixture(autouse=True)
def app_context():
    from app import app
    with app.app_context():
        yield