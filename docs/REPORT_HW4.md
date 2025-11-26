# Отчёт по ДЗ 4: Автоматизация ML пайплайнов

**Студент:** ITMO EPML Student  
**Дата:** 26 ноября 2025  
**Оркестрация:** DVC Pipelines  
**Конфигурации:** Hydra

---

## 🚀 Инструкция для ментора: Быстрая проверка

```bash
# 1. Клонировать и перейти в проект (если ещё не сделано)
git clone https://github.com/7Askar7/EPML-ITMO.git
cd EPML-ITMO

# 2. Установить зависимости
poetry install

# 3. Подтянуть данные из DVC
poetry run dvc pull

# 4. Запустить ПОЛНЫЙ пайплайн (split → train → experiments)
make pipeline               # или: poetry run dvc repro

# 5. Проверить граф зависимостей DVC
poetry run dvc dag          # покажет: split → train, split → experiments

# 6. Проверить Hydra конфигурации
cat configs/hydra/config.yaml
cat configs/hydra/algorithms/full.yaml    # 16 экспериментов
cat configs/hydra/algorithms/quick.yaml   # 4 эксперимента (быстрый тест)

# 7. Запустить с альтернативной конфигурацией (quick)
poetry run python -m src.pipelines.run_hydra_pipeline algorithms=quick

# 8. Проверить кэширование DVC (повторный запуск — всё из кэша)
poetry run dvc repro        # должен показать "Stage ... didn't change, skipping"

# 9. Посмотреть артефакты
ls reports/figures/experiments/
cat reports/figures/experiments/status.txt         # лучшая модель
cat reports/figures/experiments/experiments_top10.csv

# 10. MLflow UI для сравнения
make mlflow-ui              # http://localhost:5000
```

**Ожидаемый результат:**
- ✅ DVC пайплайн: 3 стадии (split, train, experiments)
- ✅ Кэширование: повторный `dvc repro` пропускает неизменённые стадии
- ✅ Hydra: `algorithms=full` (16 эксп.) и `algorithms=quick` (4 эксп.)
- ✅ Валидация: минимум 15 экспериментов, уникальные имена
- ✅ Мониторинг: status.txt, experiments_top10.csv, experiments_summary.png

---

## Оркестрация (DVC Pipelines)

### Граф пайплайна (dvc.yaml)
```
data/raw/winequality-red.csv
           │
           ▼
    ┌─────────────┐
    │   SPLIT     │  poetry run python -m src.data.make_dataset
    └─────────────┘
           │
     ┌─────┴─────┐
     ▼           ▼
 train.csv   test.csv
     │           │
     ▼           ▼
┌─────────┐  ┌──────────────┐
│  TRAIN  │  │ EXPERIMENTS  │  poetry run python -m src.pipelines.run_hydra_pipeline
└─────────┘  └──────────────┘
     │              │
     ▼              ▼
 model.pkl    summary.png, status.txt, top10.csv
```

### Стадии
| Стадия | Команда | Выходы |
|--------|---------|--------|
| `split` | `python -m src.data.make_dataset` | train.csv, test.csv |
| `train` | `python -m src.models.train_model` | model.pkl + MLflow |
| `experiments` | `python -m src.pipelines.run_hydra_pipeline` | 16 MLflow runs + артефакты |

### Кэширование
```bash
# Первый запуск — всё выполняется
$ dvc repro
Running stage 'split'...
Running stage 'train'...
Running stage 'experiments'...

# Второй запуск — из кэша
$ dvc repro
Stage 'split' didn't change, skipping
Stage 'train' didn't change, skipping
Stage 'experiments' didn't change, skipping
```

## Конфигурации (Hydra)

### Структура конфигов
```
configs/hydra/
├── config.yaml              # Базовый конфиг (defaults, tracking_uri, теги)
└── algorithms/
    ├── full.yaml            # 16 экспериментов (для сдачи)
    └── quick.yaml           # 4 эксперимента (для быстрого теста)
```

### Базовый конфиг (config.yaml)
```yaml
defaults:
  - _self_
  - algorithms: full         # По умолчанию full (16 экспериментов)

experiment_name: wine-quality
tracking_uri: sqlite:///mlflow.db
artifact_location: file:./mlruns
base_tags:
  orchestrator: dvc
  pipeline: hydra_experiments
```

### Композиция конфигураций
```bash
# Полный набор (16 экспериментов) — по умолчанию
poetry run python -m src.pipelines.run_hydra_pipeline

# Быстрый набор (4 эксперимента) — для тестирования
poetry run python -m src.pipelines.run_hydra_pipeline algorithms=quick

# Переопределение параметра через CLI
poetry run python -m src.pipelines.run_hydra_pipeline algorithms.experiments[0].params.C=0.1
```

### Валидация
В `src/pipelines/run_hydra_pipeline.py`:
- Проверка уникальности имён экспериментов
- Проверка минимум 15 экспериментов (для full)

## Мониторинг

### Автоматические артефакты
| Файл | Описание |
|------|----------|
| `status.txt` | Лучшая модель (имя, accuracy, f1) |
| `experiments_top10.csv` | Топ-10 экспериментов |
| `experiments_summary.png` | Bar chart accuracy |
| `cm_*.png` | Confusion matrix для каждого эксперимента |

### MLflow UI
```bash
make mlflow-ui              # http://localhost:5000
```
- Фильтрация по `tags.model_name`, `metrics.accuracy`
- Сравнение экспериментов
- Просмотр артефактов

## Скриншоты
- `reports/figures/dvc_pipeline.png` — граф DVC пайплайна
- `reports/figures/experiments/experiments_summary.png` — топ-10 моделей
- `reports/figures/experiments/cm_*.png` — confusion matrices

## Итог
✅ **Выполненные требования:**
- DVC Pipelines: 3 стадии с зависимостями и кэшированием
- Hydra: композиция конфигураций (full/quick), CLI overrides
- Валидация конфигураций (уникальность, минимум 15)
- Мониторинг: status.txt, top10.csv, summary.png
- Интеграция: DVC → Hydra → MLflow
- Воспроизводимость: `make pipeline` для полного пайплайна
