"""
Tests for skill tree unlocking API endpoint.

This module tests the /v2/progression/unlock-skill API endpoint including:
- Request validation
- Successful skill unlocking
- Error handling and responses
- Authentication and authorization
"""
import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from fastapi import status, FastAPI

from app.api.v2.progression import router, get_progression_service
from app.infrastructure.database.session import get_async_session
from api.dependencies.auth import get_current_user_id
from app.application.services.progression_service import ProgressionResult


# Create a test app with just the progression router
app_for_testing = FastAPI()
app_for_testing.include_router(router)

# Mock session and service
mock_session = AsyncMock()
mock_progression_service = AsyncMock()
mock_user_id = 1

# Override dependencies
app_for_testing.dependency_overrides[get_async_session] = lambda: mock_session
app_for_testing.dependency_overrides[get_progression_service] = lambda: mock_progression_service
app_for_testing.dependency_overrides[get_current_user_id] = lambda: mock_user_id


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app_for_testing)


@pytest.fixture(autouse=True)
def reset_mocks():
    """Reset mocks before each test."""
    mock_progression_service.reset_mock()
    mock_session.reset_mock()
    # Clear any side effects
    mock_progression_service.unlock_skill.side_effect = None


@pytest.fixture
def sample_unlock_result():
    """Create a sample unlock result."""
    result = ProgressionResult()
    result.user_id = 1
    result.category = "skill_unlock"
    result.node_name = "Advanced Pull-ups"
    result.unlock_message = "You have unlocked Advanced Pull-ups! Your upper body strength grows."
    result.skill_points_deducted = {
        'strength_skill_points': 3,
        'endurance_skill_points': 2,
        'technique_skill_points': 4,
        'total': 9
    }
    result.aura_change = 25
    result.new_aura = 175
    result.previous_aura = 150
    return result


class TestUnlockSkillAPI:
    """Test cases for the unlock skill API endpoint."""

    def test_unlock_skill_success(self, client, sample_unlock_result):
        """Test successful skill unlocking via API."""
        # Mock service
        mock_progression_service.unlock_skill.return_value = sample_unlock_result
        
        # Make request
        response = client.post(
            "/progression/unlock-skill",
            json={"node_id": "UPPER_DYNAMIC_L2"}
        )
        
        # Verify response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["success"] is True
        assert "Successfully unlocked skill" in data["message"]
        assert data["data"]["node_name"] == "Advanced Pull-ups"
        assert data["data"]["unlock_message"] == "You have unlocked Advanced Pull-ups! Your upper body strength grows."
        assert data["data"]["skill_points_deducted"]["total"] == 9
        assert data["data"]["skill_points_deducted"]["strength_skill_points"] == 3
        assert data["data"]["skill_points_deducted"]["endurance_skill_points"] == 2
        assert data["data"]["skill_points_deducted"]["technique_skill_points"] == 4
        assert data["data"]["aura_change"]["difference"] == 25
        assert data["data"]["aura_change"]["new"] == 175
        
        # Verify service was called correctly
        mock_progression_service.unlock_skill.assert_called_once_with(user_id=1, node_id="UPPER_DYNAMIC_L2")

    def test_unlock_skill_invalid_node_id(self, client):
        """Test skill unlocking with invalid node ID."""
        # Mock service to raise ValueError
        mock_progression_service.unlock_skill.side_effect = ValueError("Invalid node ID")

        response = client.post(
            "/progression/unlock-skill",
            json={"node_id": "INVALID_NODE"}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data["detail"] == "Invalid node ID"

    def test_unlock_skill_insufficient_requirements(self, client):
        """Test skill unlocking with insufficient requirements."""
        # Mock service to raise ValueError for insufficient requirements
        mock_progression_service.unlock_skill.side_effect = ValueError("Insufficient skill points")

        response = client.post(
            "/progression/unlock-skill",
            json={"node_id": "UPPER_DYNAMIC_L2"}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data["detail"] == "Insufficient skill points"

    def test_unlock_skill_already_unlocked(self, client):
        """Test skill unlocking when skill is already unlocked."""
        # Mock service to raise ValueError for already unlocked skill
        mock_progression_service.unlock_skill.side_effect = ValueError("Skill already unlocked")

        response = client.post(
            "/progression/unlock-skill",
            json={"node_id": "UPPER_DYNAMIC_L2"}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data["detail"] == "Skill already unlocked"

    def test_unlock_skill_user_not_found(self, client):
        """Test skill unlocking when user is not found."""
        # Mock service to raise exception with "not found" message
        mock_progression_service.unlock_skill.side_effect = Exception("User not found")

        response = client.post(
            "/progression/unlock-skill",
            json={"node_id": "UPPER_DYNAMIC_L2"}
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["detail"] == "User not found"

    def test_unlock_skill_server_error(self, client):
        """Test skill unlocking with server error."""
        # Mock service to raise generic exception
        mock_progression_service.unlock_skill.side_effect = Exception("Database connection failed")

        response = client.post(
            "/progression/unlock-skill",
            json={"node_id": "UPPER_DYNAMIC_L2"}
        )

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        assert data["detail"] == "An unexpected error occurred while unlocking skill"

    def test_unlock_skill_missing_node_id(self, client):
        """Test skill unlocking with missing node_id in request."""
        response = client.post(
            "/progression/unlock-skill",
            json={}
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_unlock_skill_invalid_json(self, client):
        """Test skill unlocking with invalid JSON."""
        response = client.post(
            "/progression/unlock-skill",
            data="invalid json"
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY