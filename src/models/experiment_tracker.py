"""Utilities for MLflow experiment tracking."""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Iterable

import mlflow
import mlflow.sklearn
import yaml
from mlflow import MlflowClient
from sklearn.base import BaseEstimator

PROJECT_DIR = Path(__file__).resolve().parents[2]
DEFAULT_TRACKING_URI = f"sqlite:///{PROJECT_DIR / 'mlflow.db'}"
DEFAULT_ARTIFACT_LOCATION = f"file:{PROJECT_DIR / 'mlruns'}"
DEFAULT_EXPERIMENT = "wine-quality"


def get_data_version(lock_path: Path | None = None) -> str | None:
    """Extract dataset hash from dvc.lock for MLflow tagging."""
    target = lock_path or PROJECT_DIR / "dvc.lock"
    if not target.exists():
        return None

    with target.open() as fp:
        lock_data = yaml.safe_load(fp)

    split_stage = lock_data.get("stages", {}).get("split", {})
    for dep in split_stage.get("deps", []):
        if dep.get("path") == "data/raw/winequality-red.csv":
            return dep.get("md5")
    return None


def ensure_experiment(
    tracking_uri: str = DEFAULT_TRACKING_URI,
    artifact_location: str = DEFAULT_ARTIFACT_LOCATION,
    experiment_name: str = DEFAULT_EXPERIMENT,
) -> None:
    """Create experiment with explicit artifact location if missing."""
    client = MlflowClient(tracking_uri=tracking_uri)
    if experiment_name not in {exp.name for exp in client.search_experiments()}:
        client.create_experiment(
            experiment_name,
            artifact_location=artifact_location,
        )


def configure_mlflow(
    tracking_uri: str = DEFAULT_TRACKING_URI,
    artifact_location: str = DEFAULT_ARTIFACT_LOCATION,
    experiment_name: str = DEFAULT_EXPERIMENT,
) -> None:
    """Set tracking URI, ensure experiment exists and set current experiment."""
    mlflow.set_tracking_uri(tracking_uri)
    ensure_experiment(tracking_uri, artifact_location, experiment_name)
    mlflow.set_experiment(experiment_name)


@contextmanager
def mlflow_run(
    run_name: str | None = None,
    experiment_name: str = DEFAULT_EXPERIMENT,
    tracking_uri: str = DEFAULT_TRACKING_URI,
    artifact_location: str = DEFAULT_ARTIFACT_LOCATION,
    tags: dict[str, Any] | None = None,
):
    """Context manager that opens an MLflow run with common defaults."""
    configure_mlflow(tracking_uri, artifact_location, experiment_name)
    with mlflow.start_run(run_name=run_name, tags=tags) as run:
        yield run


def log_experiment(
    *,
    run_name: str | None = None,
    experiment_name: str = DEFAULT_EXPERIMENT,
    tracking_uri: str = DEFAULT_TRACKING_URI,
    artifact_location: str = DEFAULT_ARTIFACT_LOCATION,
    tags: dict[str, Any] | None = None,
) -> Callable[[Callable[..., dict[str, Any]]], Callable[..., dict[str, Any]]]:
    """Decorator to automatically log params/metrics/artifacts from a function result.

    The wrapped function should return a dict with optional keys:
    - params: mapping of hyperparameters
    - metrics: mapping of metrics
    - artifacts: iterable of file paths to log
    - model: mapping with keys:
        estimator: fitted sklearn estimator
        artifact_path: subpath for the model (default: "model")
        registered_model_name: optional model registry name
        signature_kwargs: optional kwargs for infer_signature (input_example/signature)
    """

    def decorator(func: Callable[..., dict[str, Any]]) -> Callable[..., dict[str, Any]]:
        def wrapper(*args: Any, **kwargs: Any) -> dict[str, Any]:
            with mlflow_run(
                run_name=run_name,
                experiment_name=experiment_name,
                tracking_uri=tracking_uri,
                artifact_location=artifact_location,
                tags=tags,
            ):
                result = func(*args, **kwargs) or {}
                params = result.get("params") or {}
                metrics = result.get("metrics") or {}
                artifacts: Iterable[str] = result.get("artifacts") or []
                model_info: dict[str, Any] | None = result.get("model")

                if params:
                    mlflow.log_params(params)
                if metrics:
                    mlflow.log_metrics(metrics)
                for path in artifacts:
                    mlflow.log_artifact(str(path))
                if model_info:
                    estimator: BaseEstimator = model_info["estimator"]
                    artifact_path = model_info.get("artifact_path", "model")
                    registered_model_name = model_info.get("registered_model_name")
                    signature_kwargs = model_info.get("signature_kwargs", {})
                    mlflow.sklearn.log_model(
                        estimator,
                        artifact_path=artifact_path,
                        registered_model_name=registered_model_name,
                        **signature_kwargs,
                    )
                return result

        return wrapper

    return decorator
