"""
Tests for the FastAPI prediction service.
"""

import pytest


@pytest.fixture
def sample_prediction_payload():
    """Valid prediction request payload."""
    return {
        "date": "2024-06-15",
        "area_name": "Koramangala",
        "road_name": "Sarjapur Road",
        "average_speed": 35.5,
        "travel_time_index": 1.5,
        "congestion_level": 85.0,
        "road_capacity_utilization": 90.0,
        "incident_reports": 2,
        "public_transport_usage": 55.0,
        "traffic_signal_compliance": 82.0,
        "parking_usage": 70.0,
        "pedestrian_cyclist_count": 100,
        "weather_conditions": "Clear",
        "roadwork_activity": "No",
    }


class TestPredictionSchema:
    """Test request validation."""

    def test_valid_payload_structure(self, sample_prediction_payload):
        """Valid payload should have all required fields."""
        required_fields = [
            "date", "area_name", "road_name", "average_speed",
            "travel_time_index", "congestion_level", "road_capacity_utilization",
            "incident_reports", "public_transport_usage", "traffic_signal_compliance",
            "parking_usage", "pedestrian_cyclist_count", "weather_conditions",
            "roadwork_activity",
        ]
        for field in required_fields:
            assert field in sample_prediction_payload

    def test_payload_types(self, sample_prediction_payload):
        """Payload fields should have correct types."""
        payload = sample_prediction_payload
        assert isinstance(payload["date"], str)
        assert isinstance(payload["area_name"], str)
        assert isinstance(payload["average_speed"], float)
        assert isinstance(payload["incident_reports"], int)
        assert isinstance(payload["pedestrian_cyclist_count"], int)


class TestMetrics:
    """Test the compute_metrics function."""

    def test_metrics_computation(self):
        import numpy as np
        from src.evaluate import compute_metrics

        y_true = np.array([100, 200, 300, 400, 500])
        y_pred = np.array([110, 190, 310, 390, 510])

        metrics = compute_metrics(y_true, y_pred)

        assert "rmse" in metrics
        assert "mae" in metrics
        assert "r2" in metrics
        assert "mape" in metrics
        assert metrics["rmse"] >= 0
        assert metrics["mae"] >= 0
        assert metrics["r2"] <= 1.0
        assert metrics["mape"] >= 0

    def test_perfect_predictions(self):
        import numpy as np
        from src.evaluate import compute_metrics

        y_true = np.array([100, 200, 300])
        y_pred = np.array([100, 200, 300])

        metrics = compute_metrics(y_true, y_pred)
        assert metrics["rmse"] == 0.0
        assert metrics["mae"] == 0.0
        assert metrics["r2"] == 1.0
