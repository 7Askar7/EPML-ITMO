# Wine Quality Prediction — Data Science workspace

Полноценное окружение для экспериментов и учебных примеров по МЛ с упором на инженерные практики: по умолчанию включены форматирование, линтинг, статический анализ, тесты, Docker и шаблон для разворачивания новых проектов.

## Кратко о проекте
- Цель: предсказывать качество вина и показать, как оформить DS-проект по best practices.
- Датасет: Wine Quality (UCI), разметка `quality`, признаки — физико-химические параметры.
- Инструменты: Poetry, pre-commit (Black, isort, Ruff, MyPy, Bandit, nbqa), pytest+cov, Docker (multi-stage, non-root).
- Управление: Makefile для типовых задач, шаблон Cookiecutter и инструкции в docs/REPORT.md.

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
├── Dockerfile
├── pyproject.toml
└── README.md
```

## Быстрый старт
```bash
git clone <repo-url>
cd EPML-ITMO
poetry install           # установить зависимости (используются точные версии)
poetry run pre-commit install
poetry run pre-commit run --all-files
poetry run pytest -v
```

## Основные команды
- `make install` — poetry install + pre-commit install.
- `make format` — Black и isort.
- `make lint` — Ruff + MyPy + Bandit.
- `make test` — pytest с покрытием.
- `make docker-build` / `make docker-run` — собрать/запустить контейнер.

## Docker
Многостадийный Dockerfile: builder ставит Poetry и зависимости, runtime — лёгкий python:3.11-slim с non-root пользователем и healthcheck. Игнор по `.dockerignore`.

## Качество кода
Настройки Black/isort/Ruff/MyPy/Bandit/pytest хранятся в `pyproject.toml`. Pre-commit подтягивает те же инструменты, плюс базовые проверки файлов и nbqa для ноутбуков.

## Шаблон
`cookiecutter.json` лежит в корне: можно использовать текущий репозиторий как шаблон (`cookiecutter .`) либо вынести его в отдельный каталог для генерации новых проектов со схожей структурой.
