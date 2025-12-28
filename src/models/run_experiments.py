"""Batch runner for MLflow-tracked experiments with Hydra support."""

from __future__ import annotations

import contextlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

import joblib
import mlflow
import numpy as np
import pandas as pd
from mlflow.models import infer_signature
from sklearn.base import BaseEstimator
from sklearn.ensemble import (
    AdaBoostClassifier,
    GradientBoostingClassifier,
    RandomForestClassifier,
)
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    classification_report,
    f1_score,
)
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

PROJECT_DIR = Path(__file__).resolve().parents[2]
EXPERIMENTS_DIR = PROJECT_DIR / "reports" / "figures" / "experiments"
CLEARML_MODELS_DIR = PROJECT_DIR / "models" / "clearml"

MODEL_REGISTRY: dict[str, Any] = {
    "logreg": LogisticRegression,
    "random_forest": RandomForestClassifier,
    "gradient_boosting": GradientBoostingClassifier,
    "svc": SVC,
    "knn": KNeighborsClassifier,
    "adaboost": AdaBoostClassifier,
}


@dataclass
class ExperimentSpec:
    """Structured definition for an experiment."""

    name: str
    estimator: str
    params: dict[str, Any]


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


def _prepare_data(
    project_dir: Path,
) -> tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series]:
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
    result: tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series] = train_test_split(
        x_train,
        y_train,
        test_size=test_size,
        stratify=y_train,
        random_state=random_state,
    )
    return result


def _default_experiments() -> list[ExperimentSpec]:
    """Return a list of model configurations (>=15)."""
    return [
        ExperimentSpec("logreg_c0.5", "logreg", {"C": 0.5, "max_iter": 500}),
        ExperimentSpec("logreg_c1", "logreg", {"C": 1.0, "max_iter": 500}),
        ExperimentSpec("logreg_c2", "logreg", {"C": 2.0, "max_iter": 500}),
        ExperimentSpec(
            "rf_50_depth8",
            "random_forest",
            {"n_estimators": 50, "max_depth": 8, "random_state": 42},
        ),
        ExperimentSpec(
            "rf_100_depth10",
            "random_forest",
            {"n_estimators": 100, "max_depth": 10, "random_state": 42},
        ),
        ExperimentSpec(
            "rf_150_depth12",
            "random_forest",
            {"n_estimators": 150, "max_depth": 12, "random_state": 42},
        ),
        ExperimentSpec(
            "gb_50_lr0.05",
            "gradient_boosting",
            {"n_estimators": 50, "learning_rate": 0.05, "random_state": 42},
        ),
        ExperimentSpec(
            "gb_100_lr0.1",
            "gradient_boosting",
            {"n_estimators": 100, "learning_rate": 0.1, "random_state": 42},
        ),
        ExperimentSpec("svc_linear_c1", "svc", {"kernel": "linear", "C": 1.0}),
        ExperimentSpec(
            "svc_rbf_c1_g01", "svc", {"kernel": "rbf", "C": 1.0, "gamma": 0.1}
        ),
        ExperimentSpec(
            "svc_rbf_c2_g005", "svc", {"kernel": "rbf", "C": 2.0, "gamma": 0.05}
        ),
        ExperimentSpec(
            "knn_5_uniform", "knn", {"n_neighbors": 5, "weights": "uniform"}
        ),
        ExperimentSpec(
            "knn_10_distance", "knn", {"n_neighbors": 10, "weights": "distance"}
        ),
        ExperimentSpec(
            "ada_50",
            "adaboost",
            {"n_estimators": 50, "learning_rate": 0.8, "random_state": 42},
        ),
        ExperimentSpec(
            "ada_100",
            "adaboost",
            {"n_estimators": 100, "learning_rate": 0.6, "random_state": 42},
        ),
        ExperimentSpec(
            "rf_200_depth14",
            "random_forest",
            {"n_estimators": 200, "max_depth": 14, "random_state": 123},
        ),
    ]


def _make_tags(
    model_name: str, data_version: str | None, base_tags: dict[str, str] | None = None
) -> dict[str, str]:
    tags: dict[str, str] = {
        "model_name": model_name,
        "pipeline": "run_experiments.py",
    }
    if data_version:
        tags["data_version_md5"] = data_version
    if base_tags:
        tags.update(base_tags)
    return tags


def _save_artifacts(
    run_label: str,
    y_true: pd.Series,
    y_pred: np.ndarray,
    report: str,
) -> list[Path]:
    cm_path = _save_confusion_matrix(
        y_true, y_pred, EXPERIMENTS_DIR / f"cm_{run_label}.png"
    )
    report_path = _write_report(
        report, EXPERIMENTS_DIR / f"classification_report_{run_label}.txt"
    )
    return [cm_path, report_path]


