"""
Model Training Module
=====================
Trains multiple regression models with MLflow experiment tracking
and Optuna hyperparameter optimization.
"""

import logging
from pathlib import Path

import joblib
import mlflow
import mlflow.sklearn
import mlflow.xgboost
import numpy as np
import optuna
import xgboost as xgb
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import TimeSeriesSplit, cross_val_score

from src.data_preprocessing import load_config, run_preprocessing
from src.feature_engineering import (
    get_feature_columns,
    run_feature_engineering,
)

logger = logging.getLogger(__name__)

optuna.logging.set_verbosity(optuna.logging.WARNING)


# ===========================================================================
# Metrics
# ===========================================================================


def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    """Compute regression metrics."""
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    mape = np.mean(np.abs((y_true - y_pred) / (y_true + 1e-8))) * 100
    return {"rmse": rmse, "mae": mae, "r2": r2, "mape": mape}


# ===========================================================================
# Optuna Objective Functions
# ===========================================================================


def _rf_objective(trial, X_train, y_train):
    """Optuna objective for Random Forest."""
    params = {
        "n_estimators": trial.suggest_int("n_estimators", 100, 500),
        "max_depth": trial.suggest_int("max_depth", 5, 30),
        "min_samples_split": trial.suggest_int("min_samples_split", 2, 20),
        "min_samples_leaf": trial.suggest_int("min_samples_leaf", 1, 10),
        "max_features": trial.suggest_categorical("max_features", ["sqrt", "log2", None]),
    }
    model = RandomForestRegressor(**params, random_state=42, n_jobs=-1)
    tscv = TimeSeriesSplit(n_splits=5)
    scores = cross_val_score(model, X_train, y_train, cv=tscv, scoring="neg_root_mean_squared_error")
    return -scores.mean()


def _xgb_objective(trial, X_train, y_train):
    """Optuna objective for XGBoost."""
    params = {
        "n_estimators": trial.suggest_int("n_estimators", 100, 1000),
        "max_depth": trial.suggest_int("max_depth", 3, 12),
        "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
        "subsample": trial.suggest_float("subsample", 0.6, 1.0),
        "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
        "reg_alpha": trial.suggest_float("reg_alpha", 1e-8, 10.0, log=True),
        "reg_lambda": trial.suggest_float("reg_lambda", 1e-8, 10.0, log=True),
        "min_child_weight": trial.suggest_int("min_child_weight", 1, 10),
    }
    model = xgb.XGBRegressor(**params, random_state=42, n_jobs=-1, verbosity=0)
    tscv = TimeSeriesSplit(n_splits=5)
    scores = cross_val_score(model, X_train, y_train, cv=tscv, scoring="neg_root_mean_squared_error")
    return -scores.mean()


# ===========================================================================
# Training Functions
# ===========================================================================


def train_baseline(X_train, y_train, X_test, y_test):
    """Train Linear Regression baseline."""
    logger.info("Training baseline: Linear Regression")
    model = LinearRegression()
    model.fit(X_train, y_train)

    train_metrics = compute_metrics(y_train, model.predict(X_train))
    test_metrics = compute_metrics(y_test, model.predict(X_test))

    with mlflow.start_run(run_name="linear_regression"):
        mlflow.log_params({"model_type": "linear_regression"})
        for k, v in test_metrics.items():
            mlflow.log_metric(f"test_{k}", v)
        for k, v in train_metrics.items():
            mlflow.log_metric(f"train_{k}", v)
        mlflow.sklearn.log_model(model, name="model")

    logger.info("Baseline test metrics: %s", test_metrics)
    return model, test_metrics


def train_with_optuna(
    model_name: str,
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_test: np.ndarray,
    y_test: np.ndarray,
    n_trials: int = 50,
):
    """Train a model with Optuna hyperparameter optimization."""
    logger.info("Training %s with Optuna (%d trials)", model_name, n_trials)

    objective_map = {
        "random_forest": (_rf_objective, RandomForestRegressor),
        "xgboost": (_xgb_objective, xgb.XGBRegressor),
    }

    obj_func, ModelClass = objective_map[model_name]

    study = optuna.create_study(direction="minimize")
    study.optimize(
        lambda trial: obj_func(trial, X_train, y_train),
        n_trials=n_trials,
        show_progress_bar=True,
    )

    best_params = study.best_params
    logger.info("Best params for %s: %s", model_name, best_params)

    # Train final model with best params
    extra_kwargs = {}
    if model_name == "random_forest":
        extra_kwargs = {"random_state": 42, "n_jobs": -1}
    elif model_name == "xgboost":
        extra_kwargs = {"random_state": 42, "n_jobs": -1, "verbosity": 0}

    model = ModelClass(**best_params, **extra_kwargs)
    model.fit(X_train, y_train)

    train_metrics = compute_metrics(y_train, model.predict(X_train))
    test_metrics = compute_metrics(y_test, model.predict(X_test))

    # Log to MLflow
    with mlflow.start_run(run_name=model_name):
        mlflow.log_params(best_params)
        mlflow.log_param("model_type", model_name)
        mlflow.log_param("optuna_trials", n_trials)
        for k, v in test_metrics.items():
            mlflow.log_metric(f"test_{k}", v)
        for k, v in train_metrics.items():
            mlflow.log_metric(f"train_{k}", v)

        # Log model with the appropriate flavor
        if model_name == "xgboost":
            mlflow.xgboost.log_model(model, name="model")
        else:
            mlflow.sklearn.log_model(model, name="model")

    logger.info("%s test metrics: %s", model_name, test_metrics)
    return model, test_metrics, best_params


