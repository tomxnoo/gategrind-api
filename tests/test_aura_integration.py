"""
Integration tests for aura updates across different progression activities.

These tests verify that aura calculations are properly included in API responses
for various progression activities like XP addition, skill unlocking, and movement logging.
"""
import pytest
from unittest.mock import AsyncMock, Mock
from fastapi.testclient import TestClient
from fastapi import status, FastAPI

from app.api.v2.progression import router as progression_router, get_progression_service
from app.infrastructure.database.session import get_async_session
from app.application.services.progression_service import ProgressionService, ProgressionResult
from app.api.v2.dependencies.auth import get_current_user_id


# Create a test app with just the progression router
app_for_testing = FastAPI()
app_for_testing.include_router(progression_router)

# Mock session and service
mock_session = AsyncMock()
mock_progression_service = AsyncMock(spec=ProgressionService)

# Mock authentication
def mock_get_current_user_id():
    return 1

# Override dependencies
app_for_testing.dependency_overrides[get_async_session] = lambda: mock_session
app_for_testing.dependency_overrides[get_progression_service] = lambda: mock_progression_service
app_for_testing.dependency_overrides[get_current_user_id] = mock_get_current_user_id


class TestAuraIntegration:
    """Test class for aura integration across different progression activities."""

    @pytest.fixture
    def client(self):
        """Create a test client for the FastAPI application."""
        return TestClient(app_for_testing)

    @pytest.fixture(autouse=True)
    def reset_mocks(self):
        """Reset mocks before each test."""
        mock_progression_service.reset_mock()
        mock_session.reset_mock()
        # Clear any side effects
        mock_progression_service.add_xp.side_effect = None
        mock_progression_service.unlock_skill.side_effect = None

    @pytest.fixture
    def progression_result_with_aura(self):
        """Create a progression result with aura update information."""
        result = ProgressionResult()
        result.user_id = 1
        result.xp_added = 100
        result.category = "strength"
        result.level_changes = {}
        result.stat_points_awarded = {}
        result.milestone_rewards = {}
        result.stat_rewards_awarded = {}
        result.previous_aura = 1000
        result.new_aura = 1025
        result.aura_change_reason = "Strength progression"
        return result

    # Test XP Addition Aura Updates
    def test_add_xp_includes_aura_update(self, client, progression_result_with_aura):
        """Test that add XP endpoint includes aura update information."""
        mock_progression_service.add_xp.return_value = progression_result_with_aura
        
        response = client.post("/progression/add-xp", json={
            "user_id": 1,
            "amount": 100,
            "category": "strength"
        })
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "data" in data
        assert "aura_update" in data["data"]
        
        aura_update = data["data"]["aura_update"]
        assert aura_update["previous_aura"] == 1000
        assert aura_update["new_aura"] == 1025
        assert aura_update["change"] == 25
        assert aura_update["reason"] == "Strength progression"

    def test_add_xp_different_categories_aura_reasons(self, client):
        """Test that different XP categories produce appropriate aura change reasons."""
        categories = ["global", "strength", "endurance", "technique"]
        expected_reasons = {
            "global": "Global progression",
            "strength": "Strength progression", 
            "endurance": "Endurance progression",
            "technique": "Technique progression"
        }
        
        for category in categories:
            # Create result with category-specific aura reason
            result = ProgressionResult()
            result.user_id = 1
            result.xp_added = 100
            result.category = category
            result.level_changes = {}
            result.stat_points_awarded = {}
            result.milestone_rewards = {}
            result.stat_rewards_awarded = {}
            result.previous_aura = 1000
            result.new_aura = 1025
            result.aura_change_reason = expected_reasons[category]
            
            mock_progression_service.add_xp.return_value = result
            
            response = client.post("/progression/add-xp", json={
                "user_id": 1,
                "amount": 100,
                "category": category
            })
            
            assert response.status_code == 200
            data = response.json()
            assert "aura_update" in data["data"]
            assert data["data"]["aura_update"]["change"] == 25
            assert data["data"]["aura_update"]["reason"] == expected_reasons[category]

    def test_unlock_skill_includes_aura_update(self, client):
        """Test that unlocking a skill includes aura update information."""
        # Mock skill unlock result with aura update
        unlock_result = ProgressionResult()
        unlock_result.user_id = 1
        unlock_result.xp_added = 0
        unlock_result.category = ""
        unlock_result.level_changes = {}
        unlock_result.stat_points_awarded = {}
        unlock_result.milestone_rewards = {}
        unlock_result.stat_rewards_awarded = {}
        unlock_result.skill_points_deducted = {"strength_points": 1}
        unlock_result.unlock_message = "Unlocked Basic Push-up Form"
        unlock_result.node_name = "Basic Push-up Form"
        unlock_result.previous_aura = 1500
        unlock_result.new_aura = 1550
        unlock_result.aura_change_reason = "Skill unlock"
        
        mock_progression_service.unlock_skill.return_value = unlock_result
        
        response = client.post("/progression/unlock-skill", json={
            "node_id": "test_node_1"
        })
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "data" in data
        assert "aura_update" in data["data"]
        
        aura_update = data["data"]["aura_update"]
        assert aura_update["previous_aura"] == 1500
        assert aura_update["new_aura"] == 1550
        assert aura_update["change"] == 50
        assert aura_update["reason"] == "Skill unlock"