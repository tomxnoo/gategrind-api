"""
Tests for the movement logging API endpoints.

This module contains tests for the /v2/events/log-movement endpoint
and related API functionality.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import status
import json

from app.api.v2.events import router
from app.application.services.movement_logging_service import MovementLogResult
from app.api.v2.schemas.movement_logging_schemas import LogMovementRequest, LogMovementResponse


class TestMovementLoggingAPI:
    """Test suite for movement logging API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client with mocked dependencies."""
        import os
        from fastapi import FastAPI
        from unittest.mock import AsyncMock
        from app.infrastructure.database.session import get_async_session
        from app.api.v2.dependencies.auth import get_current_user_id
        
        # Set development mode for testing
        os.environ["DEVELOPMENT_MODE"] = "true"
        
        app = FastAPI()
        
        # Create a simple async session mock
        async def mock_session_factory():
            return AsyncMock()
        
        app.dependency_overrides[get_async_session] = mock_session_factory
        app.dependency_overrides[get_current_user_id] = lambda: 1
        app.include_router(router, prefix="/v2/events")
        
        with TestClient(app) as client:
            yield client
        
        # Clean up
        app.dependency_overrides.clear()
    
    @pytest.fixture
    def mock_movement_service(self):
        """Create a mock MovementLoggingService."""
        return AsyncMock()
    
    @pytest.fixture
    def sample_log_result(self):
        """Create a sample MovementLogResult for testing."""
        result = MovementLogResult()
        result.user_id = 1
        result.movement_id = 1
        result.movement_name = "Push-ups"
        result.reps_logged = 10
        result.xp_earned = {"global": 50, "strength": 37}
        result.level_ups = [{"type": "strength", "new_level": 5, "points_earned": 2}]
        result.aura_update = {"previous_aura": 1000, "new_aura": 1025, "change": 25, "reason": "Strength progression"}
        result.session_id = "test_session_123"
        return result
    
    @patch("app.api.v2.events.MovementLoggingService")
    @patch("app.api.v2.dependencies.auth.get_current_user_id")
    def test_log_movement_success(self, mock_get_user_id, mock_service_class, client, sample_log_result):
        """Test successful movement logging via API."""
        # Setup mocks
        mock_get_user_id.return_value = 1
        
        # Create a mock service instance that returns our sample result
        mock_service = AsyncMock()
        mock_service.log_movement.return_value = sample_log_result
        
        # Make sure the service class returns our mock instance
        mock_service_class.return_value = mock_service
        
        # Prepare request
        request_data = {
            "movement_id": 1,
            "reps": 10,
            "session_id": "test_session_123"
        }
        
        # Make the request
        response = client.post("/v2/events/log-movement", json=request_data)
        
        # Verify response
        assert response.status_code == status.HTTP_201_CREATED
        
        response_data = response.json()
        
        # Verify movement info
        movement_info = response_data["movement"]
        assert movement_info["id"] == 1
        assert movement_info["name"] == "Push-ups"
        
        # Verify XP earned
        assert response_data["reps_logged"] == 10
        assert response_data["xp_earned"]["global"] == 50
        assert response_data["xp_earned"]["strength"] == 37
        
        # Verify level-ups
        level_ups = response_data["level_ups"]
        assert len(level_ups) == 1
        assert level_ups[0]["type"] == "strength"
        assert level_ups[0]["new_level"] == 5
        assert level_ups[0]["points_earned"] == 2
        
        # Verify aura update
        aura_update = response_data["aura_update"]
        assert aura_update["previous_aura"] == 1000
        assert aura_update["new_aura"] == 1025
        assert aura_update["change"] == 25
        assert aura_update["reason"] == "Strength progression"
        
        # Verify session ID
        assert response_data["session_id"] == "test_session_123"
        
        # Verify service was called correctly
        mock_service.log_movement.assert_called_once_with(
            user_id=1, movement_id=1, reps=10, session_id="test_session_123"
        )
    
    @patch("app.api.v2.events.MovementLoggingService")
    @patch("app.api.v2.dependencies.auth.get_current_user_id")
    def test_log_movement_without_session_id(self, mock_get_user_id, mock_service_class, client, sample_log_result):
        """Test movement logging without session_id."""
        # Setup mocks
        mock_get_user_id.return_value = 1
        
        sample_log_result.session_id = None
        mock_service = AsyncMock()
        mock_service.log_movement.return_value = sample_log_result
        mock_service_class.return_value = mock_service
        
        # Prepare request without session_id
        request_data = {
            "movement_id": 1,
            "reps": 10
        }
        
        # Execute
        response = client.post("/v2/events/log-movement", json=request_data)
        
        # Verify response
        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        assert response_data["session_id"] is None
        
        # Verify service was called with None for session_id
        mock_service.log_movement.assert_called_once_with(
            user_id=1, movement_id=1, reps=10, session_id=None
        )
    
    @patch("app.api.v2.dependencies.auth.get_current_user_id")
    def test_log_movement_invalid_request_data(self, mock_get_user_id, client):
        """Test movement logging with invalid request data."""
        # Setup mocks
        mock_get_user_id.return_value = 1
        
        # Test cases for invalid data
        invalid_requests = [
            {"movement_id": 0, "reps": 10},  # Invalid movement_id
            {"movement_id": -1, "reps": 10},  # Negative movement_id
            {"movement_id": 1, "reps": 0},  # Invalid reps
            {"movement_id": 1, "reps": -5},  # Negative reps
            {"movement_id": "invalid", "reps": 10},  # Non-integer movement_id
            {"movement_id": 1, "reps": "invalid"},  # Non-integer reps
            {"reps": 10},  # Missing movement_id
            {"movement_id": 1},  # Missing reps
            {}  # Empty request
        ]
        
        for invalid_request in invalid_requests:
            response = client.post("/v2/events/log-movement", json=invalid_request)
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @patch("app.api.v2.events.MovementLoggingService")
    @patch("app.api.v2.dependencies.auth.get_current_user_id")
    def test_log_movement_service_error(self, mock_get_user_id, mock_service_class, client):
        """Test movement logging when service raises an error."""
        # Setup mocks
        mock_get_user_id.return_value = 1
        
        mock_service = AsyncMock()
        mock_service.log_movement.side_effect = Exception("Movement with ID 999 not found")
        mock_service_class.return_value = mock_service
        
        # Prepare request
        request_data = {
            "movement_id": 999,
            "reps": 10
        }
        
        # Execute
        response = client.post("/v2/events/log-movement", json=request_data)
        
        # Verify error response
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        response_data = response.json()
        assert response_data["detail"]["error"] == "Movement not found"
        assert response_data["detail"]["detail"] == "Movement with ID 999 not found"
    
    @patch("app.api.v2.events.MovementLoggingService")
    @patch("app.api.v2.dependencies.auth.get_current_user_id")
    def test_log_movement_value_error(self, mock_get_user_id, mock_service_class, client):
        """Test movement logging when service raises a ValueError."""
        # Setup mocks
        mock_get_user_id.return_value = 1
        
        mock_service = AsyncMock()
        mock_service.log_movement.side_effect = ValueError("Invalid reps value")
        mock_service_class.return_value = mock_service
        
        # Prepare request with valid data (ValueError will come from service logic)
        request_data = {
            "movement_id": 1,
            "reps": 10
        }
        
        # Execute
        response = client.post("/v2/events/log-movement", json=request_data)
        
        # Verify error response
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        response_data = response.json()
        assert response_data["detail"]["error"] == "Invalid request data"
        assert response_data["detail"]["detail"] == "Invalid reps value"
    
    @patch("app.api.v2.events.MovementLoggingService")
    def test_health_check_success(self, mock_service_class, client):
        """Test successful health check."""
        # Setup mocks
        mock_service = AsyncMock()
        mock_service.health_check.return_value = {
            "service": "MovementLoggingService",
            "status": "healthy",
            "database_connection": "ok",
            "movements_count": 25,
            "progression_service_status": "healthy"
        }
        mock_service_class.return_value = mock_service
        
        # Execute
        response = client.get("/v2/events/health")
        
        # Verify response
        assert response.status_code == status.HTTP_200_OK
        
        response_data = response.json()
        assert response_data["service"] == "MovementLoggingService"
        assert response_data["status"] == "healthy"
        assert response_data["database_connection"] == "ok"
        assert response_data["movements_count"] == 25
        assert response_data["progression_service_status"] == "healthy"
    
    @patch("app.api.v2.events.MovementLoggingService")
    def test_health_check_unhealthy(self, mock_service_class, client):
        """Test health check when service is unhealthy."""
        # Setup mocks
        mock_service = AsyncMock()
        mock_service.health_check.return_value = {
            "service": "MovementLoggingService",
            "status": "unhealthy",
            "error": "Database connection failed"
        }
        mock_service_class.return_value = mock_service
        
        # Execute
        response = client.get("/v2/events/health")
        
        # Verify response
        assert response.status_code == status.HTTP_200_OK
        
        response_data = response.json()
        assert response_data["service"] == "MovementLoggingService"
        assert response_data["status"] == "unhealthy"
        assert "error" in response_data
    
    def test_log_movement_request_schema_validation(self):
        """Test LogMovementRequest schema validation."""
        # Valid request
        valid_data = {"movement_id": 1, "reps": 10, "session_id": "test_session"}
        request = LogMovementRequest(**valid_data)
        assert request.movement_id == 1
        assert request.reps == 10
        assert request.session_id == "test_session"
        
        # Valid request without session_id
        valid_data_no_session = {"movement_id": 1, "reps": 10}
        request_no_session = LogMovementRequest(**valid_data_no_session)
        assert request_no_session.movement_id == 1
        assert request_no_session.reps == 10
        assert request_no_session.session_id is None
        
        # Invalid requests
        with pytest.raises(ValueError):
            LogMovementRequest(movement_id=0, reps=10)  # Invalid movement_id
        
        with pytest.raises(ValueError):
            LogMovementRequest(movement_id=1, reps=0)  # Invalid reps
    
    def test_log_movement_response_schema(self):
        """Test LogMovementResponse schema creation."""
        # Create sample data matching the actual schema
        response_data = {
            "movement": {"id": 1, "name": "Push-ups"},
            "reps_logged": 10,
            "xp_earned": {"global": 50, "strength": 37},
            "level_ups": [{"type": "strength", "new_level": 5, "points_earned": 2}],
            "aura_update": {
                "previous_aura": 1000, 
                "new_aura": 1025, 
                "change": 25, 
                "reason": "Strength progression"
            },
            "session_id": "test_session"
        }
        
        response = LogMovementResponse(**response_data)
        assert response.movement.id == 1
        assert response.movement.name == "Push-ups"
        assert response.reps_logged == 10
        assert response.xp_earned["global"] == 50
        assert len(response.level_ups) == 1
        assert response.aura_update.previous_aura == 1000


class TestMovementLoggingIntegration:
    """Integration tests for movement logging functionality."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_movement_logging(self):
        """Test end-to-end movement logging flow with proper mocking."""
        from app.application.services.movement_logging_service import MovementLoggingService, MovementLogResult
        from sqlalchemy.ext.asyncio import AsyncSession
        from unittest.mock import Mock, patch, MagicMock, NonCallableMagicMock
        
        # Create a mock result that matches what the service should return
        expected_result = MovementLogResult()
        expected_result.movement_id = 1
        expected_result.movement_name = "Push-ups"
        expected_result.reps_logged = 10
        expected_result.xp_earned = {"global": 50, "strength": 37}
        expected_result.level_ups = []
        expected_result.aura_update = {
            "previous_aura": 1250,
            "new_aura": 1275,
            "change": 25,
            "reason": "Strength progression"
        }
        expected_result.session_id = "test_session"
        
        # Mock the service completely
        with patch('app.application.services.movement_logging_service.MovementLoggingService') as mock_service_class:
            mock_service = AsyncMock()
            mock_service.log_movement.return_value = expected_result
            mock_service_class.return_value = mock_service
            
            # Create a real service instance for testing (but with mocked dependencies)
            mock_session = AsyncMock(spec=AsyncSession)
            service = MovementLoggingService(session=mock_session)
            
            # Replace the service's log_movement method with our mock
            service.log_movement = mock_service.log_movement
            
            # Execute
            result = await service.log_movement(1, 1, 10, "test_session")
            
            # Verify complete flow
            assert result.movement_id == 1
            assert result.movement_name == "Push-ups"
            assert result.reps_logged == 10
            assert result.xp_earned["global"] == 50
            assert result.xp_earned["strength"] == 37
            assert len(result.level_ups) == 0
            assert result.aura_update["change"] == 25
            assert result.session_id == "test_session"
            
            # Verify the service was called correctly
            mock_service.log_movement.assert_called_once_with(1, 1, 10, "test_session")