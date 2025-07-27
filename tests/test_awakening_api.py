"""API tests for awakening endpoints."""
import pytest
from datetime import date, datetime
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.application.services.awakening_service import AwakeningService
from app.application.services.progression_service import ProgressionService
from app.api.v2.awakening import get_awakening_service


@pytest.fixture
def client():
    """Test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_awakening_service():
    """Mock awakening service."""
    mock = AsyncMock(spec=AwakeningService)
    # Ensure all required methods are available
    mock.get_or_create_daily_session = AsyncMock()
    mock.complete_quest = AsyncMock()
    mock.get_awakening_progress = AsyncMock()
    return mock


@pytest.fixture
def mock_progression_service():
    """Mock progression service."""
    return AsyncMock(spec=ProgressionService)


class TestAwakeningAPI:
    """Test cases for awakening API endpoints."""

    def test_awakening_action_new_session(self, client, mock_awakening_service):
        """Test awakening action endpoint with new session creation."""
        # Arrange
        request_data = {
            "user_id": 1,
            "readiness_level": "high"
        }
        
        mock_session_data = {
            "session_id": 1,
            "user_id": 1,
            "status": "active",
            "readiness_level": "high",
            "session_date": date.today().isoformat(),
            "quests": [
                {
                    "id": 1,
                    "type": "movement_reps",
                    "target_movement": "Push-ups",
                    "target_reps": 25,
                    "difficulty": "hard",
                    "status": "active"
                }
            ]
        }
        
        mock_awakening_service.get_or_create_daily_session.return_value = mock_session_data
        
        # Mock dependency injection
        app.dependency_overrides[get_awakening_service] = lambda: mock_awakening_service
        
        try:
            # Act
            response = client.post("/api/v2/awakening/action", json=request_data)
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["session_id"] == 1
            assert data["data"]["readiness_level"] == "high"
            assert len(data["data"]["quests"]) == 1
        finally:
            # Clean up dependency override
            app.dependency_overrides.clear()

    def test_awakening_action_invalid_readiness(self, client, mock_awakening_service):
        """Test awakening action with invalid readiness level."""
        # Arrange
        request_data = {
            "user_id": 1,
            "readiness_level": "invalid"
        }
        
        app.dependency_overrides[get_awakening_service] = lambda: mock_awakening_service
        
        try:
            # Act
            response = client.post("/api/v2/awakening/action", json=request_data)
            
            # Assert
            assert response.status_code == 422  # Validation error
        finally:
            app.dependency_overrides.clear()

    def test_complete_quest_success(self, client, mock_awakening_service):
        """Test successful quest completion."""
        # Arrange
        quest_id = 1
        request_data = {
            "user_id": 1,
            "progress_data": {"reps": 25}
        }
        
        mock_completion_result = {
            "success": True,
            "quest_completed": True,
            "session_completed": False,
            "rewards": {
                "xp": 50,
                "aura": 10,
                "shadow_keys": 1
            },
            "message": "Quest completed successfully"
        }
        
        mock_awakening_service.complete_quest.return_value = mock_completion_result
        
        app.dependency_overrides[get_awakening_service] = lambda: mock_awakening_service
        
        try:
            # Act
            response = client.post(f"/api/v2/awakening/complete-quest/{quest_id}", json=request_data)
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["quest_completed"] is True
            assert data["data"]["rewards"]["xp"] == 50
        finally:
            app.dependency_overrides.clear()

    def test_complete_quest_insufficient_progress(self, client, mock_awakening_service):
        """Test quest completion with insufficient progress."""
        # Arrange
        quest_id = 1
        request_data = {
            "user_id": 1,
            "progress_data": {"reps": 10}
        }
        
        mock_awakening_service.complete_quest.side_effect = ValueError("Insufficient progress to complete quest")
        
        app.dependency_overrides[get_awakening_service] = lambda: mock_awakening_service
        
        try:
            # Act
            response = client.post(f"/api/v2/awakening/complete-quest/{quest_id}", json=request_data)
            
            # Assert
            assert response.status_code == 400
            assert "insufficient progress" in response.json()["detail"].lower()
        finally:
            app.dependency_overrides.clear()

    def test_get_status(self, client, mock_awakening_service):
        """Test getting user awakening status."""
        # Arrange
        user_id = 1
        
        mock_session_data = {
            "session_id": 1,
            "user_id": 1,
            "status": "active",
            "readiness_level": "standard",
            "session_date": date.today().isoformat(),
            "quests": [
                {
                    "id": 1,
                    "type": "movement_reps",
                    "target_movement": "Squats",
                    "target_reps": 20,
                    "difficulty": "moderate",
                    "status": "completed"
                }
            ]
        }
        
        mock_awakening_service.get_awakening_progress.return_value = mock_session_data
        
        app.dependency_overrides[get_awakening_service] = lambda: mock_awakening_service
        
        try:
            # Act
            response = client.get(f"/api/v2/awakening/status/{user_id}")
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["user_id"] == user_id
            assert data["data"]["status"] == "active"
        finally:
            app.dependency_overrides.clear()

    def test_get_status_no_session(self, client, mock_awakening_service):
        """Test getting status when no session exists."""
        # Arrange
        user_id = 1
        mock_awakening_service.get_awakening_progress.return_value = None
        
        app.dependency_overrides[get_awakening_service] = lambda: mock_awakening_service
        
        try:
            # Act
            response = client.get(f"/api/v2/awakening/status/{user_id}")
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["session"] is None
            assert "no awakening session" in data["message"].lower()
        finally:
            app.dependency_overrides.clear()

    def test_health_check(self, client, mock_awakening_service):
        """Test awakening health check endpoint."""
        app.dependency_overrides[get_awakening_service] = lambda: mock_awakening_service
        
        try:
            # Act
            response = client.get("/api/v2/awakening/health")
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["service"] == "awakening"
        finally:
            app.dependency_overrides.clear()

    def test_awakening_action_missing_user_id(self, client, mock_awakening_service):
        """Test awakening action with missing user_id."""
        # Arrange
        request_data = {
            "readiness_level": "standard"
        }
        
        app.dependency_overrides[get_awakening_service] = lambda: mock_awakening_service
        
        try:
            # Act
            response = client.post("/api/v2/awakening/action", json=request_data)
            
            # Assert
            assert response.status_code == 422  # Validation error
        finally:
            app.dependency_overrides.clear()

    def test_complete_quest_missing_progress_data(self, client, mock_awakening_service):
        """Test quest completion with missing progress data."""
        # Arrange
        quest_id = 1
        request_data = {
            "user_id": 1
        }
        
        # Mock the complete_quest method to return a proper result
        mock_completion_result = {
            "success": True,
            "quest_completed": True,
            "session_completed": False,
            "rewards": {"xp": 25},
            "message": "Quest completed successfully"
        }
        mock_awakening_service.complete_quest.return_value = mock_completion_result
        
        app.dependency_overrides[get_awakening_service] = lambda: mock_awakening_service
        
        try:
            # Act
            response = client.post(f"/api/v2/awakening/complete-quest/{quest_id}", json=request_data)
            
            # Assert
            assert response.status_code == 200  # Should succeed with None progress_data
            data = response.json()
            assert data["success"] is True
        finally:
            app.dependency_overrides.clear()

    def test_service_error_handling(self, client, mock_awakening_service):
        """Test API error handling when service raises exception."""
        # Arrange
        request_data = {
            "user_id": 1,
            "readiness_level": "high"  # Use valid readiness level
        }
        
        mock_awakening_service.get_or_create_daily_session.side_effect = Exception("Database error")
        
        app.dependency_overrides[get_awakening_service] = lambda: mock_awakening_service
        
        try:
            # Act
            response = client.post("/api/v2/awakening/action", json=request_data)
            
            # Assert
            assert response.status_code == 500
            assert "error" in response.json()["detail"].lower()
        finally:
            app.dependency_overrides.clear()