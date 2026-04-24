"""
Pytest suite for AgroAI FastAPI backend.

Tests cover:
- Health check endpoint
- Valid recommendation flow
- Input validation
- Weather fallback behavior
"""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas import SoilInput


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def mock_model_manager():
    """Mock ML model manager with standard prediction."""
    with patch("app.main.model_manager") as mock:
        mock.is_loaded.return_value = True
        mock.predict.return_value = {
            "crop": "Rice",
            "confidence": 0.87,
            "alternatives": ["Wheat", "Maize", "Sugarcane"],
        }
        yield mock


@pytest.fixture
def valid_soil_input():
    """Standard soil input for testing."""
    return {
        "N": 90,
        "P": 42,
        "K": 43,
        "ph": 6.5,
    }


@pytest.fixture
def valid_soil_input_advanced():
    """Soil input with weather coordinates."""
    return {
        "N": 90,
        "P": 42,
        "K": 43,
        "ph": 6.5,
        "temperature": 28,
        "humidity": 82,
        "latitude": 17.3850,
        "longitude": 78.4867,
    }


# ============================================================================
# TESTS
# ============================================================================


class TestHealthEndpoint:
    """Test GET / health check endpoint."""

    def test_health_returns_ok(self, client):
        """GET / should return status=ok."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "ok"
        assert "service" in data
        assert "version" in data
        assert "model_loaded" in data


class TestRecommendEndpoint:
    """Test POST /recommend endpoint."""

    def test_recommend_valid_payload(self, client, mock_model_manager, valid_soil_input):
        """POST /recommend with valid input returns 200 with correct schema."""
        response = client.post("/recommend", json=valid_soil_input)

        assert response.status_code == 200
        data = response.json()

        # Verify response schema
        assert "soil_analysis" in data
        assert "crop_recommendation" in data
        assert "fertilizer_plan" in data
        assert "alerts" in data
        assert "weather_used" in data

        # Verify soil_analysis structure
        soil = data["soil_analysis"]
        assert "n_level" in soil
        assert "p_level" in soil
        assert "k_level" in soil
        assert "ph_status" in soil
        assert "health_score" in soil
        assert "health_label" in soil

        # Verify crop_recommendation structure
        crop = data["crop_recommendation"]
        assert "crop" in crop
        assert crop["crop"] == "Rice"
        assert "confidence" in crop
        assert isinstance(crop["confidence"], float)
        assert 0 <= crop["confidence"] <= 1
        assert "alternatives" in crop
        assert isinstance(crop["alternatives"], list)
        assert len(crop["alternatives"]) == 3

        # Verify fertilizer_plan is a list
        assert isinstance(data["fertilizer_plan"], list)

        # Verify alerts is a list
        assert isinstance(data["alerts"], list)

        # Verify weather_used is False (basic endpoint)
        assert data["weather_used"] is False

    def test_recommend_missing_required_field(self, client, mock_model_manager):
        """POST /recommend with missing required field returns 422."""
        invalid_input = {
            "N": 90,
            "P": 42,
            "K": 43,
            # Missing 'ph'
        }

        response = client.post("/recommend", json=invalid_input)

        assert response.status_code == 422

    def test_recommend_invalid_field_type(self, client, mock_model_manager):
        """POST /recommend with invalid field type returns 422."""
        invalid_input = {
            "N": "ninety",  # Should be float
            "P": 42,
            "K": 43,
            "ph": 6.5,
        }

        response = client.post("/recommend", json=invalid_input)

        assert response.status_code == 422

    def test_recommend_field_out_of_range(self, client, mock_model_manager):
        """POST /recommend with out-of-range value returns 422."""
        invalid_input = {
            "N": 250,  # Max is 200
            "P": 42,
            "K": 43,
            "ph": 6.5,
        }

        response = client.post("/recommend", json=invalid_input)

        assert response.status_code == 422

    def test_recommend_ph_out_of_range(self, client, mock_model_manager):
        """POST /recommend with pH > 14 returns 422."""
        invalid_input = {
            "N": 90,
            "P": 42,
            "K": 43,
            "ph": 15.0,  # Max is 14
        }

        response = client.post("/recommend", json=invalid_input)

        assert response.status_code == 422


class TestAdvancedRecommendEndpoint:
    """Test POST /recommend-advanced endpoint with weather integration."""

    def test_advanced_requires_coordinates(
        self, client, mock_model_manager, valid_soil_input
    ):
        """POST /recommend-advanced without coordinates returns 422."""
        # Input missing latitude/longitude
        response = client.post("/recommend-advanced", json=valid_soil_input)

        assert response.status_code == 422
        data = response.json()
        assert "latitude" in data["detail"] or "longitude" in data["detail"]

    def test_advanced_with_weather_api_success(
        self, client, mock_model_manager, valid_soil_input_advanced
    ):
        """POST /recommend-advanced with valid weather API response."""
        mock_weather = {
            "temperature": 28.5,
            "humidity": 81.0,
            "city": "Hyderabad",
            "description": "Partly cloudy",
        }

        with patch("app.main.is_weather_available", return_value=True):
            with patch("app.main.fetch_weather", return_value=mock_weather):
                response = client.post("/recommend-advanced", json=valid_soil_input_advanced)

        assert response.status_code == 200
        data = response.json()

        # Should use weather
        assert data["weather_used"] is True

        # Verify all response fields present
        assert "soil_analysis" in data
        assert "crop_recommendation" in data
        assert "fertilizer_plan" in data
        assert "alerts" in data

    def test_advanced_weather_fallback_no_api_key(
        self, client, mock_model_manager, valid_soil_input_advanced
    ):
        """POST /recommend-advanced falls back when API key not set."""
        # Simulate no API key configured
        with patch("app.main.is_weather_available", return_value=False):
            response = client.post("/recommend-advanced", json=valid_soil_input_advanced)

        assert response.status_code == 200
        data = response.json()

        # Should NOT use weather (fallback)
        assert data["weather_used"] is False

        # Should still return valid response
        assert "soil_analysis" in data
        assert "crop_recommendation" in data
        assert "fertilizer_plan" in data
        assert "alerts" in data

    def test_advanced_weather_api_failure_fallback(
        self, client, mock_model_manager, valid_soil_input_advanced
    ):
        """POST /recommend-advanced handles weather API failure gracefully."""
        from app.weather import WeatherAPIError

        # API key exists but request fails
        with patch("app.main.is_weather_available", return_value=True):
            with patch(
                "app.main.fetch_weather",
                side_effect=WeatherAPIError("API timeout"),
            ):
                response = client.post("/recommend-advanced", json=valid_soil_input_advanced)

        assert response.status_code == 200
        data = response.json()

        # Should fallback gracefully
        assert data["weather_used"] is False

        # Should include warning alert
        assert isinstance(data["alerts"], list)
        warning_found = any(
            "Weather data unavailable" in alert for alert in data["alerts"]
        )
        assert warning_found

        # Should still return valid response with all fields
        assert "soil_analysis" in data
        assert "crop_recommendation" in data
        assert "fertilizer_plan" in data

    def test_advanced_weather_network_error(
        self, client, mock_model_manager, valid_soil_input_advanced
    ):
        """POST /recommend-advanced handles network errors."""
        import requests

        from app.weather import WeatherAPIError

        # Simulate network timeout
        with patch("app.main.is_weather_available", return_value=True):
            with patch(
                "app.main.fetch_weather",
                side_effect=WeatherAPIError("Connection timeout"),
            ):
                response = client.post("/recommend-advanced", json=valid_soil_input_advanced)

        assert response.status_code == 200
        data = response.json()

        # Should fallback
        assert data["weather_used"] is False


class TestResponseSchema:
    """Test response schema validation."""

    def test_recommend_response_structure(self, client, mock_model_manager, valid_soil_input):
        """Verify RecommendResponse structure."""
        response = client.post("/recommend", json=valid_soil_input)

        assert response.status_code == 200
        data = response.json()

        # Top-level fields
        required_fields = [
            "soil_analysis",
            "crop_recommendation",
            "fertilizer_plan",
            "alerts",
            "weather_used",
        ]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"

        # Soil analysis fields
        soil = data["soil_analysis"]
        soil_fields = ["n_level", "p_level", "k_level", "ph_status", "health_score", "health_label"]
        for field in soil_fields:
            assert field in soil, f"Missing soil_analysis field: {field}"

        # Crop recommendation fields
        crop = data["crop_recommendation"]
        crop_fields = ["crop", "confidence", "alternatives"]
        for field in crop_fields:
            assert field in crop, f"Missing crop_recommendation field: {field}"

        # Type checks
        assert isinstance(data["fertilizer_plan"], list)
        assert isinstance(data["alerts"], list)
        assert isinstance(data["weather_used"], bool)
        assert isinstance(crop["confidence"], float)
        assert isinstance(crop["alternatives"], list)
        assert isinstance(soil["health_score"], (int, float))

    def test_fertilizer_recommendation_fields(
        self, client, mock_model_manager, valid_soil_input
    ):
        """Verify each FertilizerRecommendation has required fields."""
        response = client.post("/recommend", json=valid_soil_input)

        assert response.status_code == 200
        data = response.json()

        # Check if fertilizer plan has items
        if len(data["fertilizer_plan"]) > 0:
            for item in data["fertilizer_plan"]:
                assert "name" in item
                assert "amount" in item
                assert "reason" in item
                assert isinstance(item["name"], str)
                assert isinstance(item["amount"], str)
                assert isinstance(item["reason"], str)


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_recommend_minimum_values(self, client, mock_model_manager):
        """POST /recommend with minimum valid values."""
        input_data = {
            "N": 0,
            "P": 0,
            "K": 0,
            "ph": 0,
        }

        response = client.post("/recommend", json=input_data)

        assert response.status_code == 200

    def test_recommend_maximum_values(self, client, mock_model_manager):
        """POST /recommend with maximum valid values."""
        input_data = {
            "N": 200,
            "P": 200,
            "K": 300,
            "ph": 14,
        }

        response = client.post("/recommend", json=input_data)

        assert response.status_code == 200

    def test_recommend_optional_fields(self, client, mock_model_manager):
        """POST /recommend with optional temperature/humidity."""
        input_data = {
            "N": 90,
            "P": 42,
            "K": 43,
            "ph": 6.5,
            "temperature": 25.5,
            "humidity": 70.0,
        }

        response = client.post("/recommend", json=input_data)

        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
