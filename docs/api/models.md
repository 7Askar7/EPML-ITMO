# Models Module

This module contains model training, experiment tracking, and batch experiment runners.

## Overview

The models module provides:

- Model training with MLflow logging
- Experiment tracking utilities
- Batch experiment runner for multiple configurations
- Support for various classifiers

## Supported Models

| Estimator | Class | Description |
|-----------|-------|-------------|
| `logreg` | LogisticRegression | Baseline linear model |
| `random_forest` | RandomForestClassifier | Ensemble of decision trees |
| `gradient_boosting` | GradientBoostingClassifier | Gradient boosted trees |
| `svc` | SVC | Support Vector Classifier |
| `knn` | KNeighborsClassifier | K-Nearest Neighbors |
| `adaboost` | AdaBoostClassifier | Adaptive boosting |

## Module Reference

### Train Model

**File:** `src/models/train_model.py`

```python
def load_processed_data(processed_dir: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load train and test datasets from processed directory.

    Args:
        processed_dir: Path to processed data directory

    Returns:
        Tuple of (train_df, test_df)
    """

def train_and_save_model(
    processed_dir: str = "data/processed",
    model_dir: str = "models"
) -> tuple[BaseEstimator, dict]:
    """Train model and save to disk with MLflow logging.

    Args:
        processed_dir: Path to processed data
        model_dir: Directory to save model

    Returns:
        Tuple of (trained_model, metrics_dict)
    """
```

### Experiment Tracker

**File:** `src/models/experiment_tracker.py`

```python
def log_experiment(
    run_name: str,
    experiment_name: str = "wine-quality",
    tracking_uri: str = "sqlite:///mlflow.db",
    tags: dict | None = None
) -> Callable:
    """Decorator for logging experiments to MLflow.

    Args:
        run_name: Name of the MLflow run
        experiment_name: Name of the experiment
        tracking_uri: MLflow tracking URI
        tags: Optional tags to add

    Returns:
        Decorated function
    """

def get_data_version(dvc_lock_path: str) -> str | None:
    """Extract data version hash from dvc.lock file.

    Args:
        dvc_lock_path: Path to dvc.lock

    Returns:
        MD5 hash of data or None
    """
```

### Run Experiments

**File:** `src/models/run_experiments.py`

```python
@dataclass
class ExperimentSpec:
    """Specification for a single experiment."""
    name: str
    estimator: str  # logreg, random_forest, gradient_boosting, svc, knn, adaboost
    params: dict[str, Any]

def run_batch(
    experiments: list[ExperimentSpec] | None = None,
    base_tags: dict[str, str] | None = None,
    min_experiments: int = 15,
    log_to_clearml: bool = False,
    register_models: bool = True,
) -> dict[str, Any]:
    """Run a batch of experiments with MLflow/ClearML tracking.

    Args:
        experiments: List of experiment specifications
        base_tags: Tags to add to all experiments
        min_experiments: Minimum required experiments
        log_to_clearml: Enable ClearML logging
        register_models: Register models in registry

    Returns:
        Dictionary with experiments, summary, and artifacts
    """
```

## Usage Examples

### Basic Training

```python
from src.models.train_model import train_and_save_model

# Train with default settings
model, metrics = train_and_save_model(
    processed_dir="data/processed",
    model_dir="models"
)

print(f"Accuracy: {metrics['accuracy']:.4f}")
```

### Run Experiments Batch

```python
from src.models.run_experiments import run_batch, ExperimentSpec

# Define experiments
experiments = [
    ExperimentSpec("rf_100", "random_forest", {"n_estimators": 100}),
    ExperimentSpec("logreg_c1", "logreg", {"C": 1.0, "max_iter": 500}),
]

# Run batch
results = run_batch(
    experiments=experiments,
    min_experiments=2,
    log_to_clearml=False
)

# Get best model
best = results["summary"].iloc[0]
print(f"Best: {best['tags.model_name']} (acc={best['metrics.accuracy']:.4f})")
```

### With MLflow Tracking

```python
from src.models.experiment_tracker import log_experiment

@log_experiment(
    run_name="my_experiment",
    experiment_name="wine-quality",
    tags={"version": "1.0"}
)
def train_model():
    # Your training code here
    return {"accuracy": 0.85, "f1": 0.82}
```

## MLflow Integration

All experiments are logged to MLflow automatically:

```bash
# View experiments
make mlflow-ui

# Access at http://localhost:5000
```

Logged artifacts include:

- Model parameters
- Metrics (accuracy, F1, precision, recall)
- Confusion matrix plots
- Classification reports
- Trained model files

## Hydra Configuration

Experiments can be configured via Hydra:

```yaml
# configs/hydra/algorithms/quick.yaml
experiments:
  - name: logreg_c1
    estimator: logreg
    params:
      C: 1.0
      max_iter: 500
  - name: rf_50
    estimator: random_forest
    params:
      n_estimators: 50
      max_depth: 8
```

Run with:

```bash
poetry run python -m src.pipelines.run_hydra_pipeline algorithms=quick
```
