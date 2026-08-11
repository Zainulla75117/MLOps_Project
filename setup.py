from setuptools import setup, find_packages

setup(
    name="bengaluru-traffic-mlops",
    version="1.0.0",
    description="MLOps pipeline for Bengaluru traffic volume prediction",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "scikit-learn>=1.3.0",
        "xgboost>=2.0.0",
        "lightgbm>=4.0.0",
        "optuna>=3.4.0",
        "mlflow>=2.9.0",
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "pydantic>=2.5.0",
        "evidently>=0.4.0",
        "pyyaml>=6.0.0",
        "joblib>=1.3.0",
    ],
)
