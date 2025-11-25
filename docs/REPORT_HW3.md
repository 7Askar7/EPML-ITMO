# Отчёт по ДЗ 3: Трекинг экспериментов

**Студент:** ITMO EPML Student  
**Дата:** 26 ноября 2025  
**Инструмент:** MLflow (локальный backend)

---

## Настройка MLflow
- Tracking URI: `sqlite:///mlflow.db`, артефакты: `file:./mlruns`.
- Эксперимент: `wine-quality` (создаётся в `src/models/experiment_tracker.py`), теги включают `data_version_md5` из `dvc.lock`.
- Декоратор `log_experiment` и контекст `mlflow_run` инкапсулируют открытие run, логирование параметров/метрик/артефактов и, при необходимости, моделей.
- Аутентификация не требуется (локальный стор). Доступ к UI: `make mlflow-ui` → `http://localhost:5000`.

## Проведённые эксперименты
- Скрипт `src/models/run_experiments.py` запускает 16 конфигураций (LogisticRegression, RandomForest, GradientBoosting, SVC, KNN, AdaBoost) с разными гиперпараметрами.
- Логируются: accuracy, f1_weighted, параметры модели, confusion matrix (PNG), текст отчёта классификации, артефакт модели (MLflow sklearn flavor). Теги: модель, версия датасета, источник пайплайна.
- Сравнение: через MLflow UI фильтры (`metrics.accuracy`, `tags.model_name`, `tags.data_version_md5`). Top-10 график — `reports/figures/experiments_summary.png`.
- Лучший эксперимент на момент отчёта: `rf_150_depth12` — accuracy 0.6813, f1_weighted 0.6669.

## Интеграция в код
- Общие утилиты: `src/models/experiment_tracker.py` (конфигурация MLflow, декоратор/контекст, чтение версии данных).
- Тренировка основной модели: `src/models/train_model.py` — использует `configure_mlflow`, логирует метрики, отчёт, регистрирует модель `wine-quality-rf` в Model Registry.
- Серия экспериментов: `src/models/run_experiments.py` — использует `log_experiment`, сохраняет артефакты и метрики автоматически.

## Воспроизводимость
1. Подготовка окружения:
   ```bash
   python3.11 -m venv .venv
   .venv/bin/pip install --upgrade pip poetry
   POETRY_VIRTUALENVS_CREATE=false .venv/bin/poetry install
   ```
2. Данные:
   ```bash
   poetry run dvc pull
   make data
   ```
3. Эксперименты и сравнение:
   ```bash
   make experiments            # 15+ run'ов будут залогированы в mlruns
   make mlflow-ui              # UI на 5000 порту для просмотра/сравнения
   ```
4. Проверки/контейнер:
   ```bash
   make test
   make docker-build && make docker-run
   ```

## Скриншоты
- `reports/figures/experiments_summary.png` — топ-эксперименты по accuracy.
- `reports/figures/dvc_pipeline.png` — схема DVC пайплайна данных (из ДЗ2).
- `reports/figures/mlflow_run.png` — пример MLflow-run и модели в Registry.
- Примеры confusion matrix для отдельных экспериментов (например, `reports/figures/cm_rf_150_depth12.png`).

## Итог
Настроен полноценный трекинг экспериментов в MLflow: локальная БД/артефакты, удобные утилиты для автологирования, серия из 15+ запусков с метриками/артефактами и готовым UI для сравнения. Все шаги воспроизводятся командами из Makefile, зависимости зафиксированы в `poetry.lock`.
