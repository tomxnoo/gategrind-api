"""
Comprehensive tests for the Progression API endpoints.

This test suite covers integration testing for the progression API endpoints,
including XP addition, level progress tracking, and error handling.
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import status, FastAPI
import json

from app.api.v2.progression import router, get_progression_service
from app.infrastructure.database.session import get_async_session
from app.application.services.progression_service import ProgressionService, ProgressionResult
from app.infrastructure.database.models.v2.ascendants import Ascendant
from app.infrastructure.database.models.v2.stats import AscendantStats


# Create a test app with just the progression router
app_for_testing = FastAPI()
app_for_testing.include_router(router)

# Mock session and service
mock_session = AsyncMock()
mock_progression_service = AsyncMock(spec=ProgressionService)

# Override dependencies
app_for_testing.dependency_overrides[get_async_session] = lambda: mock_session
app_for_testing.dependency_overrides[get_progression_service] = lambda: mock_progression_service


class TestProgressionAPI:
    """Test suite for Progression API endpoints."""
    
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
        mock_progression_service.calculate_level_progress.side_effect = None
        mock_progression_service.health_check.side_effect = None
    
    @pytest.fixture
    def sample_progression_result(self):
        """Create a sample ProgressionResult for testing."""
        result = ProgressionResult()
        result.user_id = 1
        result.xp_added = 100
        result.category = 'global'
        result.level_changes = {'global': {'previous': 5, 'new': 6, 'gained': 1}}
        result.stat_points_awarded = {'strength_points': 1, 'endurance_points': 1, 'technique_points': 1}
        result.new_aura = 150
        result.previous_aura = 100
        return result
    
    @pytest.fixture
    def sample_level_progress(self):
        """Create sample level progress data."""
        return {
            'current_level': 5,
            'current_xp': 1000,
            'next_level_xp_required': 500,
            'progress_percentage': 60.0,
            'xp_to_next_level': 200
        }
    
    @pytest.fixture
    def sample_health_data(self):
        """Create sample health check data."""
        return {
            "service": "ProgressionService",
            "status": "healthy",
            "database_connection": "ok",
            "users_count": 10
        }
    
    def test_add_xp_success(self, client, sample_progression_result):
        """Test successful XP addition."""
        mock_progression_service.add_xp.return_value = sample_progression_result
        
        # Make request
        response = client.post("/progression/add-xp", json={
            "user_id": 1,
            "amount": 100,
            "category": "global"
        })
        
        # Verify response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert "Added 100 XP to global" in data["message"]
        assert "leveled up from 5 to 6" in data["message"]
        assert data["data"]["user_id"] == 1
        assert data["data"]["xp_added"] == 100
        assert data["data"]["category"] == "global"
        
        # Verify service was called correctly
        mock_progression_service.add_xp.assert_called_once_with(
            user_id=1, amount=100, category="global"
        )
    
    def test_add_xp_validation_error_invalid_category(self, client):
        """Test XP addition with invalid category."""
        response = client.post("/progression/add-xp", json={
            "user_id": 1,
            "amount": 100,
            "category": "invalid_category"
        })
        
        # Should return validation error
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_add_xp_validation_error_negative_amount(self, client):
        """Test XP addition with negative amount."""
        response = client.post("/progression/add-xp", json={
            "user_id": 1,
            "amount": -50,
            "category": "global"
        })
        
        # Should return validation error
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_add_xp_validation_error_zero_user_id(self, client):
        """Test XP addition with zero user ID."""
        response = client.post("/progression/add-xp", json={
            "user_id": 0,
            "amount": 100,
            "category": "global"
        })
        
        # Should return validation error
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_add_xp_user_not_found(self, client):
        """Test XP addition when user is not found."""
        mock_progression_service.add_xp.side_effect = Exception("User with ID 999 not found")
        
        response = client.post("/progression/add-xp", json={
            "user_id": 999,
            "amount": 100,
            "category": "global"
        })
        
        # Should return 404
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "User with ID 999 not found" in data["detail"]
    
    def test_add_xp_service_error(self, client):
        """Test XP addition with service error."""
        mock_progression_service.add_xp.side_effect = Exception("Database connection failed")
        
        response = client.post("/progression/add-xp", json={
            "user_id": 1,
            "amount": 100,
            "category": "global"
        })
        
        # Should return 500
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        assert "unexpected error occurred" in data["detail"]
    
    def test_get_level_progress_post_success(self, client, sample_level_progress):
        """Test successful level progress retrieval via POST."""
        mock_progression_service.calculate_level_progress.return_value = sample_level_progress
        
        response = client.post("/progression/level-progress", json={
            "user_id": 1,
            "category": "global"
        })
        
        # Verify response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["data"]["user_id"] == 1
        assert data["data"]["category"] == "global"
        assert data["data"]["current_level"] == 5
        assert data["data"]["current_xp"] == 1000
        
        # Verify service was called correctly
        mock_progression_service.calculate_level_progress.assert_called_once_with(
            user_id=1, category="global"
        )
    
    def test_get_level_progress_get_success(self, client, sample_level_progress):
        """Test successful level progress retrieval via GET."""
        mock_progression_service.calculate_level_progress.return_value = sample_level_progress
        
        response = client.get("/progression/level-progress/1?category=strength")
        
        # Verify response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["data"]["user_id"] == 1
        assert data["data"]["category"] == "strength"
        
        # Verify service was called correctly
        mock_progression_service.calculate_level_progress.assert_called_once_with(
            user_id=1, category="strength"
        )
    
    def test_get_level_progress_get_default_category(self, client, sample_level_progress):
        """Test level progress retrieval with default category."""
        mock_progression_service.calculate_level_progress.return_value = sample_level_progress
        
        response = client.get("/progression/level-progress/1")
        
        # Verify response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["data"]["category"] == "global"  # Default category
    
    def test_get_level_progress_invalid_category(self, client):
        """Test level progress with invalid category."""
        response = client.get("/progression/level-progress/1?category=invalid")
        
        # Should return validation error
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "Invalid category" in data["detail"]
    
    def test_get_level_progress_user_not_found(self, client):
        """Test level progress when user is not found."""
        mock_progression_service.calculate_level_progress.side_effect = Exception("User with ID 999 not found")
        
        response = client.post("/progression/level-progress", json={
            "user_id": 999,
            "category": "global"
        })
        
        # Should return 404
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_health_check_success(self, client, sample_health_data):
        """Test successful health check."""
        mock_progression_service.health_check.return_value = sample_health_data
        
        response = client.get("/progression/health")
        
        # Verify response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["service"] == "ProgressionService"
        assert data["status"] == "healthy"
        assert data["database_connection"] == "ok"
        assert data["users_count"] == 10
        assert "timestamp" in data
    
    def test_health_check_failure(self, client):
        """Test health check failure."""
        mock_progression_service.health_check.side_effect = Exception("Database connection failed")
        
        response = client.get("/progression/health")
        
        # Should still return 200 but with unhealthy status
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["service"] == "ProgressionService"
        assert data["status"] == "unhealthy"
        assert "error" in data
    
    def test_get_valid_categories(self, client):
        """Test getting valid categories."""
        response = client.get("/progression/categories")
        
        # Verify response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "categories" in data
        assert "global" in data["categories"]
        assert "strength" in data["categories"]
        assert "endurance" in data["categories"]
        assert "technique" in data["categories"]
        assert "description" in data
    
    def test_get_xp_formula_info_success(self, client):
        """Test successful XP formula information retrieval."""
        # Mock the private method
        mock_progression_service._calculate_xp_for_level.side_effect = lambda level: 100 * (level ** 1.5) if level > 1 else 0
        
        response = client.get("/progression/xp-formula/5")
        
        # Verify response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["level"] == 5
        assert "total_xp_required" in data
        assert "xp_for_this_level" in data
        assert "formula" in data
        assert data["formula"] == "100 * (level ^ 1.5) per level"
    
    def test_get_xp_formula_info_invalid_level_low(self, client):
        """Test XP formula with invalid low level."""
        response = client.get("/progression/xp-formula/0")
        
        # Should return validation error
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "Level must be 1 or greater" in data["detail"]
    
    def test_get_xp_formula_info_invalid_level_high(self, client):
        """Test XP formula with invalid high level."""
        response = client.get("/progression/xp-formula/1001")
        
        # Should return validation error
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "Level must be 1000 or less" in data["detail"]
    
    def test_add_xp_no_level_up_message(self, client):
        """Test XP addition message when no level-up occurs."""
        # Create result with no level changes
        result = ProgressionResult()
        result.user_id = 1
        result.xp_added = 50
        result.category = 'strength'
        result.level_changes = {}
        result.stat_points_awarded = {}
        result.new_aura = 100
        result.previous_aura = 100
        
        mock_progression_service.add_xp.return_value = result
        
        response = client.post("/progression/add-xp", json={
            "user_id": 1,
            "amount": 50,
            "category": "strength"
        })
        
        # Verify response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Added 50 XP to strength"
    
    def test_add_xp_with_aura_change_message(self, client):
        """Test XP addition message includes aura change."""
        # Create result with aura change but no level-up
        result = ProgressionResult()
        result.user_id = 1
        result.xp_added = 100
        result.category = 'global'
        result.level_changes = {}
        result.stat_points_awarded = {}
        result.new_aura = 150
        result.previous_aura = 100
        
        mock_progression_service.add_xp.return_value = result
        
        response = client.post("/progression/add-xp", json={
            "user_id": 1,
            "amount": 100,
            "category": "global"
        })
        
        # Verify response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "Aura changed by 50" in data["message"]
    
    def test_missing_required_fields(self, client):
        """Test API with missing required fields."""
        # Missing amount field
        response = client.post("/progression/add-xp", json={
            "user_id": 1,
            "category": "global"
        })
        
        # Should return validation error
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_invalid_json_format(self, client):
        """Test API with invalid JSON format."""
        response = client.post(
            "/progression/add-xp",
            content="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        # Should return validation error
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY