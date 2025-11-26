# Отчёт по ДЗ 4: Автоматизация ML пайплайнов

**Оркестрация:** DVC Pipelines
**Конфигурации:** Hydra

## Что требовалось и что сделано
1) **Настройка оркестрации (4 балла)**
   - DVC-пайплайн `dvc.yaml` со стадиями: `split` → `train` → `experiments`.
   - Зависимости и кэш: данные, код и конфиги фиксируются в `dvc.lock`; `dvc repro -j` поддерживает параллель.
   - Outputs: `data/processed/*`, `models/wine_quality_model.pkl`, артефакты экспериментов в `reports/figures/experiments/*`.

2) **Конфигурации (3 балла)**
   - Hydra: базовый конфиг `configs/hydra/config.yaml` + варианты `configs/hydra/algorithms/{full,quick}.yaml`.
   - Валидация: в `src/pipelines/run_hydra_pipeline.py` проверка уникальных имён и количества экспериментов (>=15).
   - Композиция: CLI-переключение `algorithms=<variant>`; базовые теги/параметры переопределяются через Hydra.

3) **Интеграция и тестирование (2 балла)**
   - Скрипт `src/pipelines/run_hydra_pipeline.py` вызывает `run_batch` (MLflow + эксперименты), теги включают версию данных из DVC.
   - Мониторинг/артефакты: `experiments_summary.png`, `experiments_top10.csv`, `status.txt`, `val_split_info.txt`; MLflow UI для сравнения.
   - Воспроизводимость: Poetry-зависимости, DVC-remote, Makefile цели `make pipeline`, `make experiments`, тесты `make test`.

4) **Отчёт (1 балл)**
   - Текущий файл + README раздел «Оркестрация (ДЗ 4)» с командами и путями артефактов. Скриншоты/артефакты в `reports/figures/experiments/`.

## Скриншоты/артефакты
- `reports/figures/dvc_pipeline.png` — схема стадий.
- `reports/figures/experiments/experiments_summary.png` — топ-10 экспериментов.
- Confusion matrices `reports/figures/experiments/cm_*.png`, отчёты `classification_report_*.txt`.

## Команды для проверки
```bash
poetry install
poetry run dvc pull
make pipeline          # split -> train -> experiments + dvc push
make mlflow-ui         # UI на 5000 порту
```
