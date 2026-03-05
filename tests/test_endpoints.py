"""
Integration tests for the Mergington High School Activities API.

Tests use the AAA (Arrange-Act-Assert) pattern:
- Arrange: Set up test data and preconditions
- Act: Execute the code being tested
- Assert: Verify the results meet expectations

Each test is isolated with fresh mock data via the client fixture.
"""

import pytest


class TestRootEndpoint:
    """Tests for the GET / endpoint"""
    
    def test_root_redirects_to_index(self, client):
        """
        Arrange: Use the test client
        Act: Make a GET request to /
        Assert: Verify it redirects to /static/index.html
        """
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivitiesEndpoint:
    """Tests for the GET /activities endpoint"""
    
    def test_get_all_activities_returns_all_activities(self, client, mock_activities):
        """
        Arrange: Test client with mock activities
        Act: Make a GET request to /activities
        Assert: Verify all activities are returned with correct structure
        """
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert "Test Activity" in data
        assert "Empty Activity" in data
        assert data["Test Activity"]["description"] == "A test activity for unit testing"
    
    def test_get_activities_includes_participant_count(self, client):
        """
        Arrange: Test client with activities containing participants
        Act: Make a GET request to /activities
        Assert: Verify participant lists are included in response
        """
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "participants" in data["Test Activity"]
        assert "existing@test.edu" in data["Test Activity"]["participants"]
        assert data["Empty Activity"]["participants"] == []


class TestSignupEndpoint:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_student_succeeds(self, client):
        """
        Arrange: Test client with an activity that needs a new participant
        Act: POST a signup request with a new email
        Assert: Verify the student is added and response is successful
        """
        # Act
        response = client.post(
            "/activities/Test Activity/signup?email=new@test.edu"
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "Signed up new@test.edu for Test Activity" in data["message"]
    
    def test_signup_adds_participant_to_activity(self, client, mock_activities):
        """
        Arrange: Test client with an activity and mock data
        Act: POST a signup request with a new email
        Assert: Verify the participant is actually added to the activity list
        """
        # Arrange
        new_email = "another@test.edu"
        assert new_email not in mock_activities["Test Activity"]["participants"]
        
        # Act
        client.post(f"/activities/Test Activity/signup?email={new_email}")
        
        # Assert
        assert new_email in mock_activities["Test Activity"]["participants"]
    
    def test_signup_for_nonexistent_activity_returns_404(self, client):
        """
        Arrange: Test client with known activities
        Act: POST a signup request for a non-existent activity
        Assert: Verify 404 error is returned
        """
        # Act
        response = client.post(
            "/activities/Fake Activity/signup?email=student@test.edu"
        )
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_signup_duplicate_student_returns_400(self, client):
        """
        Arrange: Test client with an activity that already has a participant
        Act: POST a signup request with an email already in the activity
        Assert: Verify 400 error is returned
        """
        # Act
        response = client.post(
            "/activities/Test Activity/signup?email=existing@test.edu"
        )
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Student already signed up"
    
    def test_signup_can_add_to_empty_activity(self, client):
        """
        Arrange: Test client with an empty activity
        Act: POST a signup request for the empty activity
        Assert: Verify the student is successfully added
        """
        # Act
        response = client.post(
            "/activities/Empty Activity/signup?email=first@test.edu"
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "Signed up first@test.edu for Empty Activity" in data["message"]


class TestUnregisterEndpoint:
    """Tests for the POST /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_existing_student_succeeds(self, client):
        """
        Arrange: Test client with an activity containing a participant
        Act: POST an unregister request for an existing participant
        Assert: Verify the student is removed and response is successful
        """
        # Act
        response = client.post(
            "/activities/Test Activity/unregister?email=existing@test.edu"
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "Removed existing@test.edu from Test Activity" in data["message"]
    
    def test_unregister_removes_participant_from_activity(self, client, mock_activities):
        """
        Arrange: Test client with an activity and known participant
        Act: POST an unregister request for that participant
        Assert: Verify the participant is actually removed from the list
        """
        # Arrange
        email = "existing@test.edu"
        assert email in mock_activities["Test Activity"]["participants"]
        
        # Act
        client.post(f"/activities/Test Activity/unregister?email={email}")
        
        # Assert
        assert email not in mock_activities["Test Activity"]["participants"]
    
    def test_unregister_for_nonexistent_activity_returns_404(self, client):
        """
        Arrange: Test client with known activities
        Act: POST an unregister request for a non-existent activity
        Assert: Verify 404 error is returned
        """
        # Act
        response = client.post(
            "/activities/Fake Activity/unregister?email=student@test.edu"
        )
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_unregister_nonexistent_student_returns_404(self, client):
        """
        Arrange: Test client with an activity and a student not in it
        Act: POST an unregister request for a student not in the activity
        Assert: Verify 404 error is returned
        """
        # Act
        response = client.post(
            "/activities/Test Activity/unregister?email=nothere@test.edu"
        )
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Student not found in this activity"
    
    def test_unregister_from_empty_activity_returns_404(self, client):
        """
        Arrange: Test client with an empty activity
        Act: POST an unregister request for that empty activity
        Assert: Verify 404 error is returned
        """
        # Act
        response = client.post(
            "/activities/Empty Activity/unregister?email=anyone@test.edu"
        )
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Student not found in this activity"


class TestEndToEndScenarios:
    """End-to-end integration tests combining multiple operations"""
    
    def test_signup_and_unregister_sequence(self, client, mock_activities):
        """
        Arrange: Test client with fresh activities
        Act: Sign up a student, then unregister them
        Assert: Verify both operations succeed and state is correct
        """
        # Act: Sign up
        signup_response = client.post(
            "/activities/Test Activity/signup?email=temp@test.edu"
        )
        
        # Assert signup succeeded
        assert signup_response.status_code == 200
        assert "temp@test.edu" in mock_activities["Test Activity"]["participants"]
        
        # Act: Unregister
        unregister_response = client.post(
            "/activities/Test Activity/unregister?email=temp@test.edu"
        )
        
        # Assert unregister succeeded
        assert unregister_response.status_code == 200
        assert "temp@test.edu" not in mock_activities["Test Activity"]["participants"]
    
    def test_multiple_signups_are_isolated(self, client, mock_activities):
        """
        Arrange: Test client with multiple activities
        Act: Sign up to different activities
        Assert: Verify participants are tracked separately per activity
        """
        # Act
        client.post("/activities/Test Activity/signup?email=alice@test.edu")
        client.post("/activities/Empty Activity/signup?email=bob@test.edu")
        
        # Assert
        assert "alice@test.edu" in mock_activities["Test Activity"]["participants"]
        assert "bob@test.edu" not in mock_activities["Test Activity"]["participants"]
        assert "bob@test.edu" in mock_activities["Empty Activity"]["participants"]
        assert "alice@test.edu" not in mock_activities["Empty Activity"]["participants"]