def _signature_kwargs(x_train: pd.DataFrame, model: BaseEstimator) -> dict[str, object]:
    try:
        prediction_sample = model.predict(x_train.head(5))
    except Exception:  # pragma: no cover - fallback for models needing fit first
        prediction_sample = None
    return {
        "signature": (
            infer_signature(x_train, prediction_sample)
            if prediction_sample is not None
            else None
        ),
        "input_example": x_train.head(5),
    }


def _build_model(estimator: str, params: dict[str, Any]) -> BaseEstimator:
    if estimator not in MODEL_REGISTRY:
        available = sorted(MODEL_REGISTRY.keys())
        msg = f"Unknown estimator '{estimator}'. Available: {available}"
        raise ValueError(msg)
    return MODEL_REGISTRY[estimator](**params)


def _run_single_experiment(
    spec: ExperimentSpec,
    model: BaseEstimator,
    x_train: pd.DataFrame,
    y_train: pd.Series,
    x_test: pd.DataFrame,
    y_test: pd.Series,
    data_version: str | None,
    base_tags: dict[str, str] | None = None,
    save_model: bool = False,
) -> dict[str, object]:
    @log_experiment(
        run_name=spec.name,
        experiment_name=DEFAULT_EXPERIMENT,
        tracking_uri=DEFAULT_TRACKING_URI,
        artifact_location=DEFAULT_ARTIFACT_LOCATION,
        tags=_make_tags(spec.name, data_version, base_tags),
    )
    def _train_and_log() -> dict[str, object]:
        model.fit(x_train, y_train)
        y_pred = model.predict(x_test)
        metrics = _compute_metrics(y_test, y_pred)
        report = classification_report(y_test, y_pred, zero_division=0)
        artifacts = _save_artifacts(spec.name, y_test, y_pred, report)
        model_path = None
        if save_model:
            CLEARML_MODELS_DIR.mkdir(parents=True, exist_ok=True)
            model_path = CLEARML_MODELS_DIR / f"{spec.name}.pkl"
            joblib.dump(model, model_path)

        mlflow.log_text(report, artifact_file="classification_report.txt")

        return {
            "params": model.get_params(),
            "metrics": metrics,
            "artifacts": artifacts,
            "y_true": y_test.to_numpy(),
            "y_pred": y_pred,
            "model_path": model_path,
            "model": {
                "estimator": model,
                "artifact_path": "model",
                "signature_kwargs": _signature_kwargs(x_train, model),
            },
        }

    return _train_and_log()


def _load_mlflow_summary() -> pd.DataFrame | None:
    mlflow.set_tracking_uri(DEFAULT_TRACKING_URI)
    df = mlflow.search_runs(experiment_names=[DEFAULT_EXPERIMENT])
    if df.empty or "metrics.accuracy" not in df:
        return None

    summary = df[
        ["run_id", "tags.model_name", "metrics.accuracy", "metrics.f1_weighted"]
    ].copy()
    summary["tags.model_name"] = summary["tags.model_name"].fillna(
        summary["run_id"].str[:8]
    )
    summary = summary.dropna(subset=["metrics.accuracy"])
    return cast(pd.DataFrame, summary.sort_values("metrics.accuracy", ascending=False))


def _save_summary_plot(
    summary: pd.DataFrame | None = None,
) -> tuple[Path | None, pd.DataFrame | None, Path | None, Path | None]:
    summary_df = summary if summary is not None else _load_mlflow_summary()
    if summary_df is None or summary_df.empty:
        return None, summary_df, None, None

    EXPERIMENTS_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = EXPERIMENTS_DIR / "experiments_top10.csv"
    status_path = EXPERIMENTS_DIR / "status.txt"
    summary_df.head(10).to_csv(csv_path, index=False)

    best = summary_df.iloc[0]
    model_name = best["tags.model_name"]
    acc = best["metrics.accuracy"]
    f1 = best.get("metrics.f1_weighted", float("nan"))
    status_path.write_text(
        f"Best run: {model_name} (accuracy={acc:.4f}, f1_weighted={f1:.4f})"
    )

    try:
        import matplotlib.pyplot as plt

        top = summary_df.head(10)
        plt.figure(figsize=(8, 4.5))
        plt.bar(top["tags.model_name"], top["metrics.accuracy"], color="#2a9d8f")
        plt.xticks(rotation=45, ha="right", fontsize=9)
        plt.ylabel("Accuracy")
        plt.title("Top experiments by accuracy (MLflow)")
        plt.tight_layout()
        plot_path = EXPERIMENTS_DIR / "experiments_summary.png"
        plt.savefig(plot_path, dpi=200)
        return plot_path, summary_df, csv_path, status_path
    except Exception:  # pragma: no cover
        return None, summary_df, csv_path, status_path


