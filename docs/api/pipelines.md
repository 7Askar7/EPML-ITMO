# Pipelines Module

This module contains pipeline runners for orchestrating ML workflows.

## Overview

The pipelines module provides:

- Hydra-based experiment configuration
- ClearML pipeline integration
- DVC pipeline stages

## Module Reference

### Hydra Pipeline

**File:** `src/pipelines/run_hydra_pipeline.py`

Main function for running experiments with Hydra configuration:

```python
def run_pipeline(algorithm_variant: str = "quick", min_experiments: int = 4) -> dict:
    """Run ML experiments based on Hydra configuration.

    Args:
        algorithm_variant: Which algorithm set to use (quick/full)
        min_experiments: Minimum number of experiments required

    Returns:
        Dictionary with experiment results and summary
    """
```

### ClearML Pipeline

**File:** `src/pipelines/clearml_pipeline.py`

Main function for running the ClearML-integrated pipeline:

```python
def run_clearml_pipeline(
    variant: str | None = None,
    config_path: Path | str | None = None,
    skip_registry: bool = False,
) -> dict[str, Any]:
    """Run the end-to-end workflow with ClearML tracking.

    Args:
        variant: Hydra algorithms variant (full/quick)
        config_path: Path to ClearML config YAML
        skip_registry: Skip model registry publication

    Returns:
        Dictionary with experiment results
    """
```

## Pipeline Types

### 1. DVC Pipeline

Defined in `dvc.yaml`:

```yaml
stages:
  split:
    cmd: python -m src.data.make_dataset
    deps:
      - data/raw/winequality-red.csv
    outs:
      - data/processed/train.csv
      - data/processed/test.csv

  train:
    cmd: python -m src.models.train_model
    deps:
      - data/processed/train.csv
      - data/processed/test.csv
    outs:
      - models/wine_quality_model.pkl
```

Run with:

```bash
poetry run dvc repro
```

### 2. Hydra Pipeline

Configuration-driven experiment runner:

```bash
# Quick experiments (4 models)
poetry run python -m src.pipelines.run_hydra_pipeline algorithms=quick

# Full experiments (15+ models)
poetry run python -m src.pipelines.run_hydra_pipeline algorithms=full
```

### 3. ClearML Pipeline

Full MLOps workflow with ClearML:

```bash
# Start ClearML server
make clearml-server-up

# Run pipeline
make clearml-pipeline

# View at http://localhost:8090
```

## Usage Examples

### Run Hydra Pipeline Programmatically

```python
from src.pipelines.run_hydra_pipeline import run_pipeline

results = run_pipeline(
    algorithm_variant="quick",
    min_experiments=4
)

print(f"Completed {len(results['experiments'])} experiments")
```

### Run ClearML Pipeline

```python
from src.pipelines.clearml_pipeline import run_clearml_pipeline

results = run_clearml_pipeline(
    variant="quick",
    config_path="configs/clearml/config.yaml",
    skip_registry=False
)
```

## Configuration

### Hydra Config Structure

```
configs/hydra/
├── config.yaml           # Base configuration
└── algorithms/
    ├── quick.yaml        # 4 experiments
    └── full.yaml         # 15+ experiments
```

### ClearML Config

```yaml
# configs/clearml/config.yaml
project_name: "wine-quality-clearml"
pipeline:
  name: "wine-quality-pipeline"
  queue: "services"
  schedule: "0 6 * * *"  # Daily at 6 AM

server:
  api: "http://localhost:8008"
  web: "http://localhost:8090"
  files: "http://localhost:8091"
```

## Pipeline Outputs

| Pipeline | Outputs |
|----------|---------|
| DVC | `models/*.pkl`, `data/processed/*` |
| Hydra | `reports/figures/experiments/*` |
| ClearML | Task artifacts, Model Registry |

## Monitoring

### MLflow

```bash
make mlflow-ui
# http://localhost:5000
```

### ClearML

```bash
make clearml-server-up
# http://localhost:8090
```

Metrics available:

- Accuracy, F1, Precision, Recall
- Confusion matrices
- Training duration
- Model artifacts
