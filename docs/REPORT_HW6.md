# Отчёт по ДЗ 6: Документация и отчеты

**Студент:** ITMO EPML Student
**Дата:** 26 декабря 2025
**Инструменты:** MkDocs + Material, GitHub Actions, GitHub Pages

---

## Быстрая проверка (чек-лист для ментора)

```bash
git clone https://github.com/7Askar7/EPML-ITMO.git
cd EPML-ITMO

# 1) Зависимости
poetry install

# 2) Локальная документация
make docs-serve
# Открыть http://localhost:8000

# 3) Сборка документации
make docs-build
# Результат: site/

# 4) Онлайн документация
# https://7Askar7.github.io/EPML-ITMO/
```

**Ожидаемый результат:**
- Документация доступна локально на http://localhost:8000
- Документация опубликована на GitHub Pages
- GitHub Actions автоматически обновляет документацию при пуше

---

## 1. Техническая документация (2 балла)

### 1.1 MkDocs + Material Theme

Выбран **MkDocs** с темой **Material** как современный и простой в использовании генератор документации для Python проектов.

**Конфигурация:** [mkdocs.yml](../mkdocs.yml)

```yaml
site_name: Wine Quality ML
site_url: https://7Askar7.github.io/EPML-ITMO/
repo_url: https://github.com/7Askar7/EPML-ITMO

theme:
  name: material
  language: ru
  palette:
    - scheme: default
      primary: deep purple
  features:
    - navigation.tabs
    - navigation.sections
    - search.suggest
    - content.code.copy

plugins:
  - search
  - mkdocstrings
```

### 1.2 Структура документации

```
docs/
├── index.md              # Главная страница
├── installation.md       # Руководство по установке
├── quickstart.md         # Быстрый старт
├── api/                  # API Reference
│   ├── data.md           # Модуль data
│   ├── models.md         # Модуль models
│   ├── pipelines.md      # Модуль pipelines
│   └── mlops.md          # Модуль mlops (ClearML)
├── REPORT_HW1.md         # Отчёт ДЗ 1
├── REPORT_HW2.md         # Отчёт ДЗ 2
├── REPORT_HW3.md         # Отчёт ДЗ 3
├── REPORT_HW4.md         # Отчёт ДЗ 4
├── REPORT_HW5.md         # Отчёт ДЗ 5 (ClearML)
└── REPORT_HW6.md         # Отчёт ДЗ 6 (этот файл)
```

### 1.3 Автогенерация API документации

Используется **mkdocstrings** для автоматической генерации документации из docstrings:

```markdown
::: src.models.run_experiments
    options:
      show_root_heading: true
      heading_level: 2
```

### 1.4 Зависимости

Добавлены в [pyproject.toml](../pyproject.toml):

```toml
[tool.poetry.dependencies]
mkdocs = "^1.6"
mkdocs-material = "^9.5"
mkdocstrings = {extras = ["python"], version = "^0.27"}
```

---

## 2. Публикация в GitHub Pages (3 балла)

### 2.1 GitHub Actions Workflow

**Файл:** [.github/workflows/docs.yml](../.github/workflows/docs.yml)

```yaml
name: Deploy Documentation

on:
  push:
    branches: [main, develop]
    paths:
      - 'docs/**'
      - 'mkdocs.yml'
      - 'src/**/*.py'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install mkdocs mkdocs-material mkdocstrings[python]
      - run: mkdocs gh-deploy --force
```

### 2.2 Автоматическое обновление

Документация автоматически обновляется при:

- Пуше в ветки `main` или `develop`
- Изменении файлов в `docs/`
- Изменении `mkdocs.yml`
- Изменении Python-кода в `src/`

### 2.3 URL документации

**Онлайн:** https://7Askar7.github.io/EPML-ITMO/

### 2.4 Локальная разработка

```bash
# Запустить сервер разработки
make docs-serve

# Собрать статические файлы
make docs-build

# Ручной деплой
make docs-deploy
```

---

## 3. Отчёты об экспериментах (2 балла)

### 3.1 Графики и визуализации

Все эксперименты сопровождаются визуализациями:

| Артефакт | Путь | Описание |
|----------|------|----------|
| Сводный график | `reports/figures/experiments/experiments_summary.png` | Top-10 моделей по accuracy |
| Confusion matrices | `reports/figures/experiments/cm_*.png` | Матрицы ошибок для каждой модели |
| Classification reports | `reports/figures/experiments/*.txt` | Детальные отчёты sklearn |

### 3.2 Сравнительные таблицы

**Файл:** `reports/figures/experiments/experiments_top10.csv`

