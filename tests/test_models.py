"""Tests for model training and evaluation utilities."""

from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

from src.models.train_model import (
    evaluate_model,
    load_processed_data,
    save_model,
    train_model,
)


def _sample_dataframe() -> pd.DataFrame:
    """Create a small dataset for testing."""
    return pd.DataFrame(
        {
            "fixed_acidity": [7.0, 6.5, 7.2, 6.8, 7.1, 6.9],
            "pH": [3.2, 3.1, 3.3, 3.0, 3.2, 3.1],
            "quality": [5, 6, 5, 6, 5, 6],
        }
    )


def test_load_processed_data(tmp_path: Path) -> None:
    """Load train/test CSVs from a processed directory."""
    train_df = _sample_dataframe().iloc[:4].reset_index(drop=True)
    test_df = _sample_dataframe().iloc[4:].reset_index(drop=True)
    train_df.to_csv(tmp_path / "train.csv", index=False)
    test_df.to_csv(tmp_path / "test.csv", index=False)

    loaded_train, loaded_test = load_processed_data(tmp_path)

    assert loaded_train.equals(train_df)
    assert loaded_test.equals(test_df)


def test_train_model_fits_and_predicts() -> None:
    """Train model and ensure it can predict."""
    df = _sample_dataframe()
    x_train = df.drop("quality", axis=1)
    y_train = df["quality"]

    model = train_model(x_train, y_train)

    assert isinstance(model, RandomForestClassifier)
    assert hasattr(model, "estimators_")
    preds = model.predict(x_train)
    assert len(preds) == len(y_train)


def test_save_model_writes_pickle(tmp_path: Path) -> None:
    """save_model should persist the fitted estimator."""
    df = _sample_dataframe()
    model = train_model(df.drop("quality", axis=1), df["quality"])
    model_path = tmp_path / "model.pkl"

    save_model(model, model_path)

    loaded = joblib.load(model_path)
    assert isinstance(loaded, RandomForestClassifier)


def test_evaluate_model_outputs_metrics() -> None:
    """evaluate_model returns accuracy and text report."""
    df = _sample_dataframe()
    model = train_model(df.drop("quality", axis=1), df["quality"])

    metrics = evaluate_model(model, df.drop("quality", axis=1), df["quality"])

    assert "accuracy" in metrics
    assert "report" in metrics
    assert metrics["accuracy"]
    assert "precision" in metrics["report"]
