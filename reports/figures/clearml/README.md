# ClearML Screenshots для отчёта ДЗ 5

## Рекомендуемые скриншоты для добавления в отчёт

Откройте ClearML Web UI: http://localhost:8090 (логин: admin, пароль: admin)

### 1. experiments_list.png
**Где:** Projects → wine-quality-clearml → Experiments
**Что показать:** Список всех экспериментов в проекте
- Pipeline task: wine-quality-pipeline
- Leaderboard task: experiments-leaderboard
- Experiment tasks: exp::baseline-lr, exp::optimized-lr, etc.

### 2. pipeline_task.png
**Где:** Клик на task `wine-quality-pipeline` (ID: 9fb037471b8f4b9c850db0074c0875b6)
**Что показать:** Детали pipeline task
- Status: Completed
- Execution time
- Console logs
- Configuration (data_version, orchestrator, source, variant)

### 3. metrics_comparison.png
**Где:** Compare → Select multiple experiment tasks → Scalars
**Что показать:** Сравнение метрик между экспериментами
- Accuracy
- Precision
- Recall
- F1-score
Графики должны показывать разницу между моделями

### 4. confusion_matrix.png
**Где:** Любой experiment task → Plots → Confusion Matrix
**Что показать:** Confusion matrix для одного из экспериментов
- Четкая визуализация матрицы ошибок
- Названия классов качества вина

### 5. model_registry.png
**Где:** Models → wine-quality-registry
**Что показать:** Список моделей в реестре
- Версии моделей для разных экспериментов
- Метаданные (tags, data_version)
- Model artifacts

### 6. clearml_server.png (опционально)
**Где:** Docker Desktop или терминал
**Что показать:** Все 7 работающих контейнеров ClearML
```bash
docker ps --filter "name=clearml"
```

### 7. clearml_dashboard.png (опционально)
**Где:** Projects → wine-quality-clearml → Reports
**Что показать:** Сводный дашборд с результатами экспериментов
- Таблица лидерборда
- Сводная статистика

---

## Как сделать скриншоты

### Вариант 1: Windows Snipping Tool
1. Нажмите `Win + Shift + S`
2. Выберите область для скриншота
3. Сохраните в этой папке с соответствующим именем

### Вариант 2: Браузерные DevTools (для чистых скриншотов)
1. F12 → Toggle device toolbar (Ctrl+Shift+M)
2. Screenshot → Capture full size screenshot
3. Сохраните в этой папке

### Вариант 3: ShareX (рекомендуется)
1. Установите ShareX (бесплатно)
2. Настройте автоматическое сохранение в эту папку
3. Используйте `Ctrl + Print Screen`

---

## После добавления скриншотов

Убедитесь, что в отчёте [docs/REPORT_HW5.md](../../../docs/REPORT_HW5.md) ссылки на скриншоты корректны:

```markdown
![Experiments List](../reports/figures/clearml/experiments_list.png)
![Pipeline Task](../reports/figures/clearml/pipeline_task.png)
...
```

Проверьте отображение в GitHub или локально через Markdown preview.
