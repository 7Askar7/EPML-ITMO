# Отчёт по ДЗ 1: Настройка рабочего места Data Scientist

**Студент:** ITMO EPML Student
**Дата:** 21 ноября 2025
**Тема:** Настройка полного рабочего места Data Scientist с современными инженерными практиками

---

## Содержание
1. [Структура проекта](#структура-проекта)
2. [Шаблон Cookiecutter](#шаблон-cookiecutter)
3. [Качество кода и pre-commit](#качество-кода-и-pre-commit)
4. [Управление зависимостями](#управление-зависимостями)
5. [Контейнеризация](#контейнеризация)
6. [Git workflow](#git-workflow)
7. [Скриншоты](#скриншоты)
8. [Воспроизведение](#воспроизведение)
9. [Итог](#итог)

---

## Структура проекта
Проект собран по структуре cookiecutter-data-science и адаптирован под задание.
```
EPML-ITMO/
├── configs/                 # Конфигурации
├── data/{raw,processed,external}/ (.gitkeep)
├── docs/                    # Документация (этот отчёт)
├── models/                  # Сохраненные модели (.gitkeep)
├── notebooks/               # Jupyter notebooks
├── reports/figures/         # Скриншоты результатов
├── src/                     # Исходный код (data, features, models, visualization)
├── tests/                   # Pytest
├── .pre-commit-config.yaml  # Хуки: Black, isort, Ruff, MyPy, Bandit, nbqa
├── .gitignore               # ML/DS игноры (данные, модели, эксперименты)
├── Dockerfile, .dockerignore
├── pyproject.toml, poetry.lock
├── Makefile, README.md
└── cookiecutter.json        # Контекст шаблона
```

## Шаблон Cookiecutter
- В корне лежит `cookiecutter.json` с параметрами проекта (`project_name`, `project_slug`, автор, версия Python, включение Docker, pre-commit и т.д.).
- Репозиторий можно использовать как шаблон: `cookiecutter .` создаст копию структуры с подстановкой значений из опросника.
- Для вынесения в отдельный каталог: `cookiecutter gh:<your-fork>/EPML-ITMO` или `cookiecutter path/to/EPML-ITMO`.
- README и REPORT описывают структуру и шаги развёртывания для новых проектов.

## Качество кода и pre-commit
- Конфигурации в `pyproject.toml`:
  - Black (line-length 88, target py311)
  - isort (profile=black)
  - Ruff (E,W,F,I,C,B,UP,N,ANN,S,T20,SIM,RET; исключены ANN101/ANN102/S101)
  - MyPy (strict, py311)
  - Bandit (исключены tests/notebooks, skip B101)
  - Pytest (cov, verbose, пути тестов)
- `.pre-commit-config.yaml`: базовые проверки файлов + Black, isort, Ruff, MyPy, Bandit, nbqa-* для ноутбуков.
- Makefile цели: `format` (Black+isort), `lint` (Ruff+MyPy+Bandit), `pre-commit` (run --all-files), `test` (pytest с покрытием).

## Управление зависимостями
- Poetry с pinned-версиями:
  - Основные: `python = "3.11.*"`, pandas 2.2.3, scikit-learn 1.5.2, numpy 2.1.3, matplotlib 3.9.2, seaborn 0.13.2, jupyter 1.1.1.
  - Dev: black 24.10.0, isort 5.13.2, ruff 0.7.4, mypy 1.13.0, bandit 1.8.0, pytest 8.3.3, pytest-cov 6.0.0, pre-commit 4.0.1, pandas-stubs 2.2.3.241126, types-setuptools 75.6.0.20241126.
- Poetry создаёт .venv в проекте; lock-файл зафиксирован (`poetry.lock`) для воспроизводимости.
- Скрипт `install_poetry.ps1` для Windows (включает проверку Python и добавление Poetry в PATH).

## Контейнеризация
- Multi-stage `Dockerfile`: builder ставит Poetry и основной набор зависимостей; runtime — `python:3.11-slim`, non-root user, healthcheck; окружение `.venv` копируется из builder.
- `.dockerignore` исключает данные, артефакты, git, кеши и логи.
- Запуск: `docker build -t wine-quality-ml .` затем `docker run -it --rm -v $(pwd)/data:/app/data wine-quality-ml`.

## Git workflow
- Репозиторий и игноры настроены; рекомендации по веткам:
  - `main` — стабильные релизы.
  - `develop` — интеграция фич.
  - `feature/*` и `fix/*` — работа над задачами и багами.
- Старт: `git init`, `git add .`, `git commit -m "Initial DS workspace setup"`, затем `git checkout -b develop` и рабочие feature-ветки.

## Скриншоты
- Результаты прогонов сохранены в `reports/figures/`:
  - ![pre-commit hooks](../reports/figures/pre-commit.png) — окружения установлены, все хуки прошли (файлов для проверки не было)
  - ![pytest](../reports/figures/tests.png) — 6 тестов пройдено, покрытие `src` 100%

## Воспроизведение
1. Клонировать репозиторий и перейти в каталог.
2. Установить Poetry (см. `install_poetry.ps1` для Windows).
3. `poetry install` — установить зависимости по зафиксированным версиям.
4. `poetry run pre-commit install && poetry run pre-commit run --all-files` — прогнать хуки.
5. `poetry run pytest -v --cov=src --cov-report=term-missing` — тесты.
6. Опционально: `docker build -t wine-quality-ml .` и `docker run ...` для контейнера.

## Итог
✅ Выполнены требования: структура проекта по шаблону, README и отчёт, зафиксированные версии зависимостей, настроены pre-commit и линтеры/форматтеры (Black, isort, Ruff, MyPy, Bandit), lock-файл и Poetry-окружение, Dockerfile и .dockerignore, git-игноры и описанный workflow, добавлены скриншоты выполнения. Mentors смогут воспроизвести окружение по шагам выше.
