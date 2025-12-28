# Installation Guide

This guide covers the complete setup of the Wine Quality ML project.

## Prerequisites

Before you begin, ensure you have the following installed:

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.11.x | Runtime |
| Poetry | 1.8+ | Dependency management |
| Git | 2.40+ | Version control |
| Docker | 24+ | Containerization (optional) |

## Step 1: Clone Repository

```bash
git clone https://github.com/7Askar7/EPML-ITMO.git
cd EPML-ITMO
```

## Step 2: Install Dependencies

### Using Poetry (Recommended)

```bash
# Install all dependencies
poetry install

# Activate virtual environment
poetry shell

# Install pre-commit hooks
poetry run pre-commit install
```

### Using pip

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows

# Install from pyproject.toml
pip install .
```

## Step 3: Download Data

The dataset is managed by DVC:

```bash
# Pull data from DVC remote
poetry run dvc pull

# Verify data exists
ls data/raw/
# Should show: winequality-red.csv
```

If DVC remote is not configured, download manually:

```bash
curl -o data/raw/winequality-red.csv \
  "https://archive.ics.uci.edu/ml/machine-learning-databases/wine-quality/winequality-red.csv"

# Process data
poetry run python -m src.data.make_dataset
```

## Step 4: Verify Installation

Run the test suite to verify everything works:

```bash
# Run tests
poetry run pytest

# Run linting
poetry run ruff check src/

# Run type checking
poetry run mypy src/
```

## Optional: ClearML Setup

For ClearML MLOps platform:

### 1. Start ClearML Server

```bash
# Copy environment template
cp .env.clearml.example .env.clearml

# Start ClearML (requires Docker)
make clearml-server-up

# Access UI at http://localhost:8090
# Login: admin / admin
```

### 2. Configure Credentials

1. Open http://localhost:8090
2. Go to Settings → Workspace → Create new credentials
3. Copy `access_key` and `secret_key`
4. Update `.env.clearml`:

```bash
CLEARML_API_ACCESS_KEY=your_access_key
CLEARML_API_SECRET_KEY=your_secret_key
```

### 3. Verify ClearML

```bash
# Run pipeline
make clearml-pipeline

# Check results in UI
```

## Optional: MLflow Setup

MLflow is configured automatically. To access the UI:

```bash
# Start MLflow UI
make mlflow-ui

# Access at http://localhost:5000
```

## Docker Installation

Build and run the project in Docker:

```bash
# Build image
make docker-build

# Run container
make docker-run
```

## Troubleshooting

### Poetry Installation Issues

```bash
# Update Poetry
poetry self update

# Clear cache
poetry cache clear --all pypi

# Reinstall
rm -rf .venv poetry.lock
poetry install
```

### DVC Pull Fails

```bash
# Check remote configuration
dvc remote list

# Pull with verbose output
dvc pull -v
```

### ClearML Connection Issues

```bash
# Check Docker containers
docker ps --filter "name=clearml"

# Check API health
curl http://localhost:8008/debug.ping

# Restart services
make clearml-server-down
make clearml-server-up
```

## Next Steps

- [Quick Start](quickstart.md) - Run your first experiment
- [API Reference](api/data.md) - Explore the codebase
