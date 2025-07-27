"""
Test suite for Dungeon API endpoints

This test suite covers:
- API endpoint functionality
- Request/response validation
- Error handling and status codes
- Integration with DungeonService
- Authentication and authorization
"""
import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import status

from app.api.v2.dungeons import router
from app.application.services.dungeon_service import (
    DungeonService, 
    DungeonLevelLockedError, 
    InsufficientRequirementsError
)
from app.api.v2.schemas.dungeon_schemas import (
    DungeonEntryRequest,
    TrialCompletionRequest,
    DungeonEntryResponse,
    TrialCompletionResponse
)


@pytest.mark.asyncio
class TestDungeonAPIEndpoints:
    """Test the dungeon API endpoints."""
    
    @pytest.fixture
    def mock_dungeon_service(self):
        """Create a mock DungeonService."""
        service = AsyncMock(spec=DungeonService)
        return service
    
    @pytest.fixture
    def client(self):
        """Create a test client."""
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(router, prefix="/api/v2")
        return TestClient(app)
    
    @pytest.fixture
    def auth_headers(self):
        """Create mock authentication headers."""
        return {"Authorization": "Bearer test_token"}
    
    async def test_enter_dungeon_success(self, client, mock_dungeon_service, auth_headers):
        """Test successful dungeon entry."""
        # Mock service response
        mock_session = MagicMock()
        mock_session.id = "session_123"
        mock_session.ascendant_id = 1
        mock_session.dungeon_level = 3
        mock_session.trials_required = 3
        mock_session.trials_completed = 0
        mock_session.created_at = datetime.now(timezone.utc)
        mock_session.expires_at = datetime.now(timezone.utc)
        
        mock_trials = [
            {
                "trial_type": "movement_based",
                "target_reps": 20,
                "movement_category": "push",
                "difficulty_multiplier": 1.2
            }
        ]
        
        mock_dungeon_service.enter_dungeon.return_value = {
            "session": mock_session,
            "trials": mock_trials
        }
        
        # Mock dependency injection
        with patch("app.api.v2.dungeons.get_dungeon_service", return_value=mock_dungeon_service):
            # Note: The dungeons.py endpoints don't use authentication directly
            # They accept user_id as a parameter in the request body
            
            request_data = {
                "ascendant_id": 1,
                "dungeon_level": 3
            }
            
            response = client.post(
                "/api/v2/dungeons/enter",
                json=request_data,
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["success"] == True
            assert data["session_id"] == "session_123"
            assert data["dungeon_level"] == 3
            assert len(data["trials"]) == 1
            assert data["trials"][0]["trial_type"] == "movement_based"
    
    async def test_enter_dungeon_level_locked(self, client, mock_dungeon_service, auth_headers):
        """Test dungeon entry with locked level."""
        # Mock service to raise level locked error
        mock_dungeon_service.enter_dungeon.side_effect = DungeonLevelLockedError("Level 5 is locked")
        
        with patch("app.api.v2.dungeons.get_dungeon_service", return_value=mock_dungeon_service):
            # Note: The dungeons.py endpoints don't use authentication directly
            # They accept user_id as a parameter in the request body
                
                request_data = {
                    "ascendant_id": 1,
                    "dungeon_level": 5
                }
                
                response = client.post(
                    "/api/v2/dungeons/enter",
                    json=request_data,
                    headers=auth_headers
                )
                
                assert response.status_code == status.HTTP_403_FORBIDDEN
                data = response.json()
                assert "Level 5 is locked" in data["detail"]
    
    async def test_enter_dungeon_insufficient_requirements(self, client, mock_dungeon_service, auth_headers):
        """Test dungeon entry with insufficient requirements."""
        # Mock service to raise insufficient requirements error
        mock_dungeon_service.enter_dungeon.side_effect = InsufficientRequirementsError("Not enough aura")
        
        with patch("app.api.v2.dungeons.get_dungeon_service", return_value=mock_dungeon_service):
            # Note: The dungeons.py endpoints don't use authentication directly
            # They accept user_id as a parameter in the request body
                
                request_data = {
                    "ascendant_id": 1,
                    "dungeon_level": 3
                }
                
                response = client.post(
                    "/api/v2/dungeons/enter",
                    json=request_data,
                    headers=auth_headers
                )
                
                assert response.status_code == status.HTTP_400_BAD_REQUEST
                data = response.json()
                assert "Not enough aura" in data["detail"]
    
    async def test_enter_dungeon_invalid_request(self, client, auth_headers):
        """Test dungeon entry with invalid request data."""
        # Missing required fields
        request_data = {
            "dungeon_level": 3
            # Missing ascendant_id
        }
        
        response = client.post(
            "/api/v2/dungeons/enter",
            json=request_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    async def test_complete_trial_success(self, client, mock_dungeon_service, auth_headers):
        """Test successful trial completion."""
        # Mock service response
        mock_dungeon_service.complete_trial.return_value = {
            "success": True,
            "trial_completed": True,
            "session_completed": False,
            "rewards": {
                "base_xp": 100,
                "bonus_xp": 20,
                "total_xp": 120,
                "shadow_keys": 2
            },
            "next_trial": {
                "trial_type": "endurance_challenge",
                "target_reps": 30,
                "movement_category": "squat"
            }
        }
        
        with patch("app.api.v2.dungeons.get_dungeon_service", return_value=mock_dungeon_service):
            request_data = {
                "session_id": "session_123",
                "trial_data": {
                    "reps_completed": 20,
                    "target_reps": 20,
                    "completion_time": 60.0,
                    "form_score": 0.9
                }
            }
            
            response = client.post(
                "/api/v2/dungeons/complete-trial",
                json=request_data,
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["success"] == True
            assert data["trial_completed"] == True
            assert data["session_completed"] == False
            assert data["rewards"]["total_xp"] == 120
            assert "next_trial" in data
    
    async def test_complete_trial_session_completion(self, client, mock_dungeon_service, auth_headers):
        """Test trial completion that completes the session."""
        # Mock service response for session completion
        mock_dungeon_service.complete_trial.return_value = {
            "success": True,
            "trial_completed": True,
            "session_completed": True,
            "rewards": {
                "base_xp": 150,
                "bonus_xp": 30,
                "total_xp": 180,
                "shadow_keys": 3,
                "completion_bonus": 50
            },
            "dungeon_completed": True,
            "new_level_unlocked": 4
        }
        
        with patch("app.api.v2.dungeons.get_dungeon_service", return_value=mock_dungeon_service):
            request_data = {
                "session_id": "session_123",
                "trial_data": {
                    "reps_completed": 25,
                    "target_reps": 25,
                    "completion_time": 45.0,
                    "form_score": 0.95
                }
            }
            
            response = client.post(
                "/api/v2/dungeons/complete-trial",
                json=request_data,
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["success"] == True
            assert data["session_completed"] == True
            assert data["dungeon_completed"] == True
            assert data["new_level_unlocked"] == 4
            assert data["rewards"]["completion_bonus"] == 50
    
    async def test_complete_trial_invalid_session(self, client, mock_dungeon_service, auth_headers):
        """Test trial completion with invalid session."""
        # Mock service to raise exception for invalid session
        mock_dungeon_service.complete_trial.side_effect = ValueError("Invalid session ID")
        
        with patch("app.api.v2.dungeons.get_dungeon_service", return_value=mock_dungeon_service):
            request_data = {
                "session_id": "invalid_session",
                "trial_data": {
                    "reps_completed": 20,
                    "target_reps": 20,
                    "completion_time": 60.0,
                    "form_score": 0.9
                }
            }
            
            response = client.post(
                "/api/v2/dungeons/complete-trial",
                json=request_data,
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            data = response.json()
            assert "Invalid session ID" in data["detail"]
    
    async def test_get_dungeon_progress_success(self, client, mock_dungeon_service, auth_headers):
        """Test successful dungeon progress retrieval."""
        # Mock service response
        mock_progress = {
            "ascendant_id": 1,
            "highest_level_completed": 3,
            "current_session": {
                "session_id": "session_123",
                "dungeon_level": 4,
                "trials_completed": 1,
                "trials_required": 3,
                "progress_percentage": 33.3
            },
            "available_levels": [1, 2, 3, 4],
            "locked_levels": [5, 6, 7, 8, 9, 10],
            "total_dungeons_completed": 15,
            "total_shadow_keys_earned": 45
        }
        
        mock_dungeon_service.get_dungeon_progress.return_value = mock_progress
        
        with patch("app.api.v2.dungeons.get_dungeon_service", return_value=mock_dungeon_service):
            response = client.get(
                "/api/v2/dungeons/progress/1",
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["ascendant_id"] == 1
            assert data["highest_level_completed"] == 3
            assert data["current_session"]["session_id"] == "session_123"
            assert len(data["available_levels"]) == 4
            assert len(data["locked_levels"]) == 6
    
    async def test_get_dungeon_progress_not_found(self, client, mock_dungeon_service, auth_headers):
        """Test dungeon progress retrieval for non-existent ascendant."""
        # Mock service to return None
        mock_dungeon_service.get_dungeon_progress.return_value = None
        
        with patch("app.api.v2.dungeons.get_dungeon_service", return_value=mock_dungeon_service):
            response = client.get(
                "/api/v2/dungeons/progress/999",
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_404_NOT_FOUND
            data = response.json()
            assert "Ascendant not found" in data["detail"]
    
    async def test_get_dungeon_session_success(self, client, mock_dungeon_service, auth_headers):
        """Test successful dungeon session retrieval."""
        # Mock service response
        mock_session_data = {
            "session_id": "session_123",
            "user_id": 1,
            "dungeon_level": 3,
            "trials_completed": 2,
            "total_trials": 3,
            "is_completed": False,
            "created_at": "2024-01-15T10:00:00Z",
            "expires_at": "2024-01-15T12:00:00Z",
            "daily_modifier": {
                "type": "xp_boost",
                "multiplier": 1.5,
                "description": "XP Boost Day"
            }
        }
        
        mock_dungeon_service.get_session_data.return_value = mock_session_data
        
        with patch("app.api.v2.dungeons.get_dungeon_service", return_value=mock_dungeon_service):
            response = client.get(
                "/api/v2/dungeons/session/session_123",
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["session_id"] == "session_123"
            assert data["dungeon_level"] == 3
            assert data["trials_completed"] == 2
            assert data["daily_modifier"]["type"] == "xp_boost"
    
    async def test_get_dungeon_session_not_found(self, client, mock_dungeon_service, auth_headers):
        """Test dungeon session retrieval for non-existent session."""
        # Mock service to return None
        mock_dungeon_service.get_session_data.return_value = None
        
        with patch("app.api.v2.dungeons.get_dungeon_service", return_value=mock_dungeon_service):
            response = client.get(
                "/api/v2/dungeons/session/invalid_session",
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_404_NOT_FOUND
            data = response.json()
            assert "Session not found" in data["detail"]
    
    async def test_dungeon_health_check(self, client, mock_dungeon_service):
        """Test dungeon service health check."""
        # Mock service response
        mock_dungeon_service.health_check.return_value = {
            "status": "healthy",
            "service": "DungeonService",
            "timestamp": "2024-01-15T10:00:00Z",
            "database_connected": True,
            "active_sessions": 5
        }
        
        with patch("app.api.v2.dungeons.get_dungeon_service", return_value=mock_dungeon_service):
            response = client.get("/api/v2/dungeons/health")
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["status"] == "healthy"
            assert data["service"] == "DungeonService"
            assert data["database_connected"] == True
    
    async def test_dungeon_health_check_unhealthy(self, client, mock_dungeon_service):
        """Test dungeon service health check when unhealthy."""
        # Mock service to raise exception
        mock_dungeon_service.health_check.side_effect = Exception("Database connection failed")
        
        with patch("app.api.v2.dungeons.get_dungeon_service", return_value=mock_dungeon_service):
            response = client.get("/api/v2/dungeons/health")
            
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = response.json()
            assert "Database connection failed" in data["detail"]


@pytest.mark.asyncio
class TestDungeonAPIValidation:
    """Test request/response validation for dungeon API."""
    
    @pytest.fixture
    def client(self):
        """Create a test client."""
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(router, prefix="/api/v2/dungeons")
        return TestClient(app)
    
    def test_dungeon_entry_request_validation(self):
        """Test DungeonEntryRequest validation."""
        # Valid request
        valid_data = {
            "ascendant_id": 1,
            "shadow_keys_to_use": 3
        }
        request = DungeonEntryRequest(**valid_data)
        assert request.ascendant_id == 1
        assert request.shadow_keys_to_use == 3
        
        # Invalid ascendant_id (negative)
        with pytest.raises(ValueError):
            DungeonEntryRequest(ascendant_id=-1, shadow_keys_to_use=3)
        
        # Invalid shadow_keys_to_use (negative)
        with pytest.raises(ValueError):
            DungeonEntryRequest(ascendant_id=1, shadow_keys_to_use=-1)
        
        # Invalid shadow_keys_to_use (too many)
        with pytest.raises(ValueError):
            DungeonEntryRequest(ascendant_id=1, shadow_keys_to_use=11)
    
    def test_trial_completion_request_validation(self):
        """Test TrialCompletionRequest validation."""
        # Valid request
        valid_data = {
            "session_id": "session_123",
            "trial_data": {
                "reps_completed": 20,
                "target_reps": 20,
                "completion_time": 60.0,
                "form_score": 0.9
            }
        }
        request = TrialCompletionRequest(**valid_data)
        assert request.session_id == "session_123"
        assert request.trial_data["reps_completed"] == 20
        
        # Invalid session_id (empty)
        with pytest.raises(ValueError):
            TrialCompletionRequest(
                session_id="",
                trial_data=valid_data["trial_data"]
            )
        
        # Invalid form_score (out of range)
        invalid_trial_data = valid_data["trial_data"].copy()
        invalid_trial_data["form_score"] = 1.5
        with pytest.raises(ValueError):
            TrialCompletionRequest(
                session_id="session_123",
                trial_data=invalid_trial_data
            )
    
    def test_trial_data_validation(self):
        """Test TrialData validation."""
        from app.api.v2.schemas.dungeon_schemas import TrialData
        
        # Valid data
        valid_data = {
            "reps_completed": 20,
            "target_reps": 20,
            "completion_time": 60.0,
            "form_score": 0.9
        }
        trial_data = TrialData(**valid_data)
        assert trial_data.reps_completed == 20
        assert trial_data.form_score == 0.9
        
        # Invalid reps_completed (negative)
        with pytest.raises(ValueError):
            TrialData(
                reps_completed=-5,
                target_reps=20,
                completion_time=60.0,
                form_score=0.9
            )
        
        # Invalid completion_time (negative)
        with pytest.raises(ValueError):
            TrialData(
                reps_completed=20,
                target_reps=20,
                completion_time=-10.0,
                form_score=0.9
            )


@pytest.mark.asyncio
class TestDungeonAPIIntegration:
    """Integration tests for dungeon API endpoints."""
    
    @pytest.fixture
    def integration_client(self):
        """Create a client for integration testing."""
        # This would use a test database in a real scenario
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(router, prefix="/api/v2/dungeons")
        return TestClient(app)
    
    async def test_complete_dungeon_flow(self, integration_client):
        """Test a complete dungeon flow through the API."""
        # This would be a full integration test with a test database
        # Testing: entry -> multiple trial completions -> session completion
        
        # For now, we'll structure it but mock the dependencies
        with patch("app.api.v2.dungeons.get_dungeon_service") as mock_service_dep:
            mock_service = AsyncMock()
            mock_service_dep.return_value = mock_service
            
            # Note: The dungeons.py endpoints don't use authentication directly
            # They accept user_id as a parameter in the request body
            
            # Mock successful entry
            mock_service.enter_dungeon.return_value = {
                "session": MagicMock(id="session_123", dungeon_level=3),
                "trials": [{"trial_type": "movement_based", "target_reps": 20}]
            }
            
            # Test entry
            entry_response = integration_client.post(
                "/api/v2/dungeons/enter/3",
                json={"ascendant_id": 1, "shadow_keys_to_use": 3},
                headers={"Authorization": "Bearer test_token"}
            )
            
            assert entry_response.status_code == status.HTTP_200_OK
            
            # Mock trial completion
            mock_service.complete_trial.return_value = {
                "success": True,
                "trial_completed": True,
                "session_completed": True,
                "rewards": {"total_xp": 120, "shadow_keys": 2}
            }
            
            # Test trial completion
            completion_response = integration_client.post(
                "/api/v2/dungeons/complete-trial",
                json={
                    "session_id": "session_123",
                    "trial_data": {
                        "reps_completed": 20,
                        "target_reps": 20,
                        "completion_time": 60.0,
                        "form_score": 0.9
                    }
                },
                headers={"Authorization": "Bearer test_token"}
            )
            
            assert completion_response.status_code == status.HTTP_200_OK
            completion_data = completion_response.json()
            assert completion_data["success"] == True
            assert completion_data["session_completed"] == True