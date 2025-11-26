# Отчёт по ДЗ 4: Автоматизация ML пайплайнов

**Студент:** ITMO EPML Student  
**Дата:** 26 ноября 2025  
**Оркестрация:** DVC Pipelines  
**Конфигурации:** Hydra

---

## Оркестрация (DVC Pipelines)
- Пайплайн `dvc.yaml` с тремя стадиями и кэшированием:
  1) `split` — `poetry run python -m src.data.make_dataset` → `data/processed/train.csv`, `data/processed/test.csv`.
  2) `train` — `poetry run python -m src.models.train_model` → `models/wine_quality_model.pkl`, логирование в MLflow + Model Registry.
  3) `experiments` — `poetry run python -m src.pipelines.run_hydra_pipeline algorithms=full` → пакет из 15+ экспериментов, артефакты в `reports/figures/experiments/*`.
- Запуск/кэш: `poetry run dvc repro -j 2` (параллельные стадии), `poetry run dvc push` — все артефакты уходят в локальный remote `data/dvc_remote`.
- Мониторинг: итоговые файлы `experiments_summary.png`, `experiments_top10.csv`, `status.txt`, плюс MLflow UI.

## Конфигурации (Hydra)
- Базовый конфиг: `configs/hydra/config.yaml` (`defaults` + `_self_`, фиксирует `tracking_uri`, `artifact_location`, теги).
- Группы алгоритмов: `configs/hydra/algorithms/full.yaml` (16 конфигураций), `configs/hydra/algorithms/quick.yaml` (укороченный сет).
- Валидация: в `src/pipelines/run_hydra_pipeline.py` проверяется уникальность имён и количество экспериментов (>=15).
- Композиция: можно запускать быстрый набор `poetry run python -m src.pipelines.run_hydra_pipeline algorithms=quick` или свой вариант, переопределяя параметры в CLI.

## Интеграция и мониторинг
- Кодовая интеграция: утилиты `src/models/experiment_tracker.py` (контекст/декоратор MLflow) и `src/models/run_experiments.py` (поддерживает Hydra-эксперименты, сохраняет confusion matrix, отчёты, summary).
- MLflow: backend `sqlite:///mlflow.db`, артефакты `./mlruns`, эксперимент `wine-quality`. Теги включают версию данных из `dvc.lock`.
- Уведомления/артефакты: `status.txt` с лучшей моделью, `experiments_top10.csv`, `experiments_summary.png`; MLflow UI через `make mlflow-ui`.

## Воспроизводимость
1. Окружение:
   ```bash
   python3.11 -m venv .venv
   .venv/bin/pip install --upgrade pip poetry
   POETRY_VIRTUALENVS_CREATE=false .venv/bin/poetry install
   ```
2. Данные и пайплайн:
   ```bash
   poetry run dvc pull             # подтянуть кеш из data/dvc_remote
   make pipeline                   # split -> train -> experiments + push
   ```
   Параллель: `poetry run dvc repro -j 2`.
3. Быстрые/альтернативные эксперименты:
   ```bash
   poetry run python -m src.pipelines.run_hydra_pipeline algorithms=quick
   ```
4. Мониторинг:
   ```bash
   make mlflow-ui                  # UI на 5000 порту
   ls reports/figures/experiments  # артефакты, summary, статус
   ```
5. Тесты/контейнер:
   ```bash
   make test
   make docker-build && make docker-run
   ```

## Скриншоты
- `reports/figures/dvc_pipeline.png` — схема DVC пайплайна (из ДЗ2, актуальна с тремя стадиями).
- `reports/figures/experiments/experiments_summary.png` — топ-10 экспериментов по accuracy.
- Примеры confusion matrix: `reports/figures/experiments/cm_rf_150_depth12.png` и др.

## Итог
Реализована автоматизация на DVC Pipelines (кэш, зависимые стадии, возможность параллели) и управление конфигурациями через Hydra (композиция/валидация наборов экспериментов). MLflow интегрирован на всех этапах, артефакты и метрики сохраняются, воспроизводимость обеспечена через DVC + Poetry + Makefile команды.
