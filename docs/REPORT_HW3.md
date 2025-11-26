# Отчёт по ДЗ 3: Трекинг экспериментов

**Студент:** ITMO EPML Student  
**Дата:** 26 ноября 2025  
**Инструмент:** MLflow (локальный backend)

---

## 🚀 Инструкция для ментора: Быстрая проверка

```bash
# 1. Клонировать и перейти в проект (если ещё не сделано)
git clone https://github.com/7Askar7/EPML-ITMO.git
cd EPML-ITMO

# 2. Установить зависимости
poetry install

# 3. Подтянуть данные
poetry run dvc pull

# 4. Запустить 16 экспериментов с разными алгоритмами
make experiments            # или: poetry run python -m src.models.run_experiments

# 5. Посмотреть результаты в MLflow UI
make mlflow-ui              # http://localhost:5000
# В UI: выбрать эксперимент "wine-quality", сравнить метрики
# Ctrl+C для остановки

# 6. Проверить артефакты экспериментов
ls reports/figures/experiments/
# Должны быть: cm_*.png (confusion matrices), experiments_summary.png, status.txt

# 7. Посмотреть лучшую модель
cat reports/figures/experiments/status.txt
cat reports/figures/experiments/experiments_top10.csv
```

**Ожидаемый результат:**
- ✅ 16 экспериментов залогированы в MLflow (LogReg, RF, GBoost, SVC, KNN, AdaBoost)
- ✅ Каждый эксперимент: accuracy, f1_weighted, параметры, confusion matrix
- ✅ MLflow UI показывает все эксперименты для сравнения
- ✅ `status.txt` содержит лучшую модель (rf_150_depth12, accuracy ~0.68)
- ✅ `experiments_summary.png` — bar chart топ-10 моделей

---

## Настройка MLflow
- **Tracking URI:** `sqlite:///mlflow.db`
- **Артефакты:** `file:./mlruns`
- **Эксперимент:** `wine-quality`
- **Теги:** `data_version_md5` из dvc.lock, `model_name`, `pipeline`

## Проведённые эксперименты (16 конфигураций)

| Алгоритм | Конфигурации |
|----------|--------------|
| LogisticRegression | C=0.5, C=1.0, C=2.0 |
| RandomForest | depth=8, 10, 12, 14 |
| GradientBoosting | lr=0.05, lr=0.1 |
| SVC | linear, rbf (2 варианта) |
| KNN | k=5, k=10 |
| AdaBoost | n=50, n=100 |

**Логируется для каждого эксперимента:**
- Метрики: accuracy, f1_weighted
- Параметры: все гиперпараметры модели
- Артефакты: confusion matrix (PNG), classification report (TXT), модель (MLflow sklearn)
- Теги: model_name, data_version_md5, pipeline

## Интеграция в код

### Декоратор `@log_experiment`
```python
# src/models/experiment_tracker.py
@log_experiment(run_name="rf_100", tags={"model": "rf"})
def train_and_log():
    model.fit(X, y)
    return {"params": {...}, "metrics": {"accuracy": 0.68}, "artifacts": [...]}
```

### Контекстный менеджер `mlflow_run`
```python
with mlflow_run(run_name="experiment_1"):
    mlflow.log_params({...})
    mlflow.log_metrics({...})
```

### Утилиты
- `get_data_version()` — читает md5 из dvc.lock
- `configure_mlflow()` — настраивает tracking URI и эксперимент
- `ensure_experiment()` — создаёт эксперимент если не существует

## Скриншоты
- `reports/figures/experiments/experiments_summary.png` — топ-10 по accuracy
- `reports/figures/experiments/cm_*.png` — confusion matrix для каждого эксперимента
- `reports/figures/mlflow_run.png` — пример MLflow run

## Итог
✅ **Выполненные требования:**
- MLflow настроен (локальный SQLite + артефакты)
- 16 экспериментов с разными алгоритмами
- Логирование метрик, параметров, артефактов
- Система сравнения (MLflow UI + experiments_summary.png)
- Декораторы и контекстные менеджеры для автологирования
- Утилиты для работы с экспериментами
- Отчёт со скриншотами
