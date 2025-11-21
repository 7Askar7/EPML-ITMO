# Contributing to Wine Quality ML Project

Спасибо за интерес к улучшению проекта!

## Как внести вклад

### 1. Подготовка окружения

```bash
# Форк и клонирование репозитория
git clone <your-fork-url>
cd EPML-ITMO

# Установка зависимостей
poetry install
poetry run pre-commit install
```

### 2. Создание ветки

```bash
# Создать новую ветку для своих изменений
git checkout -b feature/your-feature-name
# или
git checkout -b fix/your-bug-fix
```

### 3. Разработка

#### Код должен соответствовать стандартам:

- Использовать type hints для всех функций
- Писать docstrings в Google стиле
- Следовать PEP 8 (автоматически через Black и Ruff)
- Покрывать код тестами

#### Пример функции с правильным оформлением:

```python
def process_data(
    df: pd.DataFrame,
    target_column: str = "quality",
) -> tuple[pd.DataFrame, pd.Series]:
    """Process input dataframe for model training.

    Args:
        df: Input dataframe with features and target
        target_column: Name of the target column

    Returns:
        Tuple of (features_df, target_series)

    Raises:
        KeyError: If target_column not found in dataframe
    """
    if target_column not in df.columns:
        raise KeyError(f"Column {target_column} not found")

    X = df.drop(columns=[target_column])
    y = df[target_column]
    return X, y
```

### 4. Проверка кода

```bash
# Форматирование
make format

# Линтинг
make lint

# Тесты
make test

# Все проверки
make all
```

Или по отдельности:

```bash
poetry run black src/ tests/
poetry run isort src/ tests/
poetry run ruff check src/ tests/ --fix
poetry run mypy src/
poetry run pytest tests/ -v --cov=src
```

### 5. Написание тестов

Все новые функции должны иметь тесты:

```python
# tests/test_your_module.py
import pytest
from src.your_module import your_function


def test_your_function() -> None:
    """Test your_function with valid input."""
    result = your_function(input_data)
    assert result == expected_output


def test_your_function_error() -> None:
    """Test your_function raises error on invalid input."""
    with pytest.raises(ValueError):
        your_function(invalid_input)
```

### 6. Коммит изменений

```bash
# Добавить файлы
git add .

# Коммит (pre-commit hooks запустятся автоматически)
git commit -m "feat: add new feature description"
```

#### Формат коммит-сообщений:

- `feat:` - новая функциональность
- `fix:` - исправление бага
- `docs:` - изменения в документации
- `style:` - форматирование, без изменения кода
- `refactor:` - рефакторинг кода
- `test:` - добавление тестов
- `chore:` - обновление зависимостей, конфигураций

### 7. Push и Pull Request

```bash
# Push в свой форк
git push origin feature/your-feature-name

# Создать Pull Request на GitHub
```

## Code Review Process

1. Все PR проходят автоматические проверки (CI/CD)
2. Код ревьюится минимум одним мейнтейнером
3. Все комментарии должны быть разрешены
4. После одобрения PR мёрджится в main

## Checklist перед созданием PR

- [ ] Код отформатирован (Black, isort)
- [ ] Линтеры не выдают ошибок (Ruff, MyPy)
- [ ] Все тесты проходят
- [ ] Добавлены новые тесты для новой функциональности
- [ ] Обновлена документация (если нужно)
- [ ] Коммит-сообщения информативные
- [ ] Pre-commit hooks установлены и проходят

## Вопросы?

Если возникли вопросы:
1. Проверьте [документацию](README.md)
2. Посмотрите существующие [issues](https://github.com/your-repo/issues)
3. Создайте новый issue с вопросом

Спасибо за вклад в проект!
