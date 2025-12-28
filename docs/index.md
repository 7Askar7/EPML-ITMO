# Wine Quality ML Project

> ML project for wine quality prediction with MLOps best practices

## Overview

This project demonstrates end-to-end machine learning workflow for predicting wine quality using the UCI Wine Quality dataset. It showcases modern MLOps practices including:

- **Data Versioning** with DVC
- **Experiment Tracking** with MLflow
- **Pipeline Orchestration** with Hydra + DVC
- **Model Registry** with MLflow & ClearML
- **CI/CD** with GitHub Actions
- **Documentation** with MkDocs

## Features

| Feature | Tool | Description |
|---------|------|-------------|
| Data Versioning | DVC | Track dataset versions and transformations |
| Experiment Tracking | MLflow | Log metrics, parameters, artifacts |
| Pipeline Orchestration | Hydra + DVC | Configure and run ML pipelines |
| MLOps Platform | ClearML | Full MLOps workflow management |
| Code Quality | Black, Ruff, MyPy | Linting and type checking |
| Testing | pytest | Unit and integration tests |
| Documentation | MkDocs | Auto-generated API docs |

## Quick Links

- [Installation Guide](installation.md) - Set up the development environment
- [Quick Start](quickstart.md) - Run your first experiment
- [API Reference](api/data.md) - Detailed API documentation

## Project Structure

```
EPML-ITMO/
├── configs/            # Configuration files (YAML)
│   ├── clearml/        # ClearML settings
│   └── hydra/          # Hydra experiment configs
├── data/               # Data directory (DVC tracked)
│   ├── raw/            # Original dataset
│   └── processed/      # Train/test splits
├── docs/               # Documentation
├── infra/              # Infrastructure (Docker)
│   └── clearml/        # ClearML server setup
├── models/             # Saved models
├── reports/            # Reports and figures
├── src/                # Source code
│   ├── data/           # Data processing
│   ├── models/         # Model training
│   ├── mlops/          # ClearML utilities
│   └── pipelines/      # Pipeline runners
└── tests/              # Test suite
```

## Getting Started

=== "Poetry"

    ```bash
    git clone https://github.com/7Askar7/EPML-ITMO.git
    cd EPML-ITMO
    poetry install
    poetry run dvc pull
    make train
    ```

=== "Docker"

    ```bash
    git clone https://github.com/7Askar7/EPML-ITMO.git
    cd EPML-ITMO
    docker build -t wine-quality-ml .
    docker run -it wine-quality-ml
    ```

## Dataset

The project uses the [Wine Quality Dataset](https://archive.ics.uci.edu/ml/datasets/wine+quality) from UCI Machine Learning Repository.

| Feature | Description |
|---------|-------------|
| fixed acidity | Tartaric acid concentration |
| volatile acidity | Acetic acid concentration |
| citric acid | Citric acid concentration |
| residual sugar | Sugar remaining after fermentation |
| chlorides | Sodium chloride concentration |
| free sulfur dioxide | Free SO2 |
| total sulfur dioxide | Total SO2 |
| density | Density of wine |
| pH | pH level |
| sulphates | Potassium sulphate concentration |
| alcohol | Alcohol percentage |
| **quality** | Target variable (3-8) |

## Models

The project includes experiments with multiple classifiers:

- **Logistic Regression** - Baseline model
- **Random Forest** - Ensemble method
- **Gradient Boosting** - Gradient boosted trees
- **SVC** - Support Vector Classifier
- **KNN** - K-Nearest Neighbors
- **AdaBoost** - Adaptive boosting

## License

MIT License - see [LICENSE](https://github.com/7Askar7/EPML-ITMO/blob/main/LICENSE) for details.
