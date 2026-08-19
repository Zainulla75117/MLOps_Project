# Bengaluru Traffic Volume Prediction — MLOps Project

End-to-end MLOps pipeline for predicting traffic volume across Bengaluru's major roads and intersections.

## Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Dataset    │────▶│ Preprocessing│────▶│   Training   │────▶│  Evaluation  │
│   (CSV/DVC)  │     │  & Features  │     │  (MLflow)    │     │  & Metrics   │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
                                                                       │
                                                                       ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Monitoring  │◀────│   AWS EKS    │◀────│    Docker     │◀────│   FastAPI    │
│ (Evidently)  │     │  (K8s Deploy)│     │   (ECR)      │     │   Service    │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
```

## Dataset

| Property | Value |
|----------|-------|
| Source | Bengaluru Traffic Dataset |
| Rows | 8,937 |
| Features | 16 (14 used after dropping data leak) |
| Target | Traffic Volume |
| Date Range | 2022-01-01 → 2024-08-09 |
| Areas Covered | Koramangala, M.G. Road, Indiranagar, Hebbal, Jayanagar, Whitefield, Yeshwanthpur, Electronic City |

## Quick Start

### Prerequisites
- Python 3.10+
- Docker & Docker Compose
- AWS CLI (configured)
- Terraform >= 1.15.8

### Local Development

```bash
# 1. Clone & install
git clone <repo-url>
cd MLOps_Project
pip install -r requirements.txt

# 2. Run the ML pipeline
python -m src.data_preprocessing
python -m src.train
python -m src.evaluate

# 3. Start the API
uvicorn src.predict:app --reload --port 8000

# 4. Run monitoring
python -m src.monitor
```

### Docker

```bash
# Start API + MLflow
docker-compose up -d

# Run training job
docker-compose --profile training up trainer

# Access
# API:    http://localhost:8000/docs
# MLflow: http://localhost:5000
```

### DVC Pipeline

```bash
dvc init
dvc repro          # Run full pipeline
dvc metrics show   # Show metrics
dvc plots show     # Show plots
```

## Infrastructure (Terraform)

Provisions on AWS `ap-south-1`:
- **VPC** — Public/private subnets across 2 AZs, NAT gateways
- **EKS** — Kubernetes 1.36 with managed node group (t3.small)
- **ECR** — Container registry with image scanning
- **S3** — MLflow artifacts + DVC remote (encrypted, versioned)

```bash
cd terraform
terraform init
terraform plan -out=plan.out
terraform apply plan.out
```

## Project Structure

```
├── src/
│   ├── data_preprocessing.py   # Data loading & cleaning
│   ├── feature_engineering.py  # Feature transformations
│   ├── train.py                # Model training (MLflow + Optuna)
│   ├── evaluate.py             # Evaluation & plots
│   ├── predict.py              # FastAPI prediction API
│   └── monitor.py              # Evidently data drift
├── tests/                      # Unit tests
├── configs/config.yaml         # Central configuration
├── k8s/                        # Kubernetes manifests
│   ├── deployment.yaml         # 2-replica deployment
│   ├── service.yaml            # ClusterIP service
│   ├── ingress.yaml            # ALB ingress
│   ├── hpa.yaml                # Autoscaler (2-10 pods)
│   └── configmap.yaml          # Environment config
├── terraform/                  # AWS infrastructure
│   ├── modules/
│   │   ├── vpc/                # Networking
│   │   ├── eks/                # Kubernetes cluster
│   │   ├── ecr/                # Container registry
│   │   └── s3/                 # Object storage
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
├── .github/workflows/ci-cd.yaml
├── Dockerfile
├── docker-compose.yaml
├── dvc.yaml
└── requirements.txt
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Service health check |
| `POST` | `/predict` | Predict traffic volume |
| `GET` | `/model/info` | Model metadata |
| `GET` | `/docs` | Swagger UI |

### Example Request

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
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
    "roadwork_activity": "No"
  }'
```

## CI/CD Pipeline

| Trigger | Stage | Actions |
|---------|-------|---------|
| PR to `main` | Lint & Test | flake8, black, pytest |
| Push to `main` | Train & Build | Retrain model → Build Docker → Push to ECR |
| Tag `v*` | Deploy | Deploy to EKS via `kubectl apply` |

## Models

- **Baseline**: Linear Regression
- **Random Forest** (Optuna-tuned)
- **XGBoost** (Optuna-tuned)
- **LightGBM** (Optuna-tuned)

Best model selected by test RMSE, tracked in MLflow.

## Monitoring

Data drift detection using **Evidently AI**:
- Dataset drift report
- Column-level drift tests
- Data quality report
- Automated alerts when drift exceeds threshold

## License

MIT
