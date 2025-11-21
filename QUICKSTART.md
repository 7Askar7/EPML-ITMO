# Быстрый старт

Это краткое руководство для быстрого запуска проекта.

## Минимальная установка (3 команды)

```bash
# 1. Установить Poetry (если не установлен)
curl -sSL https://install.python-poetry.org | python3 -

# 2. Установить зависимости и настроить проект
poetry install && poetry run pre-commit install

# 3. Проверить, что все работает
poetry run pre-commit run --all-files
```

## Основные команды

```bash
# Активировать виртуальное окружение
poetry shell

# Запустить тесты
poetry run pytest tests/ -v

# Проверить код
poetry run ruff check src/
poetry run mypy src/

# Форматировать код
poetry run black src/ tests/
poetry run isort src/ tests/
```

## Makefile команды (Linux/macOS)

```bash
make help       # Показать все команды
make install    # Установить зависимости
make format     # Форматировать код
make lint       # Проверить код
make test       # Запустить тесты
make all        # Запустить все проверки
```

## Docker

```bash
# Собрать образ
docker build -t wine-quality-ml .

# Запустить контейнер
docker run -it wine-quality-ml
```

## Структура проекта

```
EPML-ITMO/
├── src/                # Исходный код
│   ├── data/          # Обработка данных
│   ├── features/      # Feature engineering
│   ├── models/        # Модели
│   └── visualization/ # Визуализация
├── tests/             # Тесты
├── data/              # Данные (raw, processed, external)
├── models/            # Обученные модели
├── notebooks/         # Jupyter notebooks
├── configs/           # Конфигурации
├── docs/              # Документация
└── reports/           # Отчеты и графики
```

## Важные файлы

- [README.md](README.md) - Основная документация
- [SETUP.md](SETUP.md) - Подробная инструкция по установке
- [REPORT.md](docs/REPORT.md) - Отчет о проделанной работе
- [pyproject.toml](pyproject.toml) - Конфигурация всего проекта
- [.pre-commit-config.yaml](.pre-commit-config.yaml) - Pre-commit hooks

## Проверка установки

После установки выполните:

```bash
# 1. Проверить версии
poetry --version
python --version

# 2. Запустить pre-commit
poetry run pre-commit run --all-files

# 3. Запустить тесты
poetry run pytest tests/ -v
```

Все должно работать без ошибок!

## Для менторов

Минимальный набор команд для проверки:

```bash
git clone <repo-url> && cd EPML-ITMO
poetry install && poetry run pre-commit install
poetry run pre-commit run --all-files
poetry run pytest tests/ -v
```

Ожидаемый результат: Все проверки (✓ Passed), все тесты (✓ 1 passed)
