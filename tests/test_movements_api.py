"""
Integration tests for the V2 Movements API endpoints.

This module contains comprehensive integration tests for the movements API,
testing the complete request/response cycle including database interactions.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
import json

from app.main import app
from app.application.services.movement_service import MovementService
from app.api.v2.movements import get_movement_service


class TestMovementsAPIIntegration:
    """Integration tests for the movements API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create a test client for the FastAPI application."""
        return TestClient(app)
    
    @pytest.fixture
    def mock_movement_service(self):
        """Create a mock MovementService for testing."""
        service = AsyncMock(spec=MovementService)
        return service
    
    @pytest.fixture
    def sample_library_data(self):
        """Sample skill tree library data for testing."""
        return {
            "categories": [
                {
                    "id": "PULL_VERTICAL",
                    "name": "Vertical Pulling",
                    "primary_stat": "STR",
                    "skill_tree": [
                        {
                            "id": 1,
                            "level": 1,
                            "name": "Foundation",
                            "description": "Basic vertical pulling movements",
                            "requirements": {
                                "ascendant_level": 1,
                                "str_points": 0,
                                "end_points": 0,
                                "tech_points": 0
                            },
                            "movements": [
                                {
                                    "id": 1,
                                    "name": "Negative Pull-ups",
                                    "xp_per_rep": 1.5,
                                    "stat_reward_type": "STR"
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    
    @pytest.fixture
    def sample_categories_data(self):
        """Sample categories data for testing."""
        return [
            {
                "id": "PULL_VERTICAL",
                "name": "Vertical Pulling",
                "primary_stat": "STR"
            },
            {
                "id": "PUSH_VERTICAL",
                "name": "Vertical Pushing",
                "primary_stat": "STR"
            }
        ]
    
    @pytest.fixture
    def sample_category_data(self):
        """Sample single category data for testing."""
        return {
            "id": "PULL_VERTICAL",
            "name": "Vertical Pulling",
            "primary_stat": "STR",
            "skill_tree": [
                {
                    "id": 1,
                    "level": 1,
                    "name": "Foundation",
                    "description": "Basic vertical pulling movements",
                    "requirements": {
                        "ascendant_level": 1,
                        "str_points": 0,
                        "end_points": 0,
                        "tech_points": 0
                    },
                    "movements": [
                        {
                            "id": 1,
                            "name": "Negative Pull-ups",
                            "xp_per_rep": 1.5,
                            "stat_reward_type": "STR"
                        }
                    ]
                }
            ]
        }

    def test_get_skill_tree_library_success(self, client, mock_movement_service, sample_library_data):
        """Test successful GET /v2/movements/library endpoint."""
        mock_movement_service.get_skill_tree_library.return_value = sample_library_data
        mock_movement_service.close_session.return_value = None
        
        # Override the FastAPI dependency
        app.dependency_overrides[get_movement_service] = lambda: mock_movement_service
        
        try:
            response = client.get("/api/v2/movements/library")
            
            assert response.status_code == 200
            data = response.json()
            
            assert "categories" in data
            assert len(data["categories"]) == 1
            assert data["categories"][0]["id"] == "PULL_VERTICAL"
            assert data["categories"][0]["name"] == "Vertical Pulling"
            assert len(data["categories"][0]["skill_tree"]) == 1
            
            # Verify service methods were called
            mock_movement_service.get_skill_tree_library.assert_called_once()
            mock_movement_service.close_session.assert_called_once()
        finally:
            # Clean up dependency override
            app.dependency_overrides.clear()

    def test_get_skill_tree_library_service_error(self, client, mock_movement_service):
        """Test GET /v2/movements/library with service error."""
        mock_movement_service.get_skill_tree_library.side_effect = Exception("Database connection failed")
        mock_movement_service.close_session.return_value = None
        
        app.dependency_overrides[get_movement_service] = lambda: mock_movement_service
        
        try:
            response = client.get("/api/v2/movements/library")
            
            assert response.status_code == 500
            data = response.json()
            assert "detail" in data
            assert "Failed to fetch skill tree library" in data["detail"]
            
            # Verify cleanup was called even on error
            mock_movement_service.close_session.assert_called_once()
        finally:
            app.dependency_overrides.clear()

    def test_get_movement_categories_success(self, client, mock_movement_service, sample_categories_data):
        """Test successful GET /v2/movements/categories endpoint."""
        mock_movement_service.get_movement_categories.return_value = sample_categories_data
        mock_movement_service.close_session.return_value = None
        
        app.dependency_overrides[get_movement_service] = lambda: mock_movement_service
        
        try:
            response = client.get("/api/v2/movements/categories")
            
            assert response.status_code == 200
            data = response.json()
            
            assert len(data) == 2
            assert data[0]["id"] == "PULL_VERTICAL"
            assert data[1]["id"] == "PUSH_VERTICAL"
            
            mock_movement_service.get_movement_categories.assert_called_once()
            mock_movement_service.close_session.assert_called_once()
        finally:
            app.dependency_overrides.clear()

    def test_get_movement_categories_service_error(self, client, mock_movement_service):
        """Test GET /v2/movements/categories with service error."""
        mock_movement_service.get_movement_categories.side_effect = Exception("Database error")
        mock_movement_service.close_session.return_value = None
        
        app.dependency_overrides[get_movement_service] = lambda: mock_movement_service
        
        try:
            response = client.get("/api/v2/movements/categories")
            
            assert response.status_code == 500
            data = response.json()
            assert "Failed to fetch movement categories" in data["detail"]
        finally:
            app.dependency_overrides.clear()

    def test_get_movement_category_success(self, client, mock_movement_service, sample_category_data):
        """Test successful GET /v2/movements/categories/{category_id} endpoint."""
        mock_movement_service.get_movement_category.return_value = sample_category_data
        mock_movement_service.close_session.return_value = None
        
        app.dependency_overrides[get_movement_service] = lambda: mock_movement_service
        
        try:
            response = client.get("/api/v2/movements/categories/PULL_VERTICAL")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["id"] == "PULL_VERTICAL"
            assert data["name"] == "Vertical Pulling"
            assert len(data["skill_tree"]) == 1
            
            mock_movement_service.get_movement_category.assert_called_once_with("PULL_VERTICAL")
            mock_movement_service.close_session.assert_called_once()
        finally:
            app.dependency_overrides.clear()

    def test_get_movement_category_not_found(self, client, mock_movement_service):
        """Test GET /v2/movements/categories/{category_id} with non-existent category."""
        mock_movement_service.get_movement_category.return_value = None
        mock_movement_service.close_session.return_value = None
        
        app.dependency_overrides[get_movement_service] = lambda: mock_movement_service
        
        try:
            response = client.get("/api/v2/movements/categories/NONEXISTENT")
            
            assert response.status_code == 404
            data = response.json()
            assert "detail" in data
            assert "Movement category 'NONEXISTENT' not found" in data["detail"]
            
            mock_movement_service.get_movement_category.assert_called_once_with("NONEXISTENT")
            mock_movement_service.close_session.assert_called_once()
        finally:
            app.dependency_overrides.clear()

    def test_get_movement_category_service_error(self, client, mock_movement_service):
        """Test GET /v2/movements/categories/{category_id} with service error."""
        mock_movement_service.get_movement_category.side_effect = Exception("Database error")
        mock_movement_service.close_session.return_value = None
        
        app.dependency_overrides[get_movement_service] = lambda: mock_movement_service
        
        try:
            response = client.get("/api/v2/movements/categories/PULL_VERTICAL")
            
            assert response.status_code == 500
            data = response.json()
            assert "Failed to fetch movement category" in data["detail"]
        finally:
            app.dependency_overrides.clear()

    def test_health_check_success(self, client, mock_movement_service):
        """Test successful GET /v2/movements/health endpoint."""
        mock_movement_service.health_check.return_value = {"status": "healthy"}
        mock_movement_service.close_session.return_value = None
        
        app.dependency_overrides[get_movement_service] = lambda: mock_movement_service
        
        try:
            response = client.get("/api/v2/movements/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            
            mock_movement_service.health_check.assert_called_once()
            mock_movement_service.close_session.assert_called_once()
        finally:
            app.dependency_overrides.clear()

    def test_health_check_unhealthy(self, client, mock_movement_service):
        """Test GET /v2/movements/health with unhealthy status."""
        mock_movement_service.health_check.return_value = {"status": "unhealthy", "error": "Database connection failed"}
        mock_movement_service.close_session.return_value = None
        
        app.dependency_overrides[get_movement_service] = lambda: mock_movement_service
        
        try:
            response = client.get("/api/v2/movements/health")
            
            assert response.status_code == 503
            data = response.json()
            assert "detail" in data
            assert data["detail"]["status"] == "unhealthy"
            assert "error" in data["detail"]
        finally:
            app.dependency_overrides.clear()

    def test_health_check_service_error(self, client, mock_movement_service):
        """Test GET /v2/movements/health with service error."""
        mock_movement_service.health_check.side_effect = Exception("Service unavailable")
        mock_movement_service.close_session.return_value = None
        
        app.dependency_overrides[get_movement_service] = lambda: mock_movement_service
        
        try:
            response = client.get("/api/v2/movements/health")
            
            assert response.status_code == 500
            data = response.json()
            assert "detail" in data
            assert "Health check failed" in data["detail"]
        finally:
            app.dependency_overrides.clear()