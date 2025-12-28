# MLOps Module

This module provides ClearML integration utilities for experiment tracking, model registry, and notifications.

## Overview

The MLOps module provides:

- ClearML task initialization
- Metrics and parameter logging
- Model registration
- Artifact management
- Webhook notifications

## Module Reference

**File:** `src/mlops/clearml_utils.py`

### Core Functions

```python
def load_clearml_config(config_path: Path | str | None = None) -> dict[str, Any]:
    """Load ClearML configuration from YAML file.

    Args:
        config_path: Path to config file (defaults to configs/clearml/config.yaml)

    Returns:
        Configuration dictionary
    """

def init_task(
    cfg: dict[str, Any],
    task_name: str,
    task_type: str = "training",
    tags: dict[str, str] | None = None,
    force_create: bool = False,
) -> Task:
    """Initialize a ClearML Task with common defaults.

    Args:
        cfg: Configuration dictionary
        task_name: Name of the task
        task_type: Type (training, testing, monitor, etc.)
        tags: Optional tags
        force_create: Use Task.create() instead of Task.init()

    Returns:
        ClearML Task object
    """

def log_params_and_metrics(
    task: Task,
    params: dict[str, Any],
    metrics: dict[str, float] | None = None
) -> None:
    """Log parameters and metrics to ClearML task."""

def log_confusion_matrix(
    task: Task,
    y_true: np.ndarray,
    y_pred: np.ndarray,
    labels: list[str] | None = None
) -> None:
    """Log confusion matrix visualization."""

def register_model(
    task: Task,
    model_path: Path,
    name: str,
    comment: str = "",
    metadata: dict[str, Any] | None = None,
) -> str | None:
    """Register model in ClearML Model Registry."""

def upload_artifacts(task: Task, artifacts: list[Path]) -> None:
    """Upload artifact files to ClearML."""

def send_notification(message: str, webhook: str | None) -> None:
    """Send notification to webhook (e.g., Slack)."""
```

## ClearML Server Setup

### Start Server

```bash
# Copy environment template
cp .env.clearml.example .env.clearml

# Start all services
make clearml-server-up
```

### Services

| Service | Port | Description |
|---------|------|-------------|
| API Server | 8008 | REST API |
| Web Server | 8090 | Web UI |
| File Server | 8091 | Artifact storage |
| MongoDB | 27017 | Database |
| Redis | 6379 | Cache |
| Elasticsearch | 9200 | Search |

### Access UI

Open http://localhost:8090

- **Login:** admin
- **Password:** admin

## Usage Examples

### Initialize Task

```python
from src.mlops.clearml_utils import init_task, load_clearml_config

cfg = load_clearml_config("configs/clearml/config.yaml")

task = init_task(
    cfg,
    task_name="my-experiment",
    task_type="training",
    tags={"version": "1.0", "author": "user"}
)
```

### Log Metrics

```python
from src.mlops.clearml_utils import log_params_and_metrics

log_params_and_metrics(
    task,
    params={"learning_rate": 0.01, "epochs": 100},
    metrics={"accuracy": 0.85, "f1": 0.82}
)
```

### Log Confusion Matrix

```python
from src.mlops.clearml_utils import log_confusion_matrix
import numpy as np

y_true = np.array([0, 1, 1, 0, 1])
y_pred = np.array([0, 1, 0, 0, 1])

log_confusion_matrix(
    task,
    y_true=y_true,
    y_pred=y_pred,
    labels=["bad", "good"]
)
```

### Register Model

```python
from src.mlops.clearml_utils import register_model
from pathlib import Path

model_id = register_model(
    task,
    model_path=Path("models/my_model.pkl"),
    name="wine-quality-model",
    comment="Best performing model",
    metadata={"accuracy": 0.85}
)
```

### Upload Artifacts

```python
from src.mlops.clearml_utils import upload_artifacts
from pathlib import Path

artifacts = [
    Path("reports/confusion_matrix.png"),
    Path("reports/classification_report.txt")
]

upload_artifacts(task, artifacts)
```

### Send Notification

```python
from src.mlops.clearml_utils import send_notification

send_notification(
    message="Training completed! Accuracy: 0.85",
    webhook="https://hooks.slack.com/services/XXX"
)
```

## Configuration

### Environment Variables

```bash
# .env.clearml
CLEARML_API_HOST=http://localhost:8008
CLEARML_WEB_HOST=http://localhost:8090
CLEARML_FILES_HOST=http://localhost:8091
CLEARML_API_ACCESS_KEY=your_key
CLEARML_API_SECRET_KEY=your_secret
```

### YAML Configuration

```yaml
# configs/clearml/config.yaml
project_name: "wine-quality-clearml"

pipeline:
  name: "wine-quality-pipeline"
  queue: "services"

server:
  api: "http://localhost:8008"
  web: "http://localhost:8090"
  files: "http://localhost:8091"

models:
  registry_name: "wine-quality-registry"
  tags:
    owner: "epml"
    stage: "staging"

notifications:
  slack_webhook: ""
  on_success: true
  on_failure: true
```

## Docker Compose

ClearML server is managed via Docker Compose:

```bash
# Start
make clearml-server-up

# Stop
make clearml-server-down

# View logs
docker compose -f infra/clearml/docker-compose.yml logs -f

# Check status
docker ps --filter "name=clearml"
```

## Troubleshooting

### Connection Issues

```bash
# Check API health
curl http://localhost:8008/debug.ping

# Expected: {"status":"ok"}
```

### Authentication Errors

1. Verify credentials in `.env.clearml`
2. Check API key in ClearML UI (Settings → Workspace)
3. Restart services: `make clearml-server-down && make clearml-server-up`

### Memory Issues

Elasticsearch may require memory limits. Check `infra/clearml/docker-compose.yml`:

```yaml
elasticsearch:
  environment:
    - ES_JAVA_OPTS=-Xms256m -Xmx256m
  mem_limit: 768m
```