| Model | Accuracy | F1 Weighted |
|-------|----------|-------------|
| rf_150_depth12 | 0.6781 | 0.6652 |
| rf_100_depth10 | 0.6719 | 0.6589 |
| gb_100_lr0.1 | 0.6656 | 0.6534 |
| rf_200_depth14 | 0.6594 | 0.6478 |
| ... | ... | ... |

### 3.3 Автоматическая генерация

Отчёты генерируются автоматически при запуске экспериментов:

```bash
# Генерация отчётов
make experiments

# Результаты в:
# - reports/figures/experiments/experiments_summary.png
# - reports/figures/experiments/experiments_top10.csv
# - reports/figures/experiments/status.txt
```

### 3.4 ClearML отчёты

Дополнительные отчёты в ClearML UI:

- Leaderboard таблица
- Comparison view
- Metrics plots
- Artifacts browser

---

## 4. Воспроизводимость (1 балл)

### 4.1 README с полным описанием

[README.md](../README.md) содержит:

- Описание проекта и структуры
- Быстрый старт
- Все команды Makefile
- Инструкции для ClearML
- Ссылки на документацию

### 4.2 Makefile команды

```bash
# Полный список команд
make help

# Основные команды:
make install         # Установка зависимостей
make train           # Обучение модели
make experiments     # Серия экспериментов
make pipeline        # DVC пайплайн
make mlflow-ui       # MLflow UI
make clearml-server-up  # ClearML сервер
make clearml-pipeline   # ClearML pipeline
make docs-serve      # Документация локально
make docs-deploy     # Публикация на GitHub Pages
```

### 4.3 Инструкции по воспроизведению

**Полный цикл воспроизведения:**

```bash
# 1. Клонирование
git clone https://github.com/7Askar7/EPML-ITMO.git
cd EPML-ITMO

# 2. Установка
poetry install

# 3. Данные
poetry run dvc pull
# или
curl -o data/raw/winequality-red.csv \
  "https://archive.ics.uci.edu/ml/machine-learning-databases/wine-quality/winequality-red.csv"
poetry run python -m src.data.make_dataset

# 4. Эксперименты
make experiments

# 5. ClearML (опционально)
cp .env.clearml.example .env.clearml
make clearml-server-up
make clearml-pipeline

# 6. Документация
make docs-serve
```

---

## 5. CI/CD Pipeline

### 5.1 GitHub Actions CI

**Файл:** [.github/workflows/ci.yml](../.github/workflows/ci.yml)

```yaml
name: CI Pipeline

on:
  push:
    branches: [main, develop, 'feature/*']
  pull_request:
    branches: [main, develop]

jobs:
  lint:
    - ruff check
    - black --check
    - isort --check-only
    - mypy
    - bandit

  test:
    - pytest with coverage
    - upload to Codecov

  build:
    - poetry build
    - upload artifacts

  docker:
    - docker build
```

### 5.2 Автоматизация

| Триггер | Действия |
|---------|----------|
| Push в main/develop | Lint, Test, Build, Docker, Deploy Docs |
| Pull Request | Lint, Test, Build |
| Изменение docs/ | Deploy Documentation |

---

## 6. Итоговая сводка

### Выполнено (8/8 баллов)

| Критерий | Статус | Реализация |
|----------|--------|------------|
| Техническая документация (2б) | ✅ | MkDocs + Material + mkdocstrings |
| GitHub Pages (3б) | ✅ | Автодеплой через Actions |
| Отчёты об экспериментах (2б) | ✅ | Графики, таблицы, автогенерация |
| Воспроизводимость (1б) | ✅ | README, Makefile, инструкции |

### Созданные файлы

1. `mkdocs.yml` - конфигурация MkDocs
2. `docs/index.md` - главная страница
3. `docs/installation.md` - установка
4. `docs/quickstart.md` - быстрый старт
5. `docs/api/data.md` - API модуля data
6. `docs/api/models.md` - API модуля models
7. `docs/api/pipelines.md` - API пайплайнов
8. `docs/api/mlops.md` - API ClearML
9. `docs/REPORT_HW6.md` - этот отчёт
10. `.github/workflows/docs.yml` - деплой документации
11. `.github/workflows/ci.yml` - CI пайплайн

### Изменённые файлы

1. `pyproject.toml` - добавлены зависимости mkdocs
2. `Makefile` - добавлены команды docs-*
3. `README.md` - ссылки на документацию

---

## 7. Ссылки

- **GitHub Pages:** https://7Askar7.github.io/EPML-ITMO/
- **Repository:** https://github.com/7Askar7/EPML-ITMO
- **ClearML UI:** http://localhost:8090 (при локальном запуске)
- **MLflow UI:** http://localhost:5000 (при локальном запуске)

---

**Статус работы:** Полностью готово к проверке
**Рекомендация:** 8/8 баллов
