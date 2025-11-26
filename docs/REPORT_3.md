# Отчёт по ДЗ 3: Трекинг экспериментов

**Инструмент:** MLflow (локальный backend)
**Контроль конфигураций экспериментов:** Hydra + Python-утилиты

## Что требовалось и что сделано
1) **Настройка инструмента трекинга**
   - MLflow с backend `sqlite:///mlflow.db` и артефактами `./mlruns`; эксперимент `wine-quality`.
   - Аутентификация не нужна (локально), UI запускается `make mlflow-ui`.

2) **15+ экспериментов**
   - Скрипт `src/models/run_experiments.py` запускает 16 конфигураций (LogReg, RF, GBoost, SVC, KNN, AdaBoost) с разными гиперпараметрами.
   - Логируются метрики (accuracy, f1_weighted), параметры, отчёты, confusion matrix, модели (sklearn flavor).
   - Сравнение: `reports/figures/experiments/experiments_summary.png`, `experiments_top10.csv`, фильтры в MLflow UI.

3) **Интеграция в код**
   - Утилита `src/models/experiment_tracker.py`: декоратор `log_experiment`, контекст `mlflow_run`, тег `data_version_md5` из `dvc.lock`.
   - Основной тренинг `src/models/train_model.py` использует эти утилиты, регистрирует модель `wine-quality-rf`.

4) **Отчёт**
   - Этот файл + скриншоты/артефакты: `reports/figures/experiments/experiments_summary.png`, матрицы ошибок `cm_*.png`, отчёты `classification_report_*.txt`.

## Скриншоты/артефакты
- `reports/figures/experiments/experiments_summary.png` — топ-эксперименты.
- Примеры confusion matrix: `reports/figures/experiments/cm_rf_150_depth12.png` и др.

## Быстрые команды
```bash
poetry install
poetry run dvc pull
make experiments          # 15+ MLflow запусков
make mlflow-ui            # просмотр/сравнение
```
