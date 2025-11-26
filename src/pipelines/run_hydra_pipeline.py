"""Hydra-driven entrypoint to launch a batch of MLflow-tracked experiments."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import hydra
from omegaconf import DictConfig, OmegaConf

from src.models.run_experiments import ExperimentSpec, run_batch


def _validate_experiments(
    experiments: Iterable[dict[str, Any]],
    min_experiments: int = 1,
) -> list[ExperimentSpec]:
    specs = [ExperimentSpec(**exp) for exp in experiments]
    names = [spec.name for spec in specs]
    if len(set(names)) != len(names):
        duplicates = sorted({name for name in names if names.count(name) > 1})
        raise ValueError(f"Duplicate experiment names found: {duplicates}")
    if len(specs) < min_experiments:
        msg = f"At least {min_experiments} experiments required for this config."
        raise ValueError(msg)
    return specs


@hydra.main(  # type: ignore[misc]
    config_path="../../configs/hydra",
    config_name="config",
    version_base=None,
)
def main(cfg: DictConfig) -> None:  # pragma: no cover
    experiments_raw = OmegaConf.to_container(cfg.algorithms.experiments, resolve=True)
    min_exp = cfg.algorithms.get("min_experiments", 1)
    specs = _validate_experiments(experiments_raw, min_experiments=min_exp)

    tags_container = OmegaConf.to_container(cfg.base_tags, resolve=True)
    base_tags: dict[str, Any] = {
        **(tags_container if isinstance(tags_container, dict) else {}),
        "config_variant": cfg.algorithms.name,
    }
    run_batch(experiments=specs, base_tags=base_tags, min_experiments=min_exp)


if __name__ == "__main__":
    main()
