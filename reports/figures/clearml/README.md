# ClearML Screenshots (ДЗ 5)

Реальные скриншоты из ClearML Web UI (http://localhost:8090).

## Содержимое

| Файл | Описание |
|------|----------|
| `experiments_list.png` | Список экспериментов в проекте wine-quality-clearml |
| `pipeline_execution.png` | Детали выполнения pipeline (source code, commit, execution) |
| `experiment_metrics.png` | Метрики эксперимента (accuracy, f1_weighted) |
| `artifacts.png` | Артефакты pipeline (dashboard, summary, status) |
| `model_registry.png` | Model Registry с 4 моделями (ScikitLearn) |
| `docker_containers.png` | Docker containers (7 сервисов running) |

## Воспроизведение

```bash
# 1. Поднять ClearML Server
make clearml-server-up

# 2. Запустить pipeline
make clearml-pipeline

# 3. Открыть UI
# http://localhost:8090 (admin/admin)
```

## Порты

- API: http://localhost:8008
- Web UI: http://localhost:8090
- File Server: http://localhost:8091
