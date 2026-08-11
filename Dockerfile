# ===========================================================
# Multi-stage Dockerfile for Bengaluru Traffic MLOps
# ===========================================================
# Stage 1: Training image (includes all ML dependencies)
# Stage 2: Serving image (lightweight FastAPI only)
# ===========================================================

# ---- Stage 1: Training ----
FROM python:3.13-slim AS trainer

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Default: run training
CMD ["python", "-m", "src.train"]


# ---- Stage 2: Serving ----
FROM python:3.13-slim AS server

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Install only serving dependencies
RUN pip install --no-cache-dir \
    fastapi>=0.104.0 \
    "uvicorn[standard]>=0.24.0" \
    pydantic>=2.5.0 \
    pandas>=2.0.0 \
    numpy>=1.24.0 \
    scikit-learn>=1.3.0 \
    xgboost>=2.0.0 \
    joblib>=1.3.0 \
    pyyaml>=6.0.0

# Copy only what's needed for serving
COPY src/ ./src/
COPY configs/ ./configs/
COPY models/ ./models/
COPY data/processed/ ./data/processed/

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "src.predict:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
