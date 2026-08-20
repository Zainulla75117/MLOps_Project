"""
Feature Engineering Module
==========================
Transforms raw features into model-ready representations.
"""

import logging
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import yaml
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler

logger = logging.getLogger(__name__)


def load_config(config_path: str = "configs/config.yaml") -> dict:
    """Load project configuration from YAML."""
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def extract_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """Extract temporal features from the Date column."""
    df = df.copy()
    df["Date"] = pd.to_datetime(df["Date"])

    df["year"] = df["Date"].dt.year
    df["month"] = df["Date"].dt.month
    df["day_of_week"] = df["Date"].dt.dayofweek  # 0=Mon, 6=Sun
    df["day_of_month"] = df["Date"].dt.day
    df["is_weekend"] = (df["Date"].dt.dayofweek >= 5).astype(int)
    df["quarter"] = df["Date"].dt.quarter
    df["week_of_year"] = df["Date"].dt.isocalendar().week.astype(int)

    logger.info("Extracted time features: year, month, day_of_week, day_of_month, is_weekend, quarter, week_of_year")
    return df


def create_lag_features(df: pd.DataFrame, target_col: str, group_col: str, lag_periods: list[int]) -> pd.DataFrame:
    """
    Create lag features for the target variable, grouped by road/intersection.
    """
    df = df.copy()
    df = df.sort_values(["Date", group_col]).reset_index(drop=True)

    for lag in lag_periods:
        col_name = f"{target_col}_lag_{lag}"
        df[col_name] = df.groupby(group_col)[target_col].shift(lag)
        logger.info("Created lag feature: %s", col_name)

    return df


def create_rolling_features(df: pd.DataFrame, target_col: str, group_col: str, windows: list[int]) -> pd.DataFrame:
    """
    Create rolling mean and std features for the target variable.
    """
    df = df.copy()
    df = df.sort_values(["Date", group_col]).reset_index(drop=True)

    for window in windows:
        mean_col = f"{target_col}_rolling_mean_{window}"
        std_col = f"{target_col}_rolling_std_{window}"

        df[mean_col] = df.groupby(group_col)[target_col].transform(
            lambda x: x.shift(1).rolling(window, min_periods=1).mean()
        )
        df[std_col] = df.groupby(group_col)[target_col].transform(
            lambda x: x.shift(1).rolling(window, min_periods=1).std()
        )
        logger.info("Created rolling features: %s, %s", mean_col, std_col)

    return df


def create_interaction_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create interaction features between correlated variables."""
    df = df.copy()

    # Congestion × Road Capacity interaction
    if "Congestion Level" in df.columns and "Road Capacity Utilization" in df.columns:
        df["congestion_x_capacity"] = df["Congestion Level"] * df["Road Capacity Utilization"]

    # Speed × Travel Time interaction
    if "Average Speed" in df.columns and "Travel Time Index" in df.columns:
        df["speed_x_tti"] = df["Average Speed"] * df["Travel Time Index"]

    # Incident density (incidents relative to congestion)
    if "Incident Reports" in df.columns and "Congestion Level" in df.columns:
        df["incident_density"] = df["Incident Reports"] / (df["Congestion Level"] + 1)

    logger.info("Created interaction features")
    return df


def encode_categorical_features(
    df: pd.DataFrame,
    config: dict,
    encoders: dict | None = None,
    fit: bool = True,
) -> tuple[pd.DataFrame, dict]:
    """
    Encode categorical features:
    - Area Name, Road/Intersection Name → LabelEncoder
    - Weather Conditions → OneHotEncoder
    """
    df = df.copy()
    if encoders is None:
        encoders = {}

    # Label encode Area Name and Road/Intersection Name
    for col in ["Area Name", "Road/Intersection Name"]:
        if col in df.columns:
            if fit:
                le = LabelEncoder()
                df[col] = le.fit_transform(df[col])
                encoders[col] = le
            else:
                le = encoders[col]
                # Handle unseen labels gracefully
                df[col] = df[col].map(lambda x, _le=le: (_le.transform([x])[0] if x in _le.classes_ else -1))
            logger.info("Label-encoded: %s", col)

    # One-hot encode Weather Conditions
    if "Weather Conditions" in df.columns:
        if fit:
            ohe = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
            weather_encoded = ohe.fit_transform(df[["Weather Conditions"]])
            weather_cols = [f"weather_{cat}" for cat in ohe.categories_[0]]
            encoders["Weather Conditions"] = ohe
        else:
            ohe = encoders["Weather Conditions"]
            weather_encoded = ohe.transform(df[["Weather Conditions"]])
            weather_cols = [f"weather_{cat}" for cat in ohe.categories_[0]]

        weather_df = pd.DataFrame(weather_encoded, columns=weather_cols, index=df.index)
        df = pd.concat([df.drop(columns=["Weather Conditions"]), weather_df], axis=1)
        logger.info("One-hot encoded: Weather Conditions → %s", weather_cols)

    return df, encoders


def scale_numeric_features(
    df: pd.DataFrame,
    feature_cols: list[str],
    scaler: StandardScaler | None = None,
    fit: bool = True,
) -> tuple[pd.DataFrame, StandardScaler]:
    """Scale numeric features using StandardScaler."""
    df = df.copy()

    # Only scale columns that exist
    cols_to_scale = [c for c in feature_cols if c in df.columns]

    if fit:
        scaler = StandardScaler()
        df[cols_to_scale] = scaler.fit_transform(df[cols_to_scale])
    else:
        df[cols_to_scale] = scaler.transform(df[cols_to_scale])

    logger.info("Scaled %d numeric features", len(cols_to_scale))
    return df, scaler


def save_artifacts(encoders: dict, scaler: StandardScaler, output_dir: str) -> None:
    """Save encoders and scaler for inference."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    joblib.dump(encoders, output_path / "encoders.joblib")
    joblib.dump(scaler, output_path / "scaler.joblib")
    logger.info("Saved feature engineering artifacts to %s", output_path)


