# Data Processing Module

This module handles data loading, preprocessing, and splitting for the Wine Quality dataset.

## Overview

The data processing pipeline includes:

1. Loading raw CSV data
2. Splitting into train/test sets
3. Saving processed datasets

## Module Reference

**File:** `src/data/make_dataset.py`

### Functions

```python
def load_raw_data(path: str) -> pd.DataFrame:
    """Load raw wine quality CSV data.

    Args:
        path: Path to the CSV file

    Returns:
        DataFrame with wine quality data
    """

def create_train_test_split(
    df: pd.DataFrame,
    test_size: float = 0.2,
    random_state: int = 42
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split data into train and test sets.

    Args:
        df: Input DataFrame
        test_size: Proportion for test set
        random_state: Random seed for reproducibility

    Returns:
        Tuple of (train_df, test_df)
    """

def save_splits(train_df: pd.DataFrame, test_df: pd.DataFrame, output_dir: str) -> None:
    """Save train/test splits to CSV files.

    Args:
        train_df: Training DataFrame
        test_df: Test DataFrame
        output_dir: Output directory path
    """
```

## Usage Examples

### Load and Process Data

```python
from src.data.make_dataset import load_raw_data, save_splits

# Load raw data
df = load_raw_data("data/raw/winequality-red.csv")

# Create train/test splits and save
save_splits(df, output_dir="data/processed")
```

### Load Processed Data

```python
from src.models.train_model import load_processed_data

train_df, test_df = load_processed_data("data/processed")
print(f"Train: {len(train_df)}, Test: {len(test_df)}")
```

## Data Flow

```
data/raw/winequality-red.csv
         │
         ▼
    make_dataset.py
         │
         ├──► data/processed/train.csv
         │
         └──► data/processed/test.csv
```

## DVC Integration

Data is versioned using DVC:

```bash
# Pull latest data
dvc pull

# Track changes
dvc add data/raw/winequality-red.csv

# Push to remote
dvc push
```

## Configuration

Dataset configuration in `configs/config.yaml`:

```yaml
data:
  raw_path: data/raw/winequality-red.csv
  processed_dir: data/processed
  test_size: 0.2
  random_state: 42
```
