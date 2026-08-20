"""
Data Drift Monitoring Module
=============================
Detects data drift using Evidently AI and generates reports.
"""

import logging
from datetime import datetime
from pathlib import Path

import pandas as pd
import yaml
from evidently import ColumnMapping
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, DataQualityPreset
from evidently.metrics import (
    DatasetDriftMetric,
)
from evidently.test_suite import TestSuite
from evidently.tests import (
    TestNumberOfDrifted,
    TestShareOfDrifted,
    TestColumnDrift,
)

logger = logging.getLogger(__name__)


def load_config(config_path: str = "configs/config.yaml") -> dict:
    """Load project configuration."""
    with open(config_path) as f:
        return yaml.safe_load(f)


def get_column_mapping(config: dict) -> ColumnMapping:
    """Define column mapping for Evidently."""
    return ColumnMapping(
        target=config["data"]["target_column"],
        numerical_features=[
            "Average Speed",
            "Travel Time Index",
            "Congestion Level",
            "Road Capacity Utilization",
            "Incident Reports",
            "Public Transport Usage",
            "Traffic Signal Compliance",
            "Parking Usage",
            "Pedestrian and Cyclist Count",
        ],
        categorical_features=[
            "Area Name",
            "Road/Intersection Name",
            "Weather Conditions",
            "Roadwork and Construction Activity",
        ],
    )


def generate_drift_report(
    reference_data: pd.DataFrame,
    current_data: pd.DataFrame,
    config: dict,
    output_dir: str | None = None,
) -> dict:
    """
    Generate a data drift report comparing reference vs current data.

    Returns:
        dict with drift detection results and report path.
    """
    if output_dir is None:
        output_dir = config["monitoring"]["drift_report_dir"]

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    column_mapping = get_column_mapping(config)

    # --- Drift Report ---
    drift_report = Report(
        metrics=[
            DatasetDriftMetric(),
            DataDriftPreset(),
        ]
    )
    drift_report.run(
        reference_data=reference_data,
        current_data=current_data,
        column_mapping=column_mapping,
    )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = output_path / f"drift_report_{timestamp}.html"
    drift_report.save_html(str(report_path))
    logger.info("Drift report saved to %s", report_path)

    # Extract drift results
    report_dict = drift_report.as_dict()
    dataset_drift = False
    drift_share = 0.0

    for metric_result in report_dict.get("metrics", []):
        metric_id = metric_result.get("metric", "")
        if "DatasetDriftMetric" in metric_id:
            result = metric_result.get("result", {})
            dataset_drift = result.get("dataset_drift", False)
            drift_share = result.get("drift_share", 0.0)
            break

    return {
        "dataset_drift_detected": dataset_drift,
        "drift_share": drift_share,
        "report_path": str(report_path),
        "timestamp": timestamp,
    }


def run_drift_tests(
    reference_data: pd.DataFrame,
    current_data: pd.DataFrame,
    config: dict,
    output_dir: str | None = None,
) -> dict:
    """
    Run automated drift tests.

    Returns:
        dict with test results and pass/fail status.
    """
    if output_dir is None:
        output_dir = config["monitoring"]["drift_report_dir"]

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    column_mapping = get_column_mapping(config)
    drift_threshold = config["monitoring"].get("drift_threshold", 0.05)

    # --- Test Suite ---
    test_suite = TestSuite(
        tests=[
            TestNumberOfDrifted(lt=5),
            TestShareOfDrifted(lt=drift_threshold),
            TestColumnDrift(column_name="Average Speed"),
            TestColumnDrift(column_name="Congestion Level"),
            TestColumnDrift(column_name="Traffic Volume"),
        ]
    )

    test_suite.run(
        reference_data=reference_data,
        current_data=current_data,
        column_mapping=column_mapping,
    )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_report_path = output_path / f"drift_tests_{timestamp}.html"
    test_suite.save_html(str(test_report_path))
    logger.info("Drift test report saved to %s", test_report_path)

    test_dict = test_suite.as_dict()
    all_passed = test_dict.get("summary", {}).get("all_passed", False)

    return {
        "all_tests_passed": all_passed,
        "test_report_path": str(test_report_path),
        "summary": test_dict.get("summary", {}),
        "timestamp": timestamp,
    }


def generate_data_quality_report(
    reference_data: pd.DataFrame,
    current_data: pd.DataFrame,
    config: dict,
    output_dir: str | None = None,
) -> str:
    """Generate a data quality report."""
    if output_dir is None:
        output_dir = config["monitoring"]["drift_report_dir"]

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    column_mapping = get_column_mapping(config)

    quality_report = Report(metrics=[DataQualityPreset()])
    quality_report.run(
        reference_data=reference_data,
        current_data=current_data,
        column_mapping=column_mapping,
    )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = output_path / f"data_quality_{timestamp}.html"
    quality_report.save_html(str(report_path))
    logger.info("Data quality report saved to %s", report_path)
    return str(report_path)


def run_monitoring(config_path: str = "configs/config.yaml"):
    """Execute the full monitoring pipeline."""
    logging.basicConfig(level=logging.INFO)
    config = load_config(config_path)

    # Load reference (training) and current (latest) data
    ref_path = config["monitoring"]["reference_data_path"]
    reference_data = pd.read_csv(ref_path)

    # In production, current_data would come from the serving layer or database.
    # For demo, we use the test set.
    processed_dir = config["data"]["processed_dir"]
    current_data = pd.read_csv(Path(processed_dir) / "test.csv")

    # Generate reports
    drift_result = generate_drift_report(reference_data, current_data, config)
    test_result = run_drift_tests(reference_data, current_data, config)
    quality_path = generate_data_quality_report(reference_data, current_data, config)

    print("\n" + "=" * 60)
    print("MONITORING RESULTS")
    print("=" * 60)
    print(f"Dataset Drift Detected: {drift_result['dataset_drift_detected']}")
    print(f"Drift Share: {drift_result['drift_share']:.2%}")
    print(f"All Tests Passed: {test_result['all_tests_passed']}")
    print(f"\nDrift Report: {drift_result['report_path']}")
    print(f"Test Report: {test_result['test_report_path']}")
    print(f"Quality Report: {quality_path}")

    if drift_result["dataset_drift_detected"]:
        logger.warning("⚠️ DATASET DRIFT DETECTED — consider retraining the model!")

    return drift_result, test_result


if __name__ == "__main__":
    run_monitoring()