def select_best_model(results: dict) -> str:
    """Select the best model based on test RMSE."""
    best_name = min(results, key=lambda k: results[k]["metrics"]["rmse"])
    logger.info("Best model: %s (RMSE=%.4f)", best_name, results[best_name]["metrics"]["rmse"])
    return best_name


def save_model(model, name: str, output_dir: str = "models") -> str:
    """Save model artifact locally."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    model_path = output_path / f"{name}.joblib"
    joblib.dump(model, model_path)
    logger.info("Saved model to %s", model_path)
    return str(model_path)


def register_best_model(model_name: str, run_id: str, config: dict):
    """Register the best model in MLflow Model Registry."""
    registry_name = config["mlflow"]["registry_name"]
    model_uri = f"runs:/{run_id}/model"

    result = mlflow.register_model(model_uri, registry_name)
    logger.info(
        "Registered model '%s' version %s from run %s",
        registry_name,
        result.version,
        run_id,
    )
    return result


# ===========================================================================
# Main Training Pipeline
# ===========================================================================


def run_training(config_path: str = "configs/config.yaml"):
    """Execute the full training pipeline."""
    logging.basicConfig(level=logging.INFO)

    config = load_config(config_path)

    # Setup MLflow
    mlflow.set_tracking_uri(config["mlflow"]["tracking_uri"])
    mlflow.set_experiment(config["mlflow"]["experiment_name"])

    # --- Data prep ---
    train_df, test_df = run_preprocessing(config_path)
    train_df, test_df, encoders, scaler = run_feature_engineering(train_df, test_df, config)

    target = config["data"]["target_column"]
    feature_cols = get_feature_columns(train_df, target)

    X_train = np.ascontiguousarray(train_df[feature_cols].values, dtype=np.float32)
    y_train = np.ascontiguousarray(train_df[target].values, dtype=np.float32)
    X_test = np.ascontiguousarray(test_df[feature_cols].values, dtype=np.float32)
    y_test = np.ascontiguousarray(test_df[target].values, dtype=np.float32)

    logger.info(
        "Features: %d, Train: %d, Test: %d",
        len(feature_cols),
        len(X_train),
        len(X_test),
    )

    # Save feature column names for inference
    joblib.dump(feature_cols, Path(config["data"]["processed_dir"]) / "feature_cols.joblib")

    # --- Train models ---
    results = {}
    n_trials = config["training"].get("optuna_trials", 50)

    # Baseline
    model, metrics = train_baseline(X_train, y_train, X_test, y_test)
    results["linear_regression"] = {"model": model, "metrics": metrics}

    # Optimized models
    for model_name in ["random_forest", "xgboost"]:
        model, metrics, params = train_with_optuna(model_name, X_train, y_train, X_test, y_test, n_trials=n_trials)
        results[model_name] = {"model": model, "metrics": metrics, "params": params}

    # --- Select & save best model ---
    best_name = select_best_model(results)
    save_model(results[best_name]["model"], "best_model")

    # Print comparison
    print("\n" + "=" * 70)
    print("MODEL COMPARISON")
    print("=" * 70)
    print(f"{'Model':<20} {'RMSE':>10} {'MAE':>10} {'R²':>10} {'MAPE':>10}")
    print("-" * 70)
    for name, res in results.items():
        m = res["metrics"]
        marker = " ★" if name == best_name else ""
        print(f"{name:<20} {m['rmse']:>10.2f} {m['mae']:>10.2f} {m['r2']:>10.4f} {m['mape']:>9.2f}%{marker}")
    print("=" * 70)

    return results, best_name


if __name__ == "__main__":
    run_training()
