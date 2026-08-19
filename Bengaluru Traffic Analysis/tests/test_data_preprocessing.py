"""
Tests for data_preprocessing module.
"""

import os
import tempfile

import pandas as pd
import pytest

from src.data_preprocessing import clean_data, load_config, load_raw_data, split_data


@pytest.fixture
def sample_config():
    """Minimal config for testing."""
    return {
        "data": {
            "raw_path": "dataset/Banglore_traffic_Dataset.csv",
            "processed_dir": "data/processed",
            "test_size": 0.2,
            "random_state": 42,
            "target_column": "Traffic Volume",
            "drop_columns": ["Environmental Impact"],
        },
        "features": {
            "binary": ["Roadwork and Construction Activity"],
        },
    }


@pytest.fixture
def sample_df():
    """Create a sample DataFrame matching the dataset schema."""
    return pd.DataFrame(
        {
            "Date": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"],
            "Area Name": ["Koramangala"] * 3 + ["Indiranagar"] * 2,
            "Road/Intersection Name": ["Sarjapur Road"] * 3 + ["100 Feet Road"] * 2,
            "Traffic Volume": [30000, 35000, 28000, 42000, 38000],
            "Average Speed": [40.5, 35.2, 45.1, 30.8, 33.5],
            "Travel Time Index": [1.5, 1.3, 1.1, 1.5, 1.4],
            "Congestion Level": [90.0, 80.0, 60.0, 100.0, 95.0],
            "Road Capacity Utilization": [95.0, 85.0, 70.0, 100.0, 90.0],
            "Incident Reports": [2, 1, 0, 3, 1],
            "Environmental Impact": [110.0, 120.0, 95.0, 140.0, 125.0],
            "Public Transport Usage": [45.0, 50.0, 55.0, 60.0, 48.0],
            "Traffic Signal Compliance": [85.0, 90.0, 92.0, 78.0, 82.0],
            "Parking Usage": [70.0, 65.0, 75.0, 80.0, 72.0],
            "Pedestrian and Cyclist Count": [100, 95, 110, 85, 90],
            "Weather Conditions": ["Clear", "Rain", "Clear", "Fog", "Overcast"],
            "Roadwork and Construction Activity": ["No", "Yes", "No", "No", "Yes"],
        }
    )


class TestCleanData:
    """Tests for the clean_data function."""

    def test_drops_environmental_impact(self, sample_df, sample_config):
        """Environmental Impact should be dropped (data leak)."""
        result = clean_data(sample_df, sample_config)
        assert "Environmental Impact" not in result.columns

    def test_encodes_binary_columns(self, sample_df, sample_config):
        """Roadwork and Construction Activity should be 0/1."""
        result = clean_data(sample_df, sample_config)
        assert result["Roadwork and Construction Activity"].dtype in [int, "int64", "int32"]
        assert set(result["Roadwork and Construction Activity"].unique()).issubset({0, 1})

    def test_parses_date(self, sample_df, sample_config):
        """Date column should be datetime."""
        result = clean_data(sample_df, sample_config)
        assert pd.api.types.is_datetime64_any_dtype(result["Date"])

    def test_no_data_loss_on_clean_data(self, sample_df, sample_config):
        """No rows should be lost when data is already clean."""
        result = clean_data(sample_df, sample_config)
        assert len(result) == len(sample_df)

    def test_preserves_target_column(self, sample_df, sample_config):
        """Target column should not be dropped."""
        result = clean_data(sample_df, sample_config)
        assert "Traffic Volume" in result.columns


class TestSplitData:
    """Tests for the split_data function."""

    def test_split_sizes(self, sample_df, sample_config):
        """Train/test sizes should respect the configured ratio."""
        sample_df["Date"] = pd.to_datetime(sample_df["Date"])
        train, test = split_data(sample_df, sample_config)
        assert len(train) + len(test) == len(sample_df)
        assert len(test) > 0
        assert len(train) > 0

    def test_chronological_order(self, sample_df, sample_config):
        """Train dates should come before test dates."""
        sample_df["Date"] = pd.to_datetime(sample_df["Date"])
        train, test = split_data(sample_df, sample_config)
        assert train["Date"].max() <= test["Date"].min()
