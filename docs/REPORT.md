# Отчёт по ДЗ 1: Настройка рабочего места Data Scientist

**Студент:** ITMO EPML Student
**Дата:** 21 ноября 2025
**Тема:** Настройка полного рабочего места Data Scientist с современными инженерными практиками

---

## Содержание
1. [Структура проекта](#структура-проекта)
2. [Шаблон проекта](#шаблон-проекта)
3. [Качество кода и pre-commit](#качество-кода-и-pre-commit)
4. [Управление зависимостями](#управление-зависимостями)
5. [Контейнеризация](#контейнеризация)
6. [Git workflow](#git-workflow)
7. [Скриншоты](#скриншоты)
8. [Воспроизведение](#воспроизведение)
9. [Итог](#итог)

---

## Структура проекта
Проект организован по структуре [cookiecutter-data-science](https://drivendata.github.io/cookiecutter-data-science/) и адаптирован под задание.
```
EPML-ITMO/
├── configs/                 # Конфигурации (YAML)
├── data/{raw,processed,external}/  # Данные (.gitkeep, gitignored)
├── docs/                    # Документация (этот отчёт)
├── models/                  # Сохраненные модели (.gitkeep)
├── notebooks/               # Jupyter notebooks
├── reports/figures/         # Скриншоты результатов
├── src/                     # Исходный код (data, features, models, visualization)
├── tests/                   # Pytest тесты
├── .pre-commit-config.yaml  # Хуки: Black, isort, Ruff, MyPy, Bandit, nbqa
├── .gitignore               # ML/DS игноры (данные, модели, эксперименты)
├── .dockerignore            # Игноры для Docker
├── Dockerfile               # Multi-stage сборка
├── pyproject.toml           # Конфигурация Poetry и инструментов
├── poetry.lock              # Зафиксированные версии
├── Makefile                 # Автоматизация команд
├── README.md                # Описание проекта
└── cookiecutter.json        # Метаданные шаблона
```

## Шаблон проекта
Структура проекта основана на [cookiecutter-data-science](https://drivendata.github.io/cookiecutter-data-science/) — стандартном шаблоне для ML/DS проектов.

**Что сделано:**
- Файл `cookiecutter.json` содержит метаданные проекта (название, автор, версия Python, используемые инструменты).
- Структура папок соответствует best practices для Data Science проектов.
- README.md и данный отчёт служат документацией для развёртывания новых проектов по этому образцу.

**Как использовать как шаблон:**
1. Склонировать репозиторий.
2. Удалить `.git/` и специфичные данные проекта.
3. Инициализировать новый репозиторий.
4. Обновить `cookiecutter.json`, `pyproject.toml` и README под новый проект.

Альтернативно: использовать оригинальный [cookiecutter-data-science](https://github.com/drivendata/cookiecutter-data-science):
```bash
pip install cookiecutter
cookiecutter https://github.com/drivendata/cookiecutter-data-science
```

## Качество кода и pre-commit
Все конфигурации хранятся в `pyproject.toml`:

| Инструмент | Назначение | Настройки |
|------------|------------|-----------|
| **Black** | Форматирование | line-length=88, target py311 |
| **isort** | Сортировка импортов | profile=black |
| **Ruff** | Линтер | E,W,F,I,C,B,UP,N,ANN,S,T20,SIM,RET |
| **MyPy** | Статическая типизация | strict, py311 |
| **Bandit** | Безопасность | исключены tests/notebooks |
| **Pytest** | Тестирование | cov, verbose |

**Pre-commit hooks** (`.pre-commit-config.yaml`):
- Базовые проверки: trailing-whitespace, end-of-file-fixer, check-yaml/json, check-large-files
- Форматирование: Black, isort, Ruff
- Линтинг: Ruff, MyPy, Bandit
- Jupyter: nbqa-black, nbqa-isort, nbqa-ruff

**Makefile команды:**
- `make format` — Black + isort
- `make lint` — Ruff + MyPy + Bandit
- `make pre-commit` — все хуки
- `make test` — pytest с покрытием

## Управление зависимостями
**Poetry** с точными версиями пакетов:

**Основные:**
```
python = "3.11.*"
pandas = "2.2.3"
scikit-learn = "1.5.2"
numpy = "2.1.3"
matplotlib = "3.9.2"
seaborn = "0.13.2"
jupyter = "1.1.1"
dvc = "3.64.0"
mlflow = "3.6.0"
```

**Dev-зависимости:**
```
black = "24.10.0"
isort = "5.13.2"
ruff = "0.7.4"
mypy = "1.13.0"
bandit = "1.8.0"
pytest = "8.3.3"
pytest-cov = "6.0.0"
pre-commit = "4.0.1"
```

- `poetry.lock` зафиксирован для полной воспроизводимости.
- `install_poetry.ps1` — скрипт установки Poetry для Windows.

## Контейнеризация
**Multi-stage Dockerfile:**
1. **Builder stage:** устанавливает Poetry и зависимости
2. **Runtime stage:** python:3.11-slim, non-root user, healthcheck

**Особенности:**
- Non-root пользователь `mluser` для безопасности
- Healthcheck для мониторинга
- `.dockerignore` исключает данные, кеши, артефакты

**Использование:**
```bash
docker build -t wine-quality-ml .
docker run -it --rm -v $(pwd)/data:/app/data -v $(pwd)/models:/app/models wine-quality-ml
```

## Git workflow
**Стратегия ветвления:**
- `main` — стабильные релизы
- `develop` — текущая разработка и интеграция

**Настроенные игноры (.gitignore):**
- Python: `__pycache__/`, `*.pyc`, `.venv/`
- ML данные: `data/raw/*`, `data/processed/*` (кроме .dvc файлов)
- Модели: `models/*.pkl`, `models/*.h5`
- Эксперименты: `mlruns/`, `mlflow.db`, `wandb/`
- IDE: `.vscode/`, `.idea/`

## Скриншоты

### Pre-commit hooks
Результат выполнения `poetry run pre-commit run --all-files`:

![Pre-commit hooks](../reports/figures/pre-commit.png)

### Pytest с покрытием
Результат выполнения `poetry run pytest -v --cov=src`:

![Pytest results](../reports/figures/tests.png)

> **Примечание:** Для генерации скриншотов выполните команды выше и сохраните результат в `reports/figures/`.

## Воспроизведение
```bash
# 1. Клонировать репозиторий
git clone <repo-url>
cd EPML-ITMO

# 2. Установить зависимости
poetry install

# 3. Настроить pre-commit
poetry run pre-commit install
poetry run pre-commit run --all-files

# 4. Запустить тесты
poetry run pytest -v --cov=src --cov-report=term-missing

# 5. (Опционально) Docker
docker build -t wine-quality-ml .
docker run -it --rm -v $(pwd)/data:/app/data wine-quality-ml
```

## Итог
✅ **Выполненные требования:**
- Структура проекта по шаблону cookiecutter-data-science
- README и отчёт с полным описанием
- Poetry с зафиксированными версиями зависимостей
- Pre-commit hooks (Black, isort, Ruff, MyPy, Bandit, nbqa)
- Конфигурации в pyproject.toml
- Dockerfile (multi-stage, non-root) и .dockerignore
- .gitignore для ML проекта
- Git workflow с ветками main/develop

Менторы смогут воспроизвести окружение по шагам из раздела "Воспроизведение".
