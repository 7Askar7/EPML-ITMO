# Отчёт по ДЗ 2: Версионирование данных и моделей

**Студент:** ITMO EPML Student
**Дата:** 26 ноября 2025
**Выбор инструментов:** DVC (данные), MLflow (модели)

---

## 🚀 Инструкция для ментора: Быстрая проверка

```bash
# 1. Клонировать и перейти в проект (если ещё не сделано)
git clone https://github.com/7Askar7/EPML-ITMO.git
cd EPML-ITMO

# 2. Установить зависимости
poetry install

# 3. Подтянуть данные из DVC (remote уже в репозитории)
poetry run dvc pull

# 4. Проверить DVC пайплайн (split данных)
poetry run dvc repro        # пересчитает если что-то изменилось
poetry run dvc status       # должен показать "Data and calculation are up to date"

# 5. Обучить модель с логированием в MLflow
make train                  # или: poetry run python -m src.models.train_model

# 6. Посмотреть MLflow UI (метрики, модели, артефакты)
make mlflow-ui              # откроется на http://localhost:5000
# Ctrl+C для остановки

# 7. Проверить артефакты
ls data/processed/          # train.csv, test.csv
ls models/                  # wine_quality_model.pkl
ls mlruns/                  # MLflow артефакты
```

**Ожидаемый результат:**
- ✅ DVC pull: данные скачиваются из локального remote
- ✅ DVC repro: пайплайн выполняется (или "up to date")
- ✅ MLflow: модель залогирована, метрики видны в UI
- ✅ Model Registry: модель `wine-quality-rf` зарегистрирована

---

## Что настроено

### DVC для данных
- Локальный remote: `data/dvc_remote` (уже содержит кеш датасета)
- Пайплайн `dvc.yaml`:
  - Стадия `split`: `python -m src.data.make_dataset`
  - Зависимости: `data/raw/winequality-red.csv`, `src/data/make_dataset.py`
  - Выходы: `data/processed/train.csv`, `data/processed/test.csv`
- Автоматическое версионирование: `dvc.lock` фиксирует хеши всех файлов

### MLflow для моделей
- Backend: `sqlite:///mlflow.db`
- Артефакты: `./mlruns`
- Эксперимент: `wine-quality`
- Логируется:
  - Гиперпараметры (n_estimators, max_depth, random_state)
  - Метрика accuracy
  - Classification report (текст)
  - Тег `data_version_md5` из dvc.lock
  - Модель в Model Registry (`wine-quality-rf`)

### Команды Makefile
| Команда | Что делает |
|---------|------------|
| `make data` | `dvc repro` + `dvc push` |
| `make train` | Обучение + логирование в MLflow |
| `make mlflow-ui` | Запуск MLflow UI на порту 5000 |

## Скриншоты результатов
- `reports/figures/dvc_pipeline.png` — схема DVC-пайплайна
- `reports/figures/mlflow_run.png` — MLflow run с метрикой и моделью в Registry

## Итог
✅ **Выполненные требования:**
- DVC установлен и настроен с локальным remote
- Пайплайн версионирования данных (dvc.yaml + dvc.lock)
- MLflow tracking + Model Registry
- Метаданные моделей (теги, параметры, метрики)
- Инструкции по воспроизведению
- Docker контейнер (из ДЗ1)
- Зависимости зафиксированы в poetry.lock
