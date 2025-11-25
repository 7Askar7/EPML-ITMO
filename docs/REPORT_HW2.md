# Отчёт по ДЗ 2: Версионирование данных и моделей

**Студент:** ITMO EPML Student  
**Дата:** 26 ноября 2025  
**Выбор инструментов:** DVC (данные), MLflow (модели)

---

## Что настроено
- **DVC для данных**: локальный remote `data/dvc_remote` уже содержит кеш датасета `winequality-red.csv` и результатов сплита. Пайплайн `dvc.yaml` → `import-url` + стадия `split` (`python3 -m src.data.make_dataset`) с зависимостями `data/raw/winequality-red.csv` и `src/data/make_dataset.py`, выходами `data/processed/train.csv` и `data/processed/test.csv`.
- **Автоматическое версионирование**: `dvc repro` пересчитывает и фиксирует изменения в `dvc.lock`, `dvc push` кладёт их в remote (лежит в репо, поэтому воспроизводится офлайн).
- **MLflow для моделей**: трекинг на `sqlite:///mlflow.db`, артефакты в `./mlruns`. Эксперимент `wine-quality`, зарегистрированная модель `wine-quality-rf` (версия 1). `make train` логирует гиперпараметры, метрику accuracy, текстовый отчёт классификации, тег `data_version_md5` из `dvc.lock`, артефакты модели и регистрирует её в Model Registry.
- **Команды**: `make data` (DVC repro + push), `make train` (обучение + MLflow), `make mlflow-ui` (UI на `http://localhost:5000`), остальные команды из Makefile работают как прежде.
- **Зависимости зафиксированы**: DVC, MLflow, PyYAML добавлены в `pyproject.toml`/`poetry.lock` для воспроизводимости.

## Воспроизводимость
1. Python 3.11+. Создать in-project env и поставить Poetry (без глобальных установок):
   ```bash
   python3.11 -m venv .venv
   .venv/bin/pip install --upgrade pip poetry
   POETRY_VIRTUALENVS_CREATE=false .venv/bin/poetry install
   ```
2. Подтянуть данные и пересчитать пайплайн:
   ```bash
   poetry run dvc pull      # remote уже внутри репозитория
   make data                # dvc repro + dvc push
   ```
3. Обучить модель с логированием:
   ```bash
   make train               # метрики/артефакты в mlruns, модель в Registry
   make mlflow-ui           # для сравнения версий, порт 5000
   ```
4. Проверки и Docker:
   ```bash
   make test
   make docker-build
   make docker-run          # монтирует ./data и ./models
   ```
   Перед сборкой/запуском контейнера убедитесь, что `poetry run dvc pull` выполнен, чтобы в volume `./data` лежали актуальные сплиты.

## Скриншоты результатов
- `reports/figures/dvc_pipeline.png` — схема текущего DVC-пайплайна (import-url → split).
- `reports/figures/mlflow_run.png` — сводка MLflow-run c метрикой и версией модели в Registry.

## Итог
Настроены версионирование данных (DVC с локальным remote, пайплайном и lock-файлом) и моделей (MLflow tracking + Model Registry на SQLite). Все шаги воспроизводимы через Poetry и Makefile, данные доступны офлайн из включённого remote, модели логируются и сравниваются через MLflow UI.
