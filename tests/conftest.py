"""
Pytest configuration and shared fixtures for testing the Mergington High School API.

This module provides:
- Fixtures for setting up isolated test data
- TestClient with dependency overrides for clean test isolation
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, get_activities_db


@pytest.fixture
def mock_activities():
    """
    Arrange: Provide a fresh copy of test activities for each test.
    
    This fixture ensures test isolation by returning a new dictionary
    with minimal test data that won't be polluted by other tests.
    """
    return {
        "Test Activity": {
            "description": "A test activity for unit testing",
            "schedule": "Mondays, 3:00 PM - 4:00 PM",
            "max_participants": 5,
            "participants": ["existing@test.edu"]
        },
        "Empty Activity": {
            "description": "An activity with no participants",
            "schedule": "Tuesdays, 2:00 PM - 3:00 PM",
            "max_participants": 10,
            "participants": []
        }
    }


@pytest.fixture
def client(mock_activities):
    """
    Arrange: Create a TestClient with overridden dependency injection.
    
    This fixture replaces the real activities database with our mock data,
    ensuring each test starts with a clean slate. The override is cleared
    after each test to prevent state leakage.
    """
    def override_get_activities_db():
        return mock_activities
    
    app.dependency_overrides[get_activities_db] = override_get_activities_db
    
    yield TestClient(app)
    
    # Cleanup: Clear overrides after test
    app.dependency_overrides.clear()
