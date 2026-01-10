# Wine Quality Prediction — Data Science workspace

[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://7Askar7.github.io/EPML-ITMO/)
[![CI](https://github.com/7Askar7/EPML-ITMO/actions/workflows/ci.yml/badge.svg)](https://github.com/7Askar7/EPML-ITMO/actions/workflows/ci.yml)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)

Полноценное окружение для экспериментов и учебных примеров по МЛ с упором на инженерные практики: по умолчанию включены форматирование, линтинг, статический анализ, тесты, Docker и шаблон для разворачивания новых проектов.

**Документация:** [https://7Askar7.github.io/EPML-ITMO/](https://7Askar7.github.io/EPML-ITMO/)

## Кратко о проекте
- Цель: предсказывать качество вина и показать, как оформить DS-проект по best practices.
- Датасет: Wine Quality (UCI), разметка `quality`, признаки — физико-химические параметры.
- Инструменты: Poetry, pre-commit (Black, isort, Ruff, MyPy, Bandit, nbqa), pytest+cov, Docker (multi-stage, non-root).
- Управление: Makefile для типовых задач, структура по cookiecutter-data-science, инструкции в docs/REPORT_HW1.md.

## Структура
```
EPML-ITMO/
├── configs/            # Конфиги (YAML)
├── data/               # Данные raw/processed/external (gitignored)
├── docs/               # Документация (REPORT.md и др.)
├── models/             # Сохраненные модели (gitignored)
├── notebooks/          # Jupyter ноутбуки
├── reports/            # Отчёты и figures для скриншотов
├── src/                # Исходный код (data, features, models, visualization)
├── tests/              # Тесты pytest
├── .pre-commit-config.yaml
├── .dockerignore       # Игноры для Docker
├── Dockerfile
├── pyproject.toml
└── README.md
```

## Быстрый старт
```bash
git clone <repo-url>
cd EPML-ITMO
poetry install           # установить зависимости (используются точные версии)
poetry run dvc pull      # подтянуть данные из локального DVC remote (data/dvc_remote)
poetry run pre-commit install
poetry run pre-commit run --all-files
poetry run pytest -v
make train               # обучить модель с логированием в MLflow/Model Registry
```

## Основные команды
- `make install` — poetry install + pre-commit install.
- `make format` — Black и isort.
- `make lint` — Ruff + MyPy + Bandit.
- `make test` — pytest с покрытием.
- `make data` — `dvc repro` + `dvc push` (данные и сплиты версионируются).
- `make train` — обучение + логирование метрик/артефактов в MLflow.
- `make pipeline` — полный DVC-пайплайн (split → train → experiments) с пушем кеша.
- `make experiments` — серия из 15+ экспериментов с разными моделями (через Hydra+MLflow).
- `make mlflow-ui` — поднять MLflow UI на `http://localhost:5000`.
- `make docker-build` / `make docker-run` — собрать/запустить контейнер.

## Docker
Многостадийный Dockerfile: builder ставит Poetry и зависимости, runtime — лёгкий python:3.11-slim с non-root пользователем и healthcheck. Игнор по `.dockerignore`.

## Качество кода
Настройки Black/isort/Ruff/MyPy/Bandit/pytest хранятся в `pyproject.toml`. Pre-commit подтягивает те же инструменты, плюс базовые проверки файлов и nbqa для ноутбуков.

## Версионирование данных и моделей
- **DVC**: локальный remote `data/dvc_remote` уже содержит кеш с `winequality-red.csv` и сплитами; пайплайн `dvc.yaml` состоит из `import-url` + стадии `split` (`python3 -m src.data.make_dataset`). Используйте `poetry run dvc repro` и `poetry run dvc push`.
- **MLflow**: локальный backend `sqlite:///mlflow.db` и артефакты в `./mlruns`. Запуск обучения (`make train`) логирует метрики, params и артефакты, регистрирует модель `wine-quality-rf` в Model Registry. UI доступен через `make mlflow-ui`.
- **Фиксация зависимостей**: все пакеты (включая DVC/MLflow) зафиксированы в `pyproject.toml`/`poetry.lock`.

## Трекинг экспериментов
- MLflow настроен в коде (`src/models/experiment_tracker.py`), дефолт: SQLite backend `mlflow.db`, артефакты `mlruns/`, эксперимент `wine-quality`.
- Декоратор/контекст для автологирования — `log_experiment`/`mlflow_run`; утилита `get_data_version` тянет md5 из `dvc.lock` и кладёт в теги.
- Скрипт `src/models/run_experiments.py` запускает 15+ конфигураций (LogReg, RF, GBoost, SVC, KNN, AdaBoost), логирует метрики/параметры, confusion matrix и отчёт; модели сохраняются как артефакты MLflow, итоговый обзор — `reports/figures/experiments/experiments_summary.png`.
- Команда `make experiments` воспроизводит серию через Hydra (конфиги в `configs/hydra/algorithms/*.yaml`, можно выбрать, например, `algorithms=quick`).

## Оркестрация (ДЗ 4)
- **Инструмент:** DVC Pipelines (кэширование, зависимостями и параллельным `dvc repro -j`). Стадии: `split` → `train` → `experiments`. Outputs: данные, модель `models/wine_quality_model.pkl`, артефакты экспериментов (`reports/figures/experiments/*`).
- **Конфигурации:** Hydra (`configs/hydra/config.yaml` + алгоритм-группы). Можно менять набор моделей через `algorithms=<variant>` (например, `quick`), валидация уникальности/числа экспериментов в `src/pipelines/run_hydra_pipeline.py`.
- **Мониторинг:** summary-файлы `experiments_top10.csv`, `status.txt` и график `experiments_summary.png`; MLflow UI для сравнения метрик/артефактов.

## Git Workflow (стратегия ветвления)

Используется упрощённая модель **Git Flow**:

| Ветка | Назначение |
|-------|------------|
| `main` | Стабильные релизы |
| `develop` | Интеграция фич |
| `feature/*` | Новая функциональность |
| `fix/*` | Исправление багов |
| `docs/*` | Документация |

**Пример workflow:**
```bash
git checkout develop && git pull
git checkout -b feature/my-feature    # создать ветку
# ... разработка ...
git commit -m "feat: описание"
git checkout develop && git merge feature/my-feature
git push origin develop
```

## ClearML (HW5)

- `cp .env.clearml.example .env.clearml` и заполнить ключи из ClearML UI.
- `make clearml-server-up` — локальный ClearML сервер (Web: 8090, API: 8008, Files: 8091).
- `make clearml-pipeline` — быстрый прогон (Hydra quick) с логированием в ClearML.
- `make clearml-experiments` — полный набор экспериментов (15+), публикация в Model Registry.
- Подробности и скриншоты: `docs/REPORT_HW5.md`.

## Документация (HW6)

Документация проекта доступна онлайн и локально:

- **Онлайн:** [https://7Askar7.github.io/EPML-ITMO/](https://7Askar7.github.io/EPML-ITMO/)
- **Локально:** `make docs-serve` → http://localhost:8000

Команды для работы с документацией:
- `make docs-serve` — запустить локальный сервер MkDocs
- `make docs-build` — собрать статическую документацию
- `make docs-deploy` — опубликовать на GitHub Pages

Документация автоматически обновляется при пуше в main/develop через GitHub Actions.

Подробнее: [docs/REPORT_HW6.md](docs/REPORT_HW6.md)

## Шаблон проекта
Структура проекта основана на [cookiecutter-data-science](https://drivendata.github.io/cookiecutter-data-science/). Файл `cookiecutter.json` содержит метаданные проекта.

**Как использовать как шаблон:**
1. Склонировать репозиторий
2. Удалить `.git/` и специфичные данные
3. Обновить `cookiecutter.json`, `pyproject.toml` и README под новый проект
4. Инициализировать новый git-репозиторий

Альтернатива — использовать оригинальный cookiecutter-data-science:
```bash
pip install cookiecutter
cookiecutter https://github.com/drivendata/cookiecutter-data-science
```
