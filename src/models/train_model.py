"""Script for training wine quality prediction model with MLflow tracking."""

from pathlib import Path

import joblib
import mlflow
import mlflow.sklearn
import pandas as pd
from mlflow.models import infer_signature
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

from src.models.experiment_tracker import (
    DEFAULT_ARTIFACT_LOCATION,
    DEFAULT_EXPERIMENT,
    DEFAULT_TRACKING_URI,
    configure_mlflow,
    get_data_version,
)

REGISTERED_MODEL_NAME = "wine-quality-rf"


def load_processed_data(processed_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load processed train and test data from CSV files."""
    train_df = pd.read_csv(processed_dir / "train.csv")
    test_df = pd.read_csv(processed_dir / "test.csv")
    return train_df.reset_index(drop=True), test_df.reset_index(drop=True)


def train_model(x_train: pd.DataFrame, y_train: pd.Series) -> RandomForestClassifier:
    """Train a Random Forest classifier."""
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(x_train, y_train)
    return model


def evaluate_model(
    model: RandomForestClassifier,
    x_test: pd.DataFrame,
    y_test: pd.Series,
) -> dict[str, str]:
    """Evaluate model performance and return metrics."""
    y_pred = model.predict(x_test)
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, zero_division=0)
    return {"accuracy": accuracy, "report": report}


def save_model(model: RandomForestClassifier, model_path: Path) -> None:
    """Save trained model to disk using joblib for safety."""
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_path)


def main() -> None:  # pragma: no cover
    """Main training pipeline with console output for user feedback."""
    project_dir = Path(__file__).resolve().parents[2]
    processed_dir = project_dir / "data" / "processed"
    model_path = project_dir / "models" / "wine_quality_model.pkl"
    mlflow_tracking_uri = DEFAULT_TRACKING_URI
    artifact_location = DEFAULT_ARTIFACT_LOCATION
    data_version = get_data_version(project_dir / "dvc.lock")

    train_df, test_df = load_processed_data(processed_dir)

    x_train = train_df.drop("quality", axis=1)
    y_train = train_df["quality"]
    x_test = test_df.drop("quality", axis=1)
    y_test = test_df["quality"]

    model = train_model(x_train, y_train)

    metrics = evaluate_model(model, x_test, y_test)
    print(f"Test Accuracy: {metrics['accuracy']:.4f}")  # noqa: T201
    print("\nClassification Report:")  # noqa: T201
    print(metrics["report"])  # noqa: T201

    save_model(model, model_path)
    print(f"Model saved to {model_path}")  # noqa: T201

    configure_mlflow(
        tracking_uri=mlflow_tracking_uri,
        artifact_location=artifact_location,
        experiment_name=DEFAULT_EXPERIMENT,
    )

    with mlflow.start_run(run_name="random_forest") as run:
        mlflow.set_tags(
            {
                "data_version_md5": data_version or "unknown",
                "source": "train_model.py",
            }
        )
        mlflow.log_params(
            {
                "n_estimators": model.n_estimators,
                "max_depth": model.max_depth,
                "random_state": model.random_state,
            }
        )
        mlflow.log_metric("accuracy", metrics["accuracy"])
        mlflow.log_text(metrics["report"], artifact_file="classification_report.txt")

        signature = infer_signature(x_train, model.predict(x_train))
        mlflow.sklearn.log_model(
            model,
            artifact_path="model",
            registered_model_name=REGISTERED_MODEL_NAME,
            signature=signature,
            input_example=x_train.head(5),
        )
        mlflow.log_artifact(str(model_path))
        print(f"MLflow run_id: {run.info.run_id}")  # noqa: T201


if __name__ == "__main__":
    main()