def load_artifacts(output_dir: str) -> tuple[dict, StandardScaler]:
    """Load saved encoders and scaler."""
    output_path = Path(output_dir)
    encoders = joblib.load(output_path / "encoders.joblib")
    scaler = joblib.load(output_path / "scaler.joblib")
    return encoders, scaler


def get_feature_columns(df: pd.DataFrame, target_col: str) -> list[str]:
    """Get all feature column names (excluding target and Date)."""
    exclude = {target_col, "Date"}
    return [c for c in df.columns if c not in exclude]


def run_feature_engineering(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    config: dict,
) -> tuple[pd.DataFrame, pd.DataFrame, dict, StandardScaler]:
    """Execute the full feature engineering pipeline."""
    target = config["data"]["target_column"]
    lag_periods = config["features"].get("lag_periods", [1, 3, 7])
    rolling_windows = config["features"].get("rolling_windows", [7, 30])
    group_col = "Road/Intersection Name"

    # --- Time features ---
    train_df = extract_time_features(train_df)
    test_df = extract_time_features(test_df)

    # --- Lag features (use target before encoding) ---
    train_df = create_lag_features(train_df, target, group_col, lag_periods)
    test_df = create_lag_features(test_df, target, group_col, lag_periods)

    # --- Rolling features ---
    train_df = create_rolling_features(train_df, target, group_col, rolling_windows)
    test_df = create_rolling_features(test_df, target, group_col, rolling_windows)

    # --- Interaction features ---
    train_df = create_interaction_features(train_df)
    test_df = create_interaction_features(test_df)

    # --- Encode categoricals ---
    train_df, encoders = encode_categorical_features(train_df, config, fit=True)
    test_df, _ = encode_categorical_features(test_df, config, encoders=encoders, fit=False)

    # --- Fill NaN from lag/rolling with 0 ---
    train_df.fillna(0, inplace=True)
    test_df.fillna(0, inplace=True)

    # --- Scale numeric features ---
    feature_cols = get_feature_columns(train_df, target)
    numeric_cols = [c for c in feature_cols if train_df[c].dtype in [np.float64, np.int64, np.float32, np.int32]]
    train_df, scaler = scale_numeric_features(train_df, numeric_cols, fit=True)
    test_df, _ = scale_numeric_features(test_df, numeric_cols, scaler=scaler, fit=False)

    # Save artifacts
    save_artifacts(encoders, scaler, config["data"]["processed_dir"])

    return train_df, test_df, encoders, scaler


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    from src.data_preprocessing import run_preprocessing

    config = load_config()
    train_df, test_df = run_preprocessing()
    train_df, test_df, encoders, scaler = run_feature_engineering(train_df, test_df, config)
    print(f"Final train shape: {train_df.shape}")
    print(f"Final test shape: {test_df.shape}")
    print(f"Feature columns: {get_feature_columns(train_df, config['data']['target_column'])}")
