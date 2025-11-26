# Отчёт по ДЗ 2: Версионирование данных и моделей

**Выбор инструментов:**
- Данные: DVC (локальный remote).
- Модели: MLflow (tracking + Model Registry).

## Что требовалось и что сделано
1) **Настроить инструмент для данных (DVC)**
   - Установлен DVC, инициализирован репозиторий.
   - Remote: `data/dvc_remote` лежит в репо (офлайн-воспроизведение), прописан в `.dvc/config`.
   - Пайплайн: `dvc.yaml` со стадией `split` (`poetry run python -m src.data.make_dataset`) → `data/processed/train.csv`, `data/processed/test.csv`.
   - Версии данных фиксируются в `dvc.lock`, изменения пушатся `dvc push`.

2) **Настроить инструмент для моделей (MLflow)**
   - Backend: `sqlite:///mlflow.db`, артефакты: `./mlruns`.
   - Скрипт `src/models/train_model.py` логирует метрики, параметры и отчёт классификации, регистрирует модель `wine-quality-rf` в Model Registry, тегирует версию данных из `dvc.lock`.
   - Трекинг включён через утилиту `configure_mlflow`; UI запускается `make mlflow-ui`.

3) **Воспроизводимость**
   - Зависимости зафиксированы в `pyproject.toml`/`poetry.lock` (Poetry).
   - Инструкции: `poetry install`, `poetry run dvc pull`, `make data`, `make train`, `make mlflow-ui`; Dockerfile уже готов для контейнеризации.
   - Проверка: `make test`/`pytest`.

4) **Отчёт**
   - Текущий файл + иллюстрации: `reports/figures/dvc_pipeline.png`, `reports/figures/mlflow_run.png`.
   - Описание настроек DVC/MLflow, шагов воспроизведения и скриншотов добавлено в README и этот отчёт.

## Скриншоты/артефакты
- `reports/figures/dvc_pipeline.png` — схема стадий DVC.
- `reports/figures/mlflow_run.png` — пример логированного запуска и регистрации модели.

## Команды для быстрой проверки
```bash
poetry install
poetry run dvc pull
make data
make train
make mlflow-ui   # UI на 5000 порту
```