def run_batch(  # noqa: C901
    experiments: list[ExperimentSpec] | list[dict[str, Any]] | None = None,
    base_tags: dict[str, str] | None = None,
    *,
    min_experiments: int = 15,
    log_to_clearml: bool = False,
    clearml_config_path: Path | str | None = None,
    register_models: bool = True,
) -> dict[str, Any]:
    clearml_cfg: dict[str, Any] | None = None
    leaderboard_task = None
    if log_to_clearml:
        from clearml import Task

        from src.mlops.clearml_utils import (
            init_task,
            load_clearml_config,
            log_confusion_matrix,
            log_params_and_metrics,
            register_model,
            report_leaderboard,
            upload_artifacts,
        )

        clearml_cfg = load_clearml_config(clearml_config_path)
        leaderboard_task = init_task(
            clearml_cfg,
            task_name="experiments-leaderboard",
            task_type=Task.TaskTypes.monitor,
            tags={"source": "run_batch"},
            force_create=True,  # Create as subtask when pipeline task exists
        )

    def _log_clearml_experiment(
        spec: ExperimentSpec, result: dict[str, object]
    ) -> None:
        if clearml_cfg is None:
            return

        tags = _make_tags(spec.name, data_version, base_tags)
        task = init_task(
            clearml_cfg,
            task_name=f"exp::{spec.name}",
            task_type=Task.TaskTypes.training,
            tags=tags,
            force_create=True,  # Create as subtask for each experiment
        )
        params = result.get("params", {})
        metrics_raw = result.get("metrics", {})
        metrics_dict = (
            cast(dict[str, float], metrics_raw)
            if isinstance(metrics_raw, dict)
            else None
        )
        log_params_and_metrics(
            task, params if isinstance(params, dict) else {}, metrics=metrics_dict
        )

        y_true = result.get("y_true")
        y_pred = result.get("y_pred")
        if y_true is not None and y_pred is not None:
            with contextlib.suppress(Exception):
                log_confusion_matrix(
                    task, np.asarray(y_true), np.asarray(y_pred), labels=None
                )

        artifacts_raw = result.get("artifacts", [])
        artifact_list: list[Any] = (
            list(artifacts_raw) if artifacts_raw else []  # type: ignore[call-overload]
        )
        artifact_paths = [p for p in artifact_list if isinstance(p, Path)]
        if artifact_paths:
            upload_artifacts(task, artifact_paths)

        model_path = result.get("model_path")
        if register_models and isinstance(model_path, Path):
            registry_name = clearml_cfg.get("models", {}).get(
                "registry_name", "wine-quality-registry"
            )
            register_model(
                task,
                model_path,
                name=f"{registry_name}::{spec.name}",
                comment="Auto-registered from run_experiments.py",
                metadata={"data_version": data_version, **(base_tags or {})},
            )
        task.close()

    data_version = get_data_version(PROJECT_DIR / "dvc.lock")
    x_train, y_train, x_test, y_test = _prepare_data(PROJECT_DIR)

    # Light monitoring artifact
    x_train_fold, x_val_fold, y_train_fold, y_val_fold = _train_validation_split(
        x_train, y_train
    )
    fold_metrics_path = EXPERIMENTS_DIR / "val_split_info.txt"
    fold_metrics_path.parent.mkdir(parents=True, exist_ok=True)
    info = f"Train: {len(x_train_fold)}, Val: {len(x_val_fold)}, Test: {len(x_test)}"
    fold_metrics_path.write_text(info)

    if experiments is None:
        experiment_specs = _default_experiments()
    else:
        experiment_specs = [
            exp if isinstance(exp, ExperimentSpec) else ExperimentSpec(**exp)
            for exp in experiments
        ]

    if len(experiment_specs) < min_experiments:
        msg = f"At least {min_experiments} experiments required."
        raise ValueError(msg)

    results: list[dict[str, object]] = []
    for spec in experiment_specs:
        model = _build_model(spec.estimator, spec.params)
        result = _run_single_experiment(
            spec,
            model,
            x_train,
            y_train,
            x_test,
            y_test,
            data_version,
            base_tags,
            save_model=log_to_clearml,
        )
        if log_to_clearml:
            _log_clearml_experiment(spec, result)
        results.append(result | {"name": spec.name, "estimator": spec.estimator})

    plot_path, summary_df, csv_path, status_path = _save_summary_plot()
    artifact_paths: list[Path] = [
        p
        for p in [plot_path, csv_path, status_path, fold_metrics_path]
        if isinstance(p, Path)
    ]

    if log_to_clearml and clearml_cfg is not None and leaderboard_task is not None:
        leaderboard_df = (
            summary_df.head(10) if summary_df is not None else pd.DataFrame()
        )
        if not leaderboard_df.empty:
            report_leaderboard(
                leaderboard_task,
                leaderboard_df,
                title="MLflow leaderboard",
            )
        if artifact_paths:
            upload_artifacts(leaderboard_task, artifact_paths)
        leaderboard_task.close()

    return {
        "experiments": results,
        "summary": summary_df,
        "artifacts": {
            "plot": plot_path,
            "csv": csv_path,
            "status": status_path,
            "fold_metrics": fold_metrics_path,
        },
    }


def main() -> None:  # pragma: no cover
    run_batch()


if __name__ == "__main__":
    main()
