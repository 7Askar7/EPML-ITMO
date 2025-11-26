"""Hydra-driven entrypoint to launch a batch of MLflow-tracked experiments."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import hydra
from omegaconf import DictConfig, OmegaConf

from src.models.run_experiments import ExperimentSpec, run_batch


def _validate_experiments(
    experiments: Iterable[dict[str, Any]],
) -> list[ExperimentSpec]:
    specs = [ExperimentSpec(**exp) for exp in experiments]
    names = [spec.name for spec in specs]
    if len(set(names)) != len(names):
        duplicates = sorted({name for name in names if names.count(name) > 1})
        raise ValueError(f"Duplicate experiment names found: {duplicates}")
    if len(specs) < 15:
        msg = "At least 15 experiments required; check configs/hydra/algorithms/*.yaml."
        raise ValueError(msg)
    return specs


@hydra.main(  # type: ignore[misc]
    config_path="../../configs/hydra",
    config_name="config",
    version_base=None,
)
def main(cfg: DictConfig) -> None:  # pragma: no cover
    experiments_raw = OmegaConf.to_container(cfg.algorithms.experiments, resolve=True)
    specs = _validate_experiments(experiments_raw)

    tags_container = OmegaConf.to_container(cfg.base_tags, resolve=True)
    base_tags: dict[str, Any] = {
        **(tags_container if isinstance(tags_container, dict) else {}),
        "config_variant": cfg.algorithms.name,
    }
    run_batch(experiments=specs, base_tags=base_tags)


if __name__ == "__main__":
    main()
