"""
Model Evaluation Module
=======================
Evaluates trained models and generates performance reports.
"""

import logging
from pathlib import Path

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

logger = logging.getLogger(__name__)


def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    """Compute regression metrics."""
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    mape = np.mean(np.abs((y_true - y_pred) / (y_true + 1e-8))) * 100
    return {"rmse": rmse, "mae": mae, "r2": r2, "mape": mape}


def plot_predictions_vs_actual(
    y_true: np.ndarray, y_pred: np.ndarray, title: str, save_path: str
) -> None:
    """Scatter plot of predicted vs actual values."""
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(y_true, y_pred, alpha=0.3, s=10)
    min_val = min(y_true.min(), y_pred.min())
    max_val = max(y_true.max(), y_pred.max())
    ax.plot([min_val, max_val], [min_val, max_val], "r--", lw=2, label="Perfect Prediction")
    ax.set_xlabel("Actual Traffic Volume")
    ax.set_ylabel("Predicted Traffic Volume")
    ax.set_title(title)
    ax.legend()
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    logger.info("Saved prediction plot: %s", save_path)


def plot_residuals(
    y_true: np.ndarray, y_pred: np.ndarray, title: str, save_path: str
) -> None:
    """Residual distribution plot."""
    residuals = y_true - y_pred

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Residual scatter
    axes[0].scatter(y_pred, residuals, alpha=0.3, s=10)
    axes[0].axhline(y=0, color="r", linestyle="--")
    axes[0].set_xlabel("Predicted Values")
    axes[0].set_ylabel("Residuals")
    axes[0].set_title(f"{title} — Residual Scatter")

    # Residual distribution
    axes[1].hist(residuals, bins=50, edgecolor="black", alpha=0.7)
    axes[1].axvline(x=0, color="r", linestyle="--")
    axes[1].set_xlabel("Residual Value")
    axes[1].set_ylabel("Frequency")
    axes[1].set_title(f"{title} — Residual Distribution")

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    logger.info("Saved residual plot: %s", save_path)


def plot_feature_importance(
    model, feature_names: list[str], title: str, save_path: str, top_n: int = 20
) -> None:
    """Plot feature importance for tree-based models."""
    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
        indices = np.argsort(importances)[::-1][:top_n]

        fig, ax = plt.subplots(figsize=(10, 8))
        ax.barh(
            range(len(indices)),
            importances[indices],
            align="center",
        )
        ax.set_yticks(range(len(indices)))
        ax.set_yticklabels([feature_names[i] for i in indices])
        ax.invert_yaxis()
        ax.set_xlabel("Feature Importance")
        ax.set_title(title)
        plt.tight_layout()
        plt.savefig(save_path, dpi=150)
        plt.close()
        logger.info("Saved feature importance plot: %s", save_path)
    else:
        logger.warning("Model does not support feature_importances_")


def evaluate_by_segment(
    df: pd.DataFrame,
    y_true: np.ndarray,
    y_pred: np.ndarray,
    segment_col: str,
) -> pd.DataFrame:
    """Evaluate model performance segmented by a categorical column."""
    df = df.copy()
    df["y_true"] = y_true
    df["y_pred"] = y_pred

    results = []
    for seg_val, group in df.groupby(segment_col):
        metrics = compute_metrics(group["y_true"].values, group["y_pred"].values)
        metrics["segment"] = seg_val
        metrics["count"] = len(group)
        results.append(metrics)

    return pd.DataFrame(results).set_index("segment")


def run_evaluation(
    model,
    X_test: np.ndarray,
    y_test: np.ndarray,
    feature_names: list[str],
    model_name: str,
    output_dir: str = "reports",
    test_df: pd.DataFrame | None = None,
) -> dict:
    """Run full evaluation pipeline and generate reports."""
    logging.basicConfig(level=logging.INFO)

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    y_pred = model.predict(X_test)
    metrics = compute_metrics(y_test, y_pred)

    # Save metrics
    metrics_df = pd.DataFrame([metrics])
    metrics_df.to_csv(output_path / f"{model_name}_metrics.csv", index=False)

    # Generate plots
    plot_predictions_vs_actual(
        y_test, y_pred,
        f"{model_name} — Predictions vs Actual",
        str(output_path / f"{model_name}_predictions.png"),
    )
    plot_residuals(
        y_test, y_pred,
        model_name,
        str(output_path / f"{model_name}_residuals.png"),
    )
    plot_feature_importance(
        model, feature_names,
        f"{model_name} — Feature Importance",
        str(output_path / f"{model_name}_feature_importance.png"),
    )

    # Segmented evaluation
    if test_df is not None and "Area Name" in test_df.columns:
        seg_metrics = evaluate_by_segment(test_df, y_test, y_pred, "Area Name")
        seg_metrics.to_csv(output_path / f"{model_name}_area_metrics.csv")
        logger.info("Segmented metrics:\n%s", seg_metrics)

    logger.info("Evaluation complete for %s: %s", model_name, metrics)
    return metrics


if __name__ == "__main__":
    # Quick standalone evaluation of saved model
    import yaml
    from src.data_preprocessing import run_preprocessing
    from src.feature_engineering import run_feature_engineering

    with open("configs/config.yaml") as f:
        config = yaml.safe_load(f)

    model = joblib.load("models/best_model.joblib")
    feature_cols = joblib.load(
        Path(config["data"]["processed_dir"]) / "feature_cols.joblib"
    )
    
    train_df, test_df = run_preprocessing("configs/config.yaml")
    train_df, test_df, encoders, scaler = run_feature_engineering(
        train_df, test_df, config
    )

    target = config["data"]["target_column"]
    X_test = np.ascontiguousarray(test_df[feature_cols].values, dtype=np.float32)
    y_test = np.ascontiguousarray(test_df[target].values, dtype=np.float32)

    run_evaluation(model, X_test, y_test, feature_cols, "best_model", test_df=test_df)
