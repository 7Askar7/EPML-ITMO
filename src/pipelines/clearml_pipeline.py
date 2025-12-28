"""ClearML-native pipeline that mirrors the Hydra/MLflow workflow."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import pandas as pd
from clearml import Task
from omegaconf import OmegaConf

from src.mlops.clearml_utils import (
    init_task,
    load_clearml_config,
    report_leaderboard,
    send_notification,
    upload_artifacts,
)
from src.models.experiment_tracker import get_data_version
from src.models.run_experiments import ExperimentSpec, run_batch
from src.pipelines.run_hydra_pipeline import _validate_experiments

PROJECT_DIR = Path(__file__).resolve().parents[2]
DASHBOARD_DIR = PROJECT_DIR / "reports" / "figures" / "clearml"


def _load_experiments(variant: str) -> tuple[list[ExperimentSpec], int]:
    """Load experiment specs from Hydra config without invoking CLI."""
    base_cfg = OmegaConf.load(PROJECT_DIR / "configs" / "hydra" / "config.yaml")
    algo_cfg = OmegaConf.load(
        PROJECT_DIR / "configs" / "hydra" / "algorithms" / f"{variant}.yaml"
    )
    base_cfg.algorithms = algo_cfg

    experiments_raw = OmegaConf.to_container(algo_cfg.experiments, resolve=True)
    min_experiments = algo_cfg.get(
        "min_experiments", base_cfg.algorithms.get("min_experiments", 1)
    )
    specs = _validate_experiments(experiments_raw, min_experiments=min_experiments)
    return specs, min_experiments


def _save_dashboard(summary: pd.DataFrame) -> Path:
    """Create a lightweight dashboard image for the report."""
    DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)
    plot_path = DASHBOARD_DIR / "clearml_dashboard.png"

    top = summary.head(8)
    try:
        import matplotlib.pyplot as plt

        plt.figure(figsize=(8, 4))
        plt.barh(top["tags.model_name"], top["metrics.accuracy"], color="#3f37c9")
        plt.xlabel("Accuracy")
        plt.ylabel("Model")
        plt.title("ClearML Leaderboard (sample)")
        plt.gca().invert_yaxis()
        plt.tight_layout()
        plt.savefig(plot_path, dpi=200)
    except Exception:  # pragma: no cover
        plot_path.write_text("Dashboard placeholder - matplotlib unavailable")
    return plot_path


def run_clearml_pipeline(
    *,
    variant: str | None = None,
    config_path: Path | str | None = None,
    skip_registry: bool = False,
) -> dict[str, Any]:
    """Run the end-to-end workflow with ClearML tracking."""
    cfg = load_clearml_config(config_path)
    selected_variant = variant or cfg.get("experiments", {}).get(
        "default_variant", "quick"
    )
    specs, min_experiments = _load_experiments(selected_variant)
    base_tags: dict[str, str] = {
        **cfg.get("experiments", {}).get("tags", {}),
        "variant": selected_variant,
    }
    data_version = get_data_version(PROJECT_DIR / "dvc.lock") or "unknown"

    pipeline_task = init_task(
        cfg,
        task_name=cfg.get("pipeline", {}).get("name", "wine-quality-pipeline"),
        task_type=Task.TaskTypes.controller,  # ClearML 2.0+ uses controller
        tags=base_tags | {"data_version": data_version},
    )
    pipeline_task.connect(
        {"variant": selected_variant, "min_experiments": min_experiments}
    )

    results = run_batch(
        experiments=specs,
        base_tags=base_tags,
        min_experiments=min_experiments,
        log_to_clearml=True,
        clearml_config_path=config_path,
        register_models=not skip_registry,
    )

    summary = results.get("summary")
    artifacts = results.get("artifacts", {})
    leaderboard = (
        summary.head(10) if isinstance(summary, pd.DataFrame) else pd.DataFrame()
    )

    if not leaderboard.empty:
        report_leaderboard(pipeline_task, leaderboard, title="ClearML leaderboard")
    extra_artifacts = [art for art in artifacts.values() if isinstance(art, Path)]
    if not leaderboard.empty:
        extra_artifacts.append(_save_dashboard(leaderboard))
    if extra_artifacts:
        upload_artifacts(pipeline_task, extra_artifacts)

    webhook = cfg.get("notifications", {}).get("slack_webhook")
    if webhook:
        best_row = leaderboard.iloc[0] if not leaderboard.empty else None
        msg = (
            f"ClearML pipeline finished. Best model: {best_row['tags.model_name']} "
            f"(acc={best_row['metrics.accuracy']:.4f})"
            if best_row is not None
            else "ClearML pipeline finished."
        )
        send_notification(msg, webhook)

    pipeline_task.close()
    return results


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="ClearML pipeline runner")
    parser.add_argument(
        "--variant",
        type=str,
        default=None,
        help="Hydra algorithms variant to use (full|quick)",
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to ClearML config YAML (defaults to configs/clearml/config.yaml)",
    )
    parser.add_argument(
        "--skip-registry",
        action="store_true",
        help="Do not push models to ClearML Model Registry",
    )
    return parser.parse_args()


def main() -> None:  # pragma: no cover
    args = parse_args()
    run_clearml_pipeline(
        variant=args.variant,
        config_path=args.config,
        skip_registry=args.skip_registry,
    )


if __name__ == "__main__":
    main()
