"""Script for downloading and processing wine quality dataset."""

from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split


def load_data(data_path: Path) -> pd.DataFrame:
    """Load wine quality dataset.

    Args:
        data_path: Path to the CSV file

    Returns:
        DataFrame with wine quality data
    """
    return pd.read_csv(data_path, sep=";")


def split_data(
    df: pd.DataFrame,
    test_size: float = 0.2,
    random_state: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split data into train and test sets.

    Args:
        df: Input DataFrame
        test_size: Proportion of test set
        random_state: Random seed for reproducibility

    Returns:
        Tuple of (train_df, test_df)
    """
    train_df, test_df = train_test_split(
        df,
        test_size=test_size,
        random_state=random_state,
        stratify=df["quality"],
    )
    return train_df, test_df


def main() -> None:  # pragma: no cover
    """Main function to process dataset."""
    project_dir = Path(__file__).resolve().parents[2]
    raw_data_path = project_dir / "data" / "raw" / "winequality-red.csv"
    processed_dir = project_dir / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)

    # Load data
    df = load_data(raw_data_path)

    # Split data
    train_df, test_df = split_data(df)

    # Save processed data
    train_df.to_csv(processed_dir / "train.csv", index=False)
    test_df.to_csv(processed_dir / "test.csv", index=False)

    print(f"Train set size: {len(train_df)}")  # noqa: T201
    print(f"Test set size: {len(test_df)}")  # noqa: T201


if __name__ == "__main__":
    main()
