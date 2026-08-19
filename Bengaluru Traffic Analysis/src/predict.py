"""
FastAPI Prediction Service
==========================
Real-time traffic volume prediction API.
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import yaml
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# ===========================================================================
# Request / Response Schemas
# ===========================================================================

class TrafficFeatures(BaseModel):
    """Input features for traffic volume prediction."""

    date: str = Field(..., description="Date in YYYY-MM-DD format", examples=["2024-06-15"])
    area_name: str = Field(..., description="Area name", examples=["Koramangala"])
    road_name: str = Field(..., description="Road/Intersection name", examples=["Sarjapur Road"])
    average_speed: float = Field(..., ge=0, description="Average speed (km/h)")
    travel_time_index: float = Field(..., ge=1.0, description="Travel time index")
    congestion_level: float = Field(..., ge=0, le=100, description="Congestion level (0-100)")
    road_capacity_utilization: float = Field(..., ge=0, le=100, description="Road capacity utilization (%)")
    incident_reports: int = Field(..., ge=0, description="Number of incident reports")
    public_transport_usage: float = Field(..., ge=0, description="Public transport usage (%)")
    traffic_signal_compliance: float = Field(..., ge=0, le=100, description="Traffic signal compliance (%)")
    parking_usage: float = Field(..., ge=0, le=100, description="Parking usage (%)")
    pedestrian_cyclist_count: int = Field(..., ge=0, description="Pedestrian and cyclist count")
    weather_conditions: str = Field(..., description="Weather conditions", examples=["Clear"])
    roadwork_activity: str = Field(..., description="Roadwork and construction activity (Yes/No)", examples=["No"])


class PredictionResponse(BaseModel):
    """Prediction output."""

    predicted_traffic_volume: float
    area: str
    road: str
    confidence_note: str = "Point estimate from the best trained model"


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    model_loaded: bool
    version: str


# ===========================================================================
# App State
# ===========================================================================

class AppState:
    """Holds loaded model and preprocessing artifacts."""

    def __init__(self):
        self.model = None
        self.encoders = None
        self.scaler = None
        self.feature_cols = None
        self.config = None


state = AppState()


# ===========================================================================
# Startup / Shutdown
# ===========================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load model and artifacts on startup."""
    logger.info("Loading model and artifacts...")

    config_path = Path("configs/config.yaml")
    with open(config_path) as f:
        state.config = yaml.safe_load(f)

    processed_dir = Path(state.config["data"]["processed_dir"])

    state.model = joblib.load("models/best_model.joblib")
    state.encoders = joblib.load(processed_dir / "encoders.joblib")
    state.scaler = joblib.load(processed_dir / "scaler.joblib")
    state.feature_cols = joblib.load(processed_dir / "feature_cols.joblib")

    logger.info("Model and artifacts loaded successfully.")
    yield
    logger.info("Shutting down...")


# ===========================================================================
# FastAPI App
# ===========================================================================

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Bengaluru Traffic Volume Prediction API",
    description="Real-time traffic volume prediction for Bengaluru roads using ML",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

def _prepare_features(features: TrafficFeatures) -> np.ndarray:
    """
    Transform API input into the feature vector expected by the model.
    Applies the same transformations as the training pipeline.
    """
    # Build a single-row DataFrame matching the raw schema
    row = {
        "Date": features.date,
        "Area Name": features.area_name,
        "Road/Intersection Name": features.road_name,
        "Average Speed": features.average_speed,
        "Travel Time Index": features.travel_time_index,
        "Congestion Level": features.congestion_level,
        "Road Capacity Utilization": features.road_capacity_utilization,
        "Incident Reports": features.incident_reports,
        "Public Transport Usage": features.public_transport_usage,
        "Traffic Signal Compliance": features.traffic_signal_compliance,
        "Parking Usage": features.parking_usage,
        "Pedestrian and Cyclist Count": features.pedestrian_cyclist_count,
        "Weather Conditions": features.weather_conditions,
        "Roadwork and Construction Activity": 1 if features.roadwork_activity == "Yes" else 0,
    }
    df = pd.DataFrame([row])
    df["Date"] = pd.to_datetime(df["Date"])

    # --- Time features ---
    df["year"] = df["Date"].dt.year
    df["month"] = df["Date"].dt.month
    df["day_of_week"] = df["Date"].dt.dayofweek
    df["day_of_month"] = df["Date"].dt.day
    df["is_weekend"] = (df["Date"].dt.dayofweek >= 5).astype(int)
    df["quarter"] = df["Date"].dt.quarter
    df["week_of_year"] = df["Date"].dt.isocalendar().week.astype(int)

    # --- Interaction features ---
    df["congestion_x_capacity"] = df["Congestion Level"] * df["Road Capacity Utilization"]
    df["speed_x_tti"] = df["Average Speed"] * df["Travel Time Index"]
    df["incident_density"] = df["Incident Reports"] / (df["Congestion Level"] + 1)

    # --- Encode categoricals ---
    for col in ["Area Name", "Road/Intersection Name"]:
        le = state.encoders.get(col)
        if le is not None:
            if df[col].iloc[0] in le.classes_:
                df[col] = le.transform(df[col])
            else:
                df[col] = -1

    # One-hot encode weather
    ohe = state.encoders.get("Weather Conditions")
    if ohe is not None:
        weather_encoded = ohe.transform(df[["Weather Conditions"]])
        weather_cols = [f"weather_{cat}" for cat in ohe.categories_[0]]
        weather_df = pd.DataFrame(weather_encoded, columns=weather_cols, index=df.index)
        df = pd.concat([df.drop(columns=["Weather Conditions"]), weather_df], axis=1)

    # --- Lag/rolling features (set to 0 for single prediction — no history) ---
    for col in state.feature_cols:
        if col not in df.columns:
            df[col] = 0

    # Drop Date column
    if "Date" in df.columns:
        df.drop(columns=["Date"], inplace=True)

    # Reorder and select only expected features
    df = df[state.feature_cols]

    # Scale numeric features
    numeric_cols = [
        c for c in state.feature_cols
        if df[c].dtype in [np.float64, np.int64, np.float32, np.int32]
    ]
    if state.scaler is not None:
        cols_in_scaler = [c for c in numeric_cols if c in state.feature_cols]
        df[cols_in_scaler] = state.scaler.transform(df[cols_in_scaler])

    return df.values


# ===========================================================================
# Endpoints
# ===========================================================================

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Service health check."""
    return HealthResponse(
        status="healthy",
        model_loaded=state.model is not None,
        version="1.0.0",
    )


@app.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
async def predict(features: TrafficFeatures):
    """Predict traffic volume for given features."""
    if state.model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        X = _prepare_features(features)
        prediction = state.model.predict(X)[0]

        return PredictionResponse(
            predicted_traffic_volume=round(float(prediction), 2),
            area=features.area_name,
            road=features.road_name,
        )
    except Exception as e:
        logger.error("Prediction error: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.get("/model/info", tags=["Model"])
async def model_info():
    """Get information about the loaded model."""
    return {
        "model_type": type(state.model).__name__,
        "n_features": len(state.feature_cols) if state.feature_cols else 0,
        "feature_names": state.feature_cols,
    }

@app.get("/cors-test")
async def cors_test():
    return {"message": "Server is updated!"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
