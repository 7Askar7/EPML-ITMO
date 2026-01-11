"""ClearML Pipeline with visual DAG for wine-quality project.

Uses PipelineDecorator to create a real ClearML Pipeline
with dependency graph visualization in UI.

DAG structure:
    load_data -> [train_logreg, train_rf, train_gb, train_svc] -> evaluate -> register
"""

# ruff: noqa: T201, N806, E402

import argparse
import os
from pathlib import Path

# Load environment variables from .env.clearml
_env_file = Path(__file__).resolve().parents[2] / ".env.clearml"
if _env_file.exists():
    with open(_env_file, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip())

from clearml import OutputModel, Task
from clearml.automation import PipelineDecorator

# Project configuration
PROJECT_NAME = "wine-quality-clearml"
PIPELINE_NAME = "wine-quality-pipeline"


@PipelineDecorator.component(
    return_values=["data_dict"],
    cache=True,
    task_type=Task.TaskTypes.data_processing,
)
def step_load_data(project_dir: str) -> dict:
    """Step 1: Load and prepare data.

    Args:
        project_dir: absolute path to project root

    Returns:
        dict with keys: X_train, y_train, X_test, y_test, data_version
    """
    import hashlib
    from pathlib import Path

    import pandas as pd

    processed_dir = Path(project_dir) / "data" / "processed"

    train_path = processed_dir / "train.csv"
    test_path = processed_dir / "test.csv"

    # Load data
    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path)

    X_train = train_df.drop("quality", axis=1)
    y_train = train_df["quality"]
    X_test = test_df.drop("quality", axis=1)
    y_test = test_df["quality"]

    # Data version hash (not used for security, just versioning)
    data_hash = hashlib.md5(  # noqa: S324
        train_df.to_csv().encode(), usedforsecurity=False
    ).hexdigest()[:8]

    print(f"Loaded data: train={len(X_train)}, test={len(X_test)}")
    print(f"Data version: {data_hash}")

    return {
        "X_train": X_train.to_dict(),
        "y_train": y_train.tolist(),
        "X_test": X_test.to_dict(),
        "y_test": y_test.tolist(),
        "data_version": data_hash,
    }


@PipelineDecorator.component(
    return_values=["model_result"],
    cache=True,
    task_type=Task.TaskTypes.training,
)
def step_train_model(
    data_dict: dict, model_name: str, model_params: dict, project_dir: str
) -> dict:
    """Step 2: Train a single model.

    Args:
        data_dict: data from step_load_data
        model_name: model name (logreg, rf, gb, svc)
        model_params: model hyperparameters
        project_dir: absolute path to project root

    Returns:
        dict with model and metrics
    """
    import pickle  # noqa: S403
    from pathlib import Path

    import pandas as pd
    from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import accuracy_score, f1_score
    from sklearn.svm import SVC

    # Restore data from dict
    X_train = pd.DataFrame(data_dict["X_train"])
    y_train = pd.Series(data_dict["y_train"])
    X_test = pd.DataFrame(data_dict["X_test"])
    y_test = pd.Series(data_dict["y_test"])

    # Select model class
    model_classes = {
        "logreg": LogisticRegression,
        "rf": RandomForestClassifier,
        "gb": GradientBoostingClassifier,
        "svc": SVC,
    }

    model_class = model_classes.get(model_name)
    if model_class is None:
        raise ValueError(f"Unknown model: {model_name}")

    # Train model
    print(f"Training {model_name} with params: {model_params}")
    model = model_class(**model_params)
    model.fit(X_train, y_train)

    # Predict and calculate metrics
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average="weighted")

    print(f"{model_name}: accuracy={accuracy:.4f}, f1={f1:.4f}")

    # Save model
    models_dir = Path(project_dir) / "models" / "clearml"
    models_dir.mkdir(parents=True, exist_ok=True)
    model_path = models_dir / f"{model_name}.pkl"
    with open(model_path, "wb") as f:
        pickle.dump(model, f)

    return {
        "name": model_name,
        "model_path": str(model_path),
        "accuracy": accuracy,
        "f1": f1,
        "params": model_params,
    }


