"""Tests for data processing functions."""

from pathlib import Path

import pandas as pd

from src.data.make_dataset import load_data, split_data


def test_split_data() -> None:
    """Test data splitting function."""
    # Create sample data
    df = pd.DataFrame(
        {
            "feature1": range(100),
            "feature2": range(100, 200),
            "quality": [3, 4, 5, 6, 7] * 20,
        }
    )

    # Split data
    train_df, test_df = split_data(df, test_size=0.2, random_state=42)

    # Assertions
    assert len(train_df) == 80
    assert len(test_df) == 20
    assert len(train_df) + len(test_df) == len(df)
    assert set(train_df.columns) == set(test_df.columns)


def test_load_data(tmp_path: Path) -> None:
    """Ensure CSV is read with expected separator."""
    data_path = tmp_path / "wine.csv"
    expected = pd.DataFrame({"a": [1, 2], "quality": [3, 4]})
    expected.to_csv(data_path, sep=";", index=False)

    loaded = load_data(data_path)

    assert loaded.equals(expected)
