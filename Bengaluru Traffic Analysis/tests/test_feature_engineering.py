"""
Tests for feature_engineering module.
"""

import numpy as np
import pandas as pd
import pytest

from src.feature_engineering import (
    create_interaction_features,
    create_lag_features,
    create_rolling_features,
    encode_categorical_features,
    extract_time_features,
)


@pytest.fixture
def sample_df():
    """Create a sample DataFrame for feature engineering tests."""
    return pd.DataFrame(
        {
            "Date": pd.date_range("2024-01-01", periods=10, freq="D"),
            "Area Name": ["Koramangala"] * 5 + ["Indiranagar"] * 5,
            "Road/Intersection Name": ["Sarjapur Road"] * 5 + ["100 Feet Road"] * 5,
            "Traffic Volume": [
                30000,
                35000,
                28000,
                42000,
                38000,
                25000,
                32000,
                29000,
                40000,
                36000,
            ],
            "Average Speed": [
                40.5,
                35.2,
                45.1,
                30.8,
                33.5,
                42.0,
                38.0,
                44.0,
                31.0,
                35.0,
            ],
            "Travel Time Index": [1.5, 1.3, 1.1, 1.5, 1.4, 1.2, 1.3, 1.1, 1.5, 1.4],
            "Congestion Level": [90, 80, 60, 100, 95, 70, 85, 65, 98, 88],
            "Road Capacity Utilization": [95, 85, 70, 100, 90, 75, 88, 68, 97, 85],
            "Incident Reports": [2, 1, 0, 3, 1, 0, 2, 1, 3, 2],
            "Weather Conditions": [
                "Clear",
                "Rain",
                "Clear",
                "Fog",
                "Overcast",
                "Clear",
                "Rain",
                "Clear",
                "Fog",
                "Clear",
            ],
            "Roadwork and Construction Activity": [0, 1, 0, 0, 1, 0, 0, 1, 0, 0],
            "Public Transport Usage": [45, 50, 55, 60, 48, 42, 52, 58, 62, 46],
            "Traffic Signal Compliance": [85, 90, 92, 78, 82, 88, 91, 94, 76, 84],
            "Parking Usage": [70, 65, 75, 80, 72, 68, 63, 77, 82, 70],
            "Pedestrian and Cyclist Count": [
                100,
                95,
                110,
                85,
                90,
                105,
                98,
                112,
                88,
                93,
            ],
        }
    )


@pytest.fixture
def sample_config():
    return {
        "data": {
            "target_column": "Traffic Volume",
        },
        "features": {
            "categorical": [
                "Area Name",
                "Road/Intersection Name",
                "Weather Conditions",
            ],
            "binary": ["Roadwork and Construction Activity"],
        },
    }


class TestExtractTimeFeatures:
    def test_creates_time_columns(self, sample_df):
        result = extract_time_features(sample_df)
        expected_cols = [
            "year",
            "month",
            "day_of_week",
            "day_of_month",
            "is_weekend",
            "quarter",
            "week_of_year",
        ]
        for col in expected_cols:
            assert col in result.columns, f"Missing column: {col}"

    def test_is_weekend_values(self, sample_df):
        result = extract_time_features(sample_df)
        assert set(result["is_weekend"].unique()).issubset({0, 1})

    def test_preserves_original_columns(self, sample_df):
        original_cols = set(sample_df.columns)
        result = extract_time_features(sample_df)
        assert original_cols.issubset(set(result.columns))


class TestLagFeatures:
    def test_creates_lag_columns(self, sample_df):
        result = create_lag_features(
            sample_df, "Traffic Volume", "Road/Intersection Name", [1, 3]
        )
        assert "Traffic Volume_lag_1" in result.columns
        assert "Traffic Volume_lag_3" in result.columns

    def test_lag_1_has_nan(self, sample_df):
        result = create_lag_features(
            sample_df, "Traffic Volume", "Road/Intersection Name", [1]
        )
        # First row per group should have NaN
        assert result["Traffic Volume_lag_1"].isna().any()


class TestRollingFeatures:
    def test_creates_rolling_columns(self, sample_df):
        result = create_rolling_features(
            sample_df, "Traffic Volume", "Road/Intersection Name", [3]
        )
        assert "Traffic Volume_rolling_mean_3" in result.columns
        assert "Traffic Volume_rolling_std_3" in result.columns


class TestInteractionFeatures:
    def test_creates_interaction_columns(self, sample_df):
        result = create_interaction_features(sample_df)
        assert "congestion_x_capacity" in result.columns
        assert "speed_x_tti" in result.columns
        assert "incident_density" in result.columns

    def test_interaction_values(self, sample_df):
        result = create_interaction_features(sample_df)
        expected = (
            sample_df["Congestion Level"] * sample_df["Road Capacity Utilization"]
        )
        pd.testing.assert_series_equal(
            result["congestion_x_capacity"], expected, check_names=False
        )


class TestEncodeCategorical:
    def test_encodes_area_name(self, sample_df, sample_config):
        result, encoders = encode_categorical_features(
            sample_df, sample_config, fit=True
        )
        assert result["Area Name"].dtype in [np.int32, np.int64, int]
        assert "Area Name" in encoders

    def test_one_hot_encodes_weather(self, sample_df, sample_config):
        result, encoders = encode_categorical_features(
            sample_df, sample_config, fit=True
        )
        assert "Weather Conditions" not in result.columns
        weather_cols = [c for c in result.columns if c.startswith("weather_")]
        assert len(weather_cols) > 0

    def test_transform_mode(self, sample_df, sample_config):
        _, encoders = encode_categorical_features(sample_df, sample_config, fit=True)
        result, _ = encode_categorical_features(
            sample_df, sample_config, encoders=encoders, fit=False
        )
        assert "Weather Conditions" not in result.columns
