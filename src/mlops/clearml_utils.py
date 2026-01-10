"""Helper utilities for ClearML tracking, model registry and notifications."""

from __future__ import annotations

import json
import os
import urllib.request
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml  # type: ignore[import-untyped]
from clearml import Task
from dotenv import load_dotenv

# Загрузка переменных окружения из .env.clearml
# Ищем файл .env.clearml в корне проекта
_env_file = Path(__file__).parent.parent.parent / ".env.clearml"
if _env_file.exists():
    load_dotenv(_env_file, override=False)

DEFAULT_CONFIG_PATH = Path("configs/clearml/config.yaml")


def load_clearml_config(config_path: Path | str | None = None) -> dict[str, Any]:
    """Load ClearML configuration from YAML (fallbacks to sane defaults)."""
    path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
    if not path.exists():
        return {
            "project_name": "wine-quality-clearml",
            "pipeline": {"name": "wine-quality-pipeline", "queue": "services"},
            "server": {
                "api": os.environ.get("CLEARML_API_HOST", "http://localhost:8008"),
                "web": os.environ.get("CLEARML_WEB_HOST", "http://localhost:8090"),
                "files": os.environ.get("CLEARML_FILES_HOST", "http://localhost:8091"),
            },
            "auth": {
                "access_key": os.environ.get("CLEARML_API_ACCESS_KEY", ""),
                "secret_key": os.environ.get("CLEARML_API_SECRET_KEY", ""),
            },
            "models": {"registry_name": "wine-quality-registry"},
            "notifications": {"slack_webhook": ""},
        }

    with path.open() as fp:
        cfg: dict[str, Any] = yaml.safe_load(fp)
    return cfg


def apply_clearml_env(cfg: dict[str, Any]) -> None:
    """Export ClearML server/auth settings into environment variables."""
    server = cfg.get("server", {})
    auth = cfg.get("auth", {})
    os.environ.setdefault(
        "CLEARML_API_HOST", server.get("api", "http://localhost:8008")
    )
    os.environ.setdefault(
        "CLEARML_WEB_HOST", server.get("web", "http://localhost:8090")
    )
    os.environ.setdefault(
        "CLEARML_FILES_HOST", server.get("files", "http://localhost:8091")
    )
    if auth.get("access_key"):
        os.environ.setdefault("CLEARML_API_ACCESS_KEY", str(auth["access_key"]))
    if auth.get("secret_key"):
        os.environ.setdefault("CLEARML_API_SECRET_KEY", str(auth["secret_key"]))


def init_task(
    cfg: dict[str, Any],
    *,
    task_name: str,
    task_type: str = Task.TaskTypes.training,
    tags: dict[str, str] | None = None,
    reuse_last_task_id: bool = False,
    force_create: bool = False,
) -> Task:
    """Initialize a ClearML Task with common defaults and tags.

    Args:
        force_create: If True, use Task.create() instead of Task.init() for subtasks
    """
    apply_clearml_env(cfg)

    if force_create:
        # For creating subtasks when a parent task already exists
        task = Task.create(
            project_name=cfg.get("project_name", "wine-quality-clearml"),
            task_name=task_name,
            task_type=task_type,
        )
    else:
        task = Task.init(
            project_name=cfg.get("project_name", "wine-quality-clearml"),
            task_name=task_name,
            task_type=task_type,
            reuse_last_task_id=reuse_last_task_id,
        )
    if tags:
        task.add_tags([f"{k}:{v}" for k, v in tags.items()])
    return task


def log_params_and_metrics(
    task: Task, params: dict[str, Any], metrics: dict[str, float] | None = None
) -> None:
    """Attach params and metrics to the current task."""
    if params:
        task.connect(params, name="hyperparameters")
    if metrics:
        logger = task.get_logger()
        for key, value in metrics.items():
            logger.report_scalar(
                title="metrics", series=key, value=float(value), iteration=0
            )


def log_confusion_matrix(
    task: Task, y_true: np.ndarray, y_pred: np.ndarray, labels: list[str] | None = None
) -> None:
    """Log a confusion matrix to ClearML if possible."""
    logger = task.get_logger()
    labels_idx = sorted(set(y_true.tolist()) | set(y_pred.tolist()))
    display_labels = labels or [str(label) for label in labels_idx]
    matrix = np.zeros((len(display_labels), len(display_labels)), dtype=int)
    for true_val, pred_val in zip(y_true, y_pred, strict=False):
        i = labels_idx.index(true_val)
        j = labels_idx.index(pred_val)
        matrix[i, j] += 1
    logger.report_confusion_matrix(
        title="Confusion Matrix",
        series="eval",
        matrix=matrix.tolist(),
        iteration=0,
        xaxis=display_labels,
        yaxis=display_labels,
    )


def upload_artifacts(task: Task, artifacts: list[Path]) -> None:
    """Upload local artifact files to ClearML."""
    for path in artifacts:
        if not path.exists():
            continue
        task.upload_artifact(
            name=path.stem.replace(".", "_"),
            artifact_object=str(path),
        )


def register_model(
    task: Task,
    model_path: Path,
    *,
    name: str,
    comment: str = "",
    metadata: dict[str, Any] | None = None,
) -> str | None:
    """Register a model file in the ClearML Model Registry."""
    if not model_path.exists():
        return None
    output_model = task.update_output_model(
        model_path=str(model_path),
        name=name,
        auto_delete_file=False,
        comment=comment,
    )
    if metadata:
        try:
            task.get_logger().report_text(json.dumps(metadata, indent=2))
        except Exception:
            task.get_logger().report_text(str(metadata))
    model_id = None
    if hasattr(output_model, "id"):
        model_id = output_model.id
    elif hasattr(output_model, "model_id"):
        model_id = output_model.model_id
    return model_id


def report_leaderboard(task: Task, leaderboard: pd.DataFrame, title: str) -> None:
    """Log a pandas DataFrame as a ClearML table."""
    logger = task.get_logger()
    logger.report_table(
        title=title,
        series="leaderboard",
        iteration=0,
        table_plot=leaderboard,
    )


def send_notification(message: str, webhook: str | None) -> None:
    """Send a simple JSON payload to a webhook (e.g., Slack)."""
    if not webhook:
        return
    payload = json.dumps({"text": message}).encode("utf-8")
    request = urllib.request.Request(  # noqa: S310
        webhook,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        urllib.request.urlopen(request, timeout=5)  # noqa: S310  # nosec B310
    except Exception:
        # Notifications are best-effort; failures should not break the pipeline.
        return
