# Quick Start Guide

Get up and running with Wine Quality ML in minutes.

## TL;DR

```bash
git clone https://github.com/7Askar7/EPML-ITMO.git
cd EPML-ITMO
poetry install
poetry run dvc pull
make train
```

## 1. Train a Model

Train the default Random Forest model:

```bash
make train
```

This will:

- Load processed train/test data
- Train a RandomForestClassifier
- Log metrics to MLflow
- Register model in MLflow Model Registry
- Save model to `models/wine_quality_model.pkl`

## 2. Run Experiments

Run a batch of 15+ experiments with different models:

```bash
# Quick variant (4 experiments)
make experiments algorithms=quick

# Full variant (15+ experiments)
make experiments algorithms=full
```

Results are saved to:

- `reports/figures/experiments/experiments_summary.png`
- `reports/figures/experiments/experiments_top10.csv`

## 3. View Results in MLflow

```bash
make mlflow-ui
```

Open http://localhost:5000 to:

- Compare experiments
- View metrics and parameters
- Download artifacts
- Manage model registry

## 4. Run with ClearML

For full MLOps workflow with ClearML:

```bash
# Start ClearML server (requires Docker)
make clearml-server-up

# Run pipeline with ClearML tracking
make clearml-pipeline

# View results at http://localhost:8090
```

## 5. Use Hydra Configurations

Customize experiments with Hydra:

```bash
# Use full algorithm set
poetry run python -m src.pipelines.run_hydra_pipeline algorithms=full

# Override parameters
poetry run python -m src.pipelines.run_hydra_pipeline \
    algorithms=quick \
    algorithms.min_experiments=2
```

Configuration files:

- `configs/hydra/config.yaml` - Base config
- `configs/hydra/algorithms/quick.yaml` - Quick experiments
- `configs/hydra/algorithms/full.yaml` - Full experiments

## 6. Run DVC Pipeline

Execute the full reproducible pipeline:

```bash
# Run pipeline
make pipeline

# Or with DVC directly
poetry run dvc repro
```

Pipeline stages:

1. `split` - Create train/test splits
2. `train` - Train model
3. `experiments` - Run experiment batch

## Common Commands

| Command | Description |
|---------|-------------|
| `make install` | Install dependencies |
| `make train` | Train model |
| `make experiments` | Run experiments |
| `make pipeline` | Full DVC pipeline |
| `make mlflow-ui` | Start MLflow UI |
| `make clearml-server-up` | Start ClearML |
| `make clearml-pipeline` | Run ClearML pipeline |
| `make test` | Run tests |
| `make lint` | Check code quality |
| `make format` | Format code |
| `make docs-serve` | Local documentation |

## Example: Custom Experiment

Create a custom experiment programmatically:

```python
from src.models.run_experiments import run_batch, ExperimentSpec

# Define custom experiments
experiments = [
    ExperimentSpec(
        name="my_rf_model",
        estimator="random_forest",
        params={"n_estimators": 100, "max_depth": 10}
    ),
    ExperimentSpec(
        name="my_logreg",
        estimator="logreg",
        params={"C": 1.0, "max_iter": 500}
    ),
]

# Run batch
results = run_batch(
    experiments=experiments,
    min_experiments=2,
    log_to_clearml=True  # Enable ClearML tracking
)

print(f"Best accuracy: {results['summary'].iloc[0]['metrics.accuracy']:.4f}")
```

## Next Steps

- [API Reference](api/models.md) - Detailed API documentation
- [HW5 Report](REPORT_HW5.md) - ClearML integration details
- [HW6 Report](REPORT_HW6.md) - Documentation setup