@PipelineDecorator.component(
    return_values=["best_model"],
    task_type=Task.TaskTypes.qc,
)
def step_evaluate(
    model_logreg: dict,
    model_rf: dict,
    model_gb: dict,
    model_svc: dict,
) -> dict:
    """Step 3: Evaluate and select the best model.

    Args:
        model_*: training results for each model

    Returns:
        dict with the best model
    """
    models = [model_logreg, model_rf, model_gb, model_svc]

    print("\n=== Model Comparison ===")
    for m in models:
        print(f"  {m['name']}: accuracy={m['accuracy']:.4f}, f1={m['f1']:.4f}")

    # Select best by accuracy
    best = max(models, key=lambda x: x["accuracy"])
    print(f"\nBest model: {best['name']} (accuracy={best['accuracy']:.4f})")

    return best


@PipelineDecorator.component(
    task_type=Task.TaskTypes.custom,
)
def step_register(best_model: dict, data_version: str) -> None:
    """Step 4: Register the best model in ClearML Model Registry.

    Args:
        best_model: result from step_evaluate
        data_version: data version hash
    """
    from clearml import Task

    task = Task.current_task()
    if task is None:
        print("No active task, skipping registration")
        return

    model_path = best_model["model_path"]
    model_name = best_model["name"]

    print(f"Registering model: {model_name}")
    print(f"  Path: {model_path}")
    print(f"  Accuracy: {best_model['accuracy']:.4f}")
    print(f"  Data version: {data_version}")

    # Create OutputModel for registration
    output_model = OutputModel(
        task=task,
        name=f"wine-quality-{model_name}",
        framework="scikit-learn",
    )
    output_model.update_weights(weights_filename=model_path)
    output_model.update_design(config_dict=best_model["params"])

    # Add metadata
    task.set_parameter("best_model", model_name)
    task.set_parameter("best_accuracy", best_model["accuracy"])
    task.set_parameter("best_f1", best_model["f1"])
    task.set_parameter("data_version", data_version)

    print(f"Model registered: {output_model.id}")


# Absolute path to project root (computed at module import time)
PROJECT_DIR = str(Path(__file__).resolve().parents[2])


@PipelineDecorator.pipeline(
    name=PIPELINE_NAME,
    project=PROJECT_NAME,
    version="2.0",
    pipeline_execution_queue="services",
)
def wine_quality_pipeline() -> None:
    """Main ClearML Pipeline for wine-quality.

    DAG structure:
        load_data
            |
        +---+---+-------+-------+
        |       |       |       |
      logreg   rf      gb     svc   (parallel)
        |       |       |       |
        +---+---+-------+-------+
            |
        evaluate
            |
        register
    """
    # Step 1: Load data
    data = step_load_data(project_dir=PROJECT_DIR)

    # Step 2: Train models (parallel)
    model_logreg = step_train_model(
        data_dict=data,
        model_name="logreg",
        model_params={"C": 1.0, "max_iter": 300, "random_state": 42},
        project_dir=PROJECT_DIR,
    )

    model_rf = step_train_model(
        data_dict=data,
        model_name="rf",
        model_params={"n_estimators": 50, "max_depth": 8, "random_state": 42},
        project_dir=PROJECT_DIR,
    )

    model_gb = step_train_model(
        data_dict=data,
        model_name="gb",
        model_params={"n_estimators": 50, "learning_rate": 0.05, "random_state": 42},
        project_dir=PROJECT_DIR,
    )

    model_svc = step_train_model(
        data_dict=data,
        model_name="svc",
        model_params={"C": 1.0, "kernel": "linear", "random_state": 42},
        project_dir=PROJECT_DIR,
    )

    # Step 3: Evaluate and select best model
    best_model = step_evaluate(
        model_logreg=model_logreg,
        model_rf=model_rf,
        model_gb=model_gb,
        model_svc=model_svc,
    )

    # Step 4: Register best model
    step_register(best_model=best_model, data_version=data["data_version"])


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="ClearML Pipeline runner")
    parser.add_argument(
        "--local",
        action="store_true",
        default=True,
        help="Run pipeline locally (default: True)",
    )
    parser.add_argument(
        "--remote",
        action="store_true",
        help="Run pipeline on ClearML Agent queue",
    )
    return parser.parse_args()


def main() -> None:
    """Entry point for running the pipeline."""
    args = parse_args()

    if args.remote:
        # Run on ClearML Agent
        print("Starting pipeline on ClearML Agent queue...")
        PipelineDecorator.set_default_execution_queue("services")
        wine_quality_pipeline()
    else:
        # Run locally
        print("Running pipeline locally...")
        PipelineDecorator.run_locally()
        wine_quality_pipeline()

    print("\nPipeline completed!")
    print("View results at: http://localhost:8090/projects/*/pipelines")


if __name__ == "__main__":
    main()
