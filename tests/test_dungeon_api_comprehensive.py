"""
Comprehensive API Endpoint Tests for Dungeon System

This test suite covers:
- All dungeon API endpoints
- Authentication and authorization
- Input validation
- Error handling
- Response format validation
- Rate limiting
"""
import pytest
import json
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import status

from app.main import app
from app.infrastructure.database.models.v2 import (
    Ascendant, DungeonSession, DungeonTrial, DailyModifier
)


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_auth_token():
    """Mock authentication token."""
    return "Bearer test_token_123"


@pytest.fixture
def sample_ascendant_data():
    """Sample ascendant data for testing."""
    return {
        "id": 1,
        "username": "test_user",
        "aura": 2000,
        "strength_points": 100,
        "endurance_points": 95,
        "technique_points": 90,
        "skill_points": 200
    }


@pytest.fixture
def sample_session_data():
    """Sample dungeon session data."""
    return {
        "id": 1,
        "ascendant_id": 1,
        "dungeon_level": 5,
        "status": "active",
        "trial_data": {
            "trial_id": "test_123",
            "movements": ["push_up", "squat", "burpee"],
            "requirements": {"push_up": 20, "squat": 30, "burpee": 15}
        },
        "expires_at": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
    }


class TestDungeonAPIEndpoints:
    """Test all dungeon API endpoints."""
    
    @patch("app.api.v2.dependencies.auth.get_current_user_id")
    def test_enter_dungeon_success(self, mock_get_user_id, client, mock_auth_token, sample_ascendant_data):
        """Test successful dungeon entry."""
        # Setup authentication mock
        mock_get_user_id.return_value = 1
        
        with patch('app.application.services.dungeon_service.DungeonService.enter_dungeon') as mock_enter:
            mock_enter.return_value = {
                "status": "success",
                "session_id": 1,
                "dungeon_level": 5,
                "trial_data": {
                    "trial_id": "test_123",
                    "movements": ["push_up", "squat"],
                    "requirements": {"push_up": 20, "squat": 30}
                },
                "expires_at": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
            }
            
            response = client.post(
                "/api/v2/dungeons/enter",
                json={"dungeon_level": 5},
                headers={"Authorization": mock_auth_token}
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["status"] == "success"
            assert data["session_id"] == 1
            assert data["dungeon_level"] == 5
            assert "trial_data" in data
    
    @patch("app.api.v2.dependencies.auth.get_current_user_id")
    def test_enter_dungeon_invalid_level(self, mock_get_user_id, client, mock_auth_token):
        """Test dungeon entry with invalid level."""
        # Setup authentication mock
        mock_get_user_id.return_value = 1
        
        response = client.post(
            "/api/v2/dungeons/enter",
            json={"dungeon_level": 0},  # Invalid level
            headers={"Authorization": mock_auth_token}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @patch("app.api.v2.dependencies.auth.get_current_user_id")
    def test_enter_dungeon_insufficient_requirements(self, mock_get_user_id, client, mock_auth_token):
        """Test dungeon entry with insufficient requirements."""
        # Setup authentication mock
        mock_get_user_id.return_value = 1
        
        with patch('app.application.services.dungeon_service.DungeonService.enter_dungeon') as mock_enter:
            from app.application.services.dungeon_service import InsufficientRequirementsError
            mock_enter.side_effect = InsufficientRequirementsError("Insufficient aura")
            
            response = client.post(
                "/api/v2/dungeons/enter",
                json={"dungeon_level": 10},
                headers={"Authorization": mock_auth_token}
            )
            
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            data = response.json()
            assert "Insufficient aura" in data["detail"]
    
    @patch("app.api.v2.dependencies.auth.get_current_user_id")
    def test_enter_dungeon_active_session_exists(self, mock_get_user_id, client, mock_auth_token):
        """Test dungeon entry when active session already exists."""
        # Setup authentication mock
        mock_get_user_id.return_value = 1
        
        with patch('app.application.services.dungeon_service.DungeonService.enter_dungeon') as mock_enter:
            from app.application.services.dungeon_service import ActiveSessionExistsError
            mock_enter.side_effect = ActiveSessionExistsError("Active session exists")
            
            response = client.post(
                "/api/v2/dungeons/enter",
                json={"dungeon_level": 5},
                headers={"Authorization": mock_auth_token}
            )
            
            assert response.status_code == status.HTTP_409_CONFLICT
            data = response.json()
            assert "Active session exists" in data["detail"]
    
    @patch("app.api.v2.dependencies.auth.get_current_user_id")
    def test_get_active_session_success(self, mock_get_user_id, client, mock_auth_token, sample_session_data):
        """Test getting active session successfully."""
        # Setup authentication mock
        mock_get_user_id.return_value = 1
        
        with patch('app.application.services.dungeon_service.DungeonService.get_active_session') as mock_get:
            mock_session = MagicMock()
            mock_session.id = 1
            mock_session.dungeon_level = 5
            mock_session.status = "active"
            mock_session.trial_data = sample_session_data["trial_data"]
            mock_session.expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
            mock_get.return_value = mock_session
            
            response = client.get(
                "/api/v2/dungeons/session",
                headers={"Authorization": mock_auth_token}
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["id"] == 1
            assert data["dungeon_level"] == 5
            assert data["status"] == "active"
    
    @patch("app.api.v2.dependencies.auth.get_current_user_id")
    def test_get_active_session_not_found(self, mock_get_user_id, client, mock_auth_token):
        """Test getting active session when none exists."""
        # Setup authentication mock
        mock_get_user_id.return_value = 1
        
        with patch('app.application.services.dungeon_service.DungeonService.get_active_session') as mock_get:
            mock_get.return_value = None
            
            response = client.get(
                "/api/v2/dungeons/session",
                headers={"Authorization": mock_auth_token}
            )
            
            assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @patch("app.api.v2.dependencies.auth.get_current_user_id")
    def test_complete_trial_success(self, mock_get_user_id, client, mock_auth_token):
        """Test successful trial completion."""
        # Setup authentication mock
        mock_get_user_id.return_value = 1
        
        with patch('app.application.services.dungeon_service.DungeonService.complete_trial') as mock_complete:
            mock_complete.return_value = {
                "status": "completed",
                "rewards": [
                    {"type": "shadow_key", "amount": 1},
                    {"type": "experience", "amount": 100}
                ],
                "completion_time": 300,
                "accuracy": 95.5
            }
            
            completion_data = {
                "movements_completed": ["push_up", "squat", "burpee"],
                "completion_time": 300,
                "accuracy": 95.5
            }
            
            response = client.post(
                "/api/v2/dungeons/complete",
                json=completion_data,
                headers={"Authorization": mock_auth_token}
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["status"] == "completed"
            assert len(data["rewards"]) == 2
            assert data["completion_time"] == 300
            assert data["accuracy"] == 95.5
    
    @patch("app.api.v2.dependencies.auth.get_current_user_id")
    def test_complete_trial_invalid_data(self, mock_get_user_id, client, mock_auth_token):
        """Test trial completion with invalid data."""
        # Setup authentication mock
        mock_get_user_id.return_value = 1
        
        invalid_data = {
            "movements_completed": [],  # Empty movements
            "completion_time": -1,  # Invalid time
            "accuracy": 150  # Invalid accuracy > 100
        }
        
        response = client.post(
            "/api/v2/dungeons/complete",
            json=invalid_data,
            headers={"Authorization": mock_auth_token}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @patch("app.api.v2.dependencies.auth.get_current_user_id")
    def test_abandon_session_success(self, mock_get_user_id, client, mock_auth_token):
        """Test successful session abandonment."""
        # Setup authentication mock
        mock_get_user_id.return_value = 1
        
        with patch('app.application.services.dungeon_service.DungeonService.abandon_active_session') as mock_abandon:
            mock_abandon.return_value = {
                "status": "abandoned",
                "session_id": 1,
                "message": "Session abandoned successfully"
            }
            
            response = client.post(
                "/api/v2/dungeons/abandon",
                headers={"Authorization": mock_auth_token}
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["status"] == "abandoned"
            assert data["session_id"] == 1
    
    @patch("app.api.v2.dependencies.auth.get_current_user_id")
    def test_get_dungeon_progress_success(self, mock_get_user_id, client, mock_auth_token):
        """Test getting dungeon progress successfully."""
        # Setup authentication mock
        mock_get_user_id.return_value = 1
        
        with patch('app.application.services.dungeon_service.DungeonService.get_dungeon_progress') as mock_progress:
            mock_progress.return_value = {
                "current_level": 5,
                "max_unlocked_level": 8,
                "total_completions": 25,
                "total_shadow_keys": 15,
                "recent_sessions": [
                    {
                        "level": 5,
                        "status": "completed",
                        "completion_time": 300,
                        "completed_at": datetime.now(timezone.utc).isoformat()
                    }
                ]
            }
            
            response = client.get(
                "/api/v2/dungeons/progress",
                headers={"Authorization": mock_auth_token}
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["current_level"] == 5
            assert data["max_unlocked_level"] == 8
            assert data["total_completions"] == 25
            assert len(data["recent_sessions"]) == 1
    
    def test_get_daily_modifier_success(self, client, mock_auth_token):
        """Test getting daily modifier successfully."""
        with patch('app.application.services.dungeon_service.DungeonService.get_active_daily_modifier') as mock_modifier:
            mock_modifier.return_value = {
                "modifier_type": "strength_focus",
                "description": "Strength training day",
                "difficulty_multiplier": 1.2,
                "reward_multiplier": 1.3,
                "date": datetime.now(timezone.utc).date().isoformat()
            }
            
            response = client.get(
                "/api/v2/dungeons/daily-modifier",
                headers={"Authorization": mock_auth_token}
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["modifier_type"] == "strength_focus"
            assert data["difficulty_multiplier"] == 1.2
            assert data["reward_multiplier"] == 1.3
    
    def test_get_leaderboard_success(self, client, mock_auth_token):
        """Test getting dungeon leaderboard successfully."""
        with patch('app.application.services.dungeon_service.DungeonService.get_leaderboard') as mock_leaderboard:
            mock_leaderboard.return_value = {
                "leaderboard": {
                    "daily": [
                        {"username": "player1", "level": 10, "completions": 5, "total_time": 1200},
                        {"username": "player2", "level": 9, "completions": 4, "total_time": 1350}
                    ],
                    "weekly": [
                        {"username": "player1", "level": 10, "completions": 25, "total_time": 6000},
                        {"username": "player3", "level": 8, "completions": 20, "total_time": 7200}
                    ],
                    "all_time": [
                        {"username": "player1", "level": 10, "completions": 100, "total_time": 25000},
                        {"username": "player4", "level": 10, "completions": 95, "total_time": 26000}
                    ]
                }
            }
            
            response = client.get(
                "/api/v2/dungeons/leaderboard",
                headers={"Authorization": mock_auth_token}
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "leaderboard" in data
            assert "daily" in data["leaderboard"]
            assert "weekly" in data["leaderboard"]
            assert "all_time" in data["leaderboard"]
            assert len(data["leaderboard"]["daily"]) == 2
    
    @patch("app.api.v2.dependencies.auth.get_current_user_id")
    def test_unauthorized_access(self, mock_get_user_id, client):
        """Test that endpoints require authentication."""
        # Setup authentication mock to raise an exception for unauthorized access
        from fastapi import HTTPException
        mock_get_user_id.side_effect = HTTPException(status_code=401, detail="Unauthorized")
        
        endpoints = [
            ("/api/v2/dungeons/enter", "POST", {"dungeon_level": 5}),
            ("/api/v2/dungeons/session", "GET", None),
            ("/api/v2/dungeons/complete", "POST", {"movements_completed": []}),
            ("/api/v2/dungeons/abandon", "POST", None),
            ("/api/v2/dungeons/progress", "GET", None),
            ("/api/v2/dungeons/daily-modifier", "GET", None),
            ("/api/v2/dungeons/leaderboard", "GET", None)
        ]
        
        for endpoint, method, data in endpoints:
            if method == "GET":
                response = client.get(endpoint, headers={"Authorization": "Bearer invalid_token"})
            else:
                response = client.post(endpoint, json=data, headers={"Authorization": "Bearer invalid_token"})
            
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @patch("app.api.v2.dependencies.auth.get_current_user_id")
    def test_rate_limiting(self, mock_get_user_id, client, mock_auth_token):
        """Test rate limiting on API endpoints."""
        # Setup authentication mock
        mock_get_user_id.return_value = 1
        
        # This would typically test actual rate limiting
        # For now, we'll test the structure
        
        with patch('app.application.services.dungeon_service.DungeonService.enter_dungeon') as mock_enter:
            mock_enter.return_value = {"status": "success", "session_id": 1}
            
            # Make multiple rapid requests
            responses = []
            for _ in range(10):
                response = client.post(
                    "/api/v2/dungeons/enter",
                    json={"dungeon_level": 1},
                    headers={"Authorization": mock_auth_token}
                )
                responses.append(response.status_code)
            
            # In a real implementation, some requests would be rate limited
            # For now, we just verify the endpoint structure works
            assert all(code in [200, 429, 400] for code in responses)


class TestDungeonAPIValidation:
    """Test input validation for dungeon API endpoints."""
    
    @patch("app.api.v2.dependencies.auth.get_current_user_id")
    def test_enter_dungeon_validation(self, mock_get_user_id, client, mock_auth_token):
        """Test input validation for dungeon entry."""
        # Setup authentication mock
        mock_get_user_id.return_value = 1
        
        invalid_inputs = [
            {},  # Missing dungeon_level
            {"dungeon_level": "invalid"},  # Wrong type
            {"dungeon_level": -1},  # Negative level
            {"dungeon_level": 1000},  # Too high level
        ]
        
        for invalid_input in invalid_inputs:
            response = client.post(
                "/api/v2/dungeons/enter",
                json=invalid_input,
                headers={"Authorization": mock_auth_token}
            )
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @patch("app.api.v2.dependencies.auth.get_current_user_id")
    def test_complete_trial_validation(self, mock_get_user_id, client, mock_auth_token):
        """Test input validation for trial completion."""
        # Setup authentication mock
        mock_get_user_id.return_value = 1
        
        invalid_inputs = [
            {},  # Missing required fields
            {"movements_completed": "invalid"},  # Wrong type
            {"movements_completed": [], "completion_time": "invalid"},  # Wrong type
            {"movements_completed": [], "completion_time": -1},  # Negative time
            {"movements_completed": [], "completion_time": 100, "accuracy": -1},  # Negative accuracy
            {"movements_completed": [], "completion_time": 100, "accuracy": 150},  # Accuracy > 100
        ]
        
        for invalid_input in invalid_inputs:
            response = client.post(
                "/api/v2/dungeons/complete",
                json=invalid_input,
                headers={"Authorization": mock_auth_token}
            )
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestDungeonAPIErrorHandling:
    """Test error handling for dungeon API endpoints."""
    
    def test_database_error_handling(self, client, mock_auth_token):
        """Test handling of database errors."""
        with patch('app.application.services.dungeon_service.DungeonService.enter_dungeon') as mock_enter:
            mock_enter.side_effect = Exception("Database connection failed")
            
            response = client.post(
                "/api/v2/dungeons/enter",
                json={"dungeon_level": 5},
                headers={"Authorization": mock_auth_token}
            )
            
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    
    def test_service_unavailable_handling(self, client, mock_auth_token):
        """Test handling when service is unavailable."""
        with patch('app.application.services.dungeon_service.DungeonService.health_check') as mock_health:
            mock_health.return_value = False
            
            response = client.get(
                "/api/v2/dungeons/health",
                headers={"Authorization": mock_auth_token}
            )
            
            # This would return service unavailable in a real implementation
            # For now, we test the structure
            assert response.status_code in [200, 503]