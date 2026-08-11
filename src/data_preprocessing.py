"""
Data Preprocessing Module
=========================
Handles loading, cleaning, and splitting the Bengaluru traffic dataset.
"""

import logging
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from sklearn.model_selection import train_test_split

logger = logging.getLogger(__name__)


def load_config(config_path: str = "configs/config.yaml") -> dict:
    """Load project configuration from YAML."""
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def load_raw_data(path: str) -> pd.DataFrame:
    """Load the raw CSV dataset."""
    logger.info("Loading raw data from %s", path)
    df = pd.read_csv(path)
    logger.info("Loaded %d rows × %d columns", df.shape[0], df.shape[1])
    return df


def clean_data(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    """
    Clean the raw dataset:
    - Parse Date column
    - Drop data-leak columns (Environmental Impact)
    - Convert binary columns to 0/1
    - Remove duplicates
    """
    df = df.copy()

    # Parse date
    df["Date"] = pd.to_datetime(df["Date"])

    # Drop data-leak columns
    drop_cols = config["data"].get("drop_columns", [])
    existing_drop = [c for c in drop_cols if c in df.columns]
    if existing_drop:
        logger.info("Dropping data-leak columns: %s", existing_drop)
        df.drop(columns=existing_drop, inplace=True)

    # Convert binary columns
    for col in config["features"].get("binary", []):
        if col in df.columns:
            df[col] = df[col].map({"Yes": 1, "No": 0}).astype(int)
            logger.info("Encoded binary column: %s", col)

    # Remove duplicates
    n_dups = df.duplicated().sum()
    if n_dups > 0:
        logger.info("Removing %d duplicate rows", n_dups)
        df.drop_duplicates(inplace=True)

    # Drop rows with any NaN in the target
    target = config["data"]["target_column"]
    df.dropna(subset=[target], inplace=True)

    logger.info("Cleaned data: %d rows × %d columns", df.shape[0], df.shape[1])
    return df


def split_data(
    df: pd.DataFrame, config: dict
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Time-aware train/test split.
    Sorts by date, then splits to avoid data leakage from future dates.
    """
    test_size = config["data"].get("test_size", 0.2)
    random_state = config["data"].get("random_state", 42)

    # Sort by date for time-series integrity
    df = df.sort_values("Date").reset_index(drop=True)

    # Use a chronological split rather than random for time-series data
    split_idx = int(len(df) * (1 - test_size))
    train_df = df.iloc[:split_idx].copy()
    test_df = df.iloc[split_idx:].copy()

    logger.info(
        "Split data: train=%d rows, test=%d rows", len(train_df), len(test_df)
    )
    return train_df, test_df


def save_processed_data(
    train_df: pd.DataFrame, test_df: pd.DataFrame, output_dir: str
) -> None:
    """Save processed train and test sets to CSV."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    train_path = output_path / "train.csv"
    test_path = output_path / "test.csv"

    train_df.to_csv(train_path, index=False)
    test_df.to_csv(test_path, index=False)
    logger.info("Saved processed data to %s", output_path)


def run_preprocessing(config_path: str = "configs/config.yaml") -> tuple[pd.DataFrame, pd.DataFrame]:
    """Execute the full preprocessing pipeline."""
    logging.basicConfig(level=logging.INFO)

    config = load_config(config_path)
    df = load_raw_data(config["data"]["raw_path"])
    df = clean_data(df, config)
    train_df, test_df = split_data(df, config)
    save_processed_data(train_df, test_df, config["data"]["processed_dir"])

    return train_df, test_df


if __name__ == "__main__":
    run_preprocessing()
