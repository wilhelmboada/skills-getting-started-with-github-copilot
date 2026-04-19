import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)
client_no_redirect = TestClient(app, follow_redirects=False)


class TestActivitiesAPI:
    """Test suite for the Mergington High School Activities API"""

    def test_get_activities(self):
        """Test GET /activities returns all activities with correct structure"""
        # Arrange
        # (TestClient and app are already set up)

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0  # Should have activities

        # Check structure of first activity
        first_activity = next(iter(data.values()))
        required_keys = ["description", "schedule", "max_participants", "participants"]
        for key in required_keys:
            assert key in first_activity
        assert isinstance(first_activity["participants"], list)

    def test_signup_valid(self):
        """Test POST /activities/{name}/signup with valid data"""
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

        # Assert
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert email in result["message"]

        # Verify participant was added
        get_response = client.get("/activities")
        activities = get_response.json()
        assert email in activities[activity_name]["participants"]

    def test_signup_duplicate(self):
        """Test POST /activities/{name}/signup prevents duplicate signups"""
        # Arrange
        activity_name = "Programming Class"
        email = "emma@mergington.edu"  # Already signed up

        # Act
        response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

        # Assert
        assert response.status_code == 400
        result = response.json()
        assert "detail" in result
        assert "already signed up" in result["detail"]

    def test_signup_invalid_activity(self):
        """Test POST /activities/{name}/signup with non-existent activity"""
        # Arrange
        invalid_activity = "NonExistent Club"
        email = "student@mergington.edu"

        # Act
        response = client.post(f"/activities/{invalid_activity}/signup", params={"email": email})

        # Assert
        assert response.status_code == 404
        result = response.json()
        assert "detail" in result
        assert "not found" in result["detail"]

    def test_unregister_valid(self):
        """Test DELETE /activities/{name}/participants/{email} with valid data"""
        # Arrange
        activity_name = "Gym Class"
        email = "john@mergington.edu"  # Already signed up

        # Act
        response = client.delete(f"/activities/{activity_name}/participants/{email}")

        # Assert
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert "Unregistered" in result["message"]

        # Verify participant was removed
        get_response = client.get("/activities")
        activities = get_response.json()
        assert email not in activities[activity_name]["participants"]

    def test_unregister_activity_not_found(self):
        """Test DELETE /activities/{name}/participants/{email} with invalid activity"""
        # Arrange
        invalid_activity = "Fake Club"
        email = "student@mergington.edu"

        # Act
        response = client.delete(f"/activities/{invalid_activity}/participants/{email}")

        # Assert
        assert response.status_code == 404
        result = response.json()
        assert "detail" in result
        assert "not found" in result["detail"]

    def test_unregister_participant_not_found(self):
        """Test DELETE /activities/{name}/participants/{email} with participant not in activity"""
        # Arrange
        activity_name = "Chess Club"
        email = "notsignedup@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity_name}/participants/{email}")

        # Assert
        assert response.status_code == 404
        result = response.json()
        assert "detail" in result
        assert "not found" in result["detail"]

    def test_root_redirect(self):
        """Test GET / redirects to static index.html"""
        # Arrange
        # (No special setup needed)

        # Act
        response = client_no_redirect.get("/")

        # Assert
        assert response.status_code == 307  # Temporary redirect
        assert response.headers["location"] == "/static/index.html"