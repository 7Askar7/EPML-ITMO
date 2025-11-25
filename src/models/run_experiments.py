"""Batch runner for MLflow-tracked experiments."""

from __future__ import annotations

from pathlib import Path

import mlflow
import numpy as np
import pandas as pd
from mlflow.models import infer_signature
from sklearn.ensemble import AdaBoostClassifier, GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import ConfusionMatrixDisplay, accuracy_score, classification_report, f1_score
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC

from src.models.experiment_tracker import (
    DEFAULT_ARTIFACT_LOCATION,
    DEFAULT_EXPERIMENT,
    DEFAULT_TRACKING_URI,
    get_data_version,
    log_experiment,
)
from src.models.train_model import load_processed_data


def _save_confusion_matrix(
    y_true: pd.Series,
    y_pred: np.ndarray,
    out_path: Path,
) -> Path:
    """Render confusion matrix and save to file."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    disp = ConfusionMatrixDisplay.from_predictions(y_true, y_pred, cmap="Blues")
    disp.figure_.tight_layout()
    disp.figure_.savefig(out_path, dpi=200)
    return out_path


def _write_report(text: str, out_path: Path) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text)
    return out_path


def _compute_metrics(y_true: pd.Series, y_pred: np.ndarray) -> dict[str, float]:
    return {
        "accuracy": accuracy_score(y_true, y_pred),
        "f1_weighted": f1_score(y_true, y_pred, average="weighted"),
    }


def _prepare_data(project_dir: Path) -> tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series]:
    processed_dir = project_dir / "data" / "processed"
    train_df, test_df = load_processed_data(processed_dir)
    x_train = train_df.drop("quality", axis=1)
    y_train = train_df["quality"]
    x_test = test_df.drop("quality", axis=1)
    y_test = test_df["quality"]
    return x_train, y_train, x_test, y_test


def _train_validation_split(
    x_train: pd.DataFrame,
    y_train: pd.Series,
    test_size: float = 0.1,
    random_state: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    return train_test_split(
        x_train,
        y_train,
        test_size=test_size,
        stratify=y_train,
        random_state=random_state,
    )


def _experiment_configs() -> list[dict[str, object]]:
    """Return a list of model configurations (>=15)."""
    return [
        {"name": "logreg_c0.5", "model": LogisticRegression(C=0.5, max_iter=500)},
        {"name": "logreg_c1", "model": LogisticRegression(C=1.0, max_iter=500)},
        {"name": "logreg_c2", "model": LogisticRegression(C=2.0, max_iter=500)},
        {"name": "rf_50_depth8", "model": RandomForestClassifier(n_estimators=50, max_depth=8, random_state=42)},
        {"name": "rf_100_depth10", "model": RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)},
        {"name": "rf_150_depth12", "model": RandomForestClassifier(n_estimators=150, max_depth=12, random_state=42)},
        {"name": "gb_50_lr0.05", "model": GradientBoostingClassifier(n_estimators=50, learning_rate=0.05, random_state=42)},
        {"name": "gb_100_lr0.1", "model": GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, random_state=42)},
        {"name": "svc_linear_c1", "model": SVC(kernel="linear", C=1.0)},
        {"name": "svc_rbf_c1_g01", "model": SVC(kernel="rbf", C=1.0, gamma=0.1)},
        {"name": "svc_rbf_c2_g005", "model": SVC(kernel="rbf", C=2.0, gamma=0.05)},
        {"name": "knn_5_uniform", "model": KNeighborsClassifier(n_neighbors=5, weights="uniform")},
        {"name": "knn_10_distance", "model": KNeighborsClassifier(n_neighbors=10, weights="distance")},
        {"name": "ada_50", "model": AdaBoostClassifier(n_estimators=50, learning_rate=0.8, random_state=42)},
        {"name": "ada_100", "model": AdaBoostClassifier(n_estimators=100, learning_rate=0.6, random_state=42)},
        {"name": "rf_200_depth14", "model": RandomForestClassifier(n_estimators=200, max_depth=14, random_state=123)},
    ]


def _make_tags(model_name: str, data_version: str | None) -> dict[str, str]:
    tags: dict[str, str] = {
        "model_name": model_name,
        "pipeline": "run_experiments.py",
    }
    if data_version:
        tags["data_version_md5"] = data_version
    return tags


def _save_artifacts(
    project_dir: Path,
    run_label: str,
    y_true: pd.Series,
    y_pred: np.ndarray,
    report: str,
) -> list[Path]:
    figures_dir = project_dir / "reports" / "figures"
    cm_path = _save_confusion_matrix(y_true, y_pred, figures_dir / f"cm_{run_label}.png")
    report_path = _write_report(report, figures_dir / f"classification_report_{run_label}.txt")
    return [cm_path, report_path]


def _signature_kwargs(x_train: pd.DataFrame, model) -> dict[str, object]:
    try:
        prediction_sample = model.predict(x_train.head(5))
    except Exception:  # pragma: no cover - fallback for models needing fit first
        prediction_sample = None
    return {
        "signature": infer_signature(x_train, prediction_sample) if prediction_sample is not None else None,
        "input_example": x_train.head(5),
    }


def _run_single_experiment(
    model_config: dict[str, object],
    x_train: pd.DataFrame,
    y_train: pd.Series,
    x_test: pd.DataFrame,
    y_test: pd.Series,
    project_dir: Path,
    data_version: str | None,
) -> dict[str, object]:
    model = model_config["model"]
    name = model_config["name"]

    @log_experiment(
        run_name=name,
        experiment_name=DEFAULT_EXPERIMENT,
        tracking_uri=DEFAULT_TRACKING_URI,
        artifact_location=DEFAULT_ARTIFACT_LOCATION,
        tags=_make_tags(name, data_version),
    )
    def _train_and_log() -> dict[str, object]:
        model.fit(x_train, y_train)
        y_pred = model.predict(x_test)
        metrics = _compute_metrics(y_test, y_pred)
        report = classification_report(y_test, y_pred, zero_division=0)
        artifacts = _save_artifacts(project_dir, name, y_test, y_pred, report)

        mlflow.log_text(report, artifact_file="classification_report.txt")

        return {
            "params": model.get_params(),
            "metrics": metrics,
            "artifacts": artifacts,
            "model": {
                "estimator": model,
                "artifact_path": "model",
                "signature_kwargs": _signature_kwargs(x_train, model),
            },
        }

    return _train_and_log()


def main() -> None:  # pragma: no cover
    project_dir = Path(__file__).resolve().parents[2]
    data_version = get_data_version(project_dir / "dvc.lock")
    x_train, y_train, x_test, y_test = _prepare_data(project_dir)

    # Hold-out split for light validation score logging
    x_train_fold, x_val_fold, y_train_fold, y_val_fold = _train_validation_split(x_train, y_train)
    fold_metrics_path = project_dir / "reports" / "figures" / "val_split_info.txt"
    fold_metrics_path.parent.mkdir(parents=True, exist_ok=True)
    fold_metrics_path.write_text(
        f"Train size: {len(x_train_fold)}, Val size: {len(x_val_fold)}, Test size: {len(x_test)}"
    )

    for config in _experiment_configs():
        _run_single_experiment(config, x_train, y_train, x_test, y_test, project_dir, data_version)


if __name__ == "__main__":
    main()
