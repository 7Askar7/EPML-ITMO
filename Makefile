.PHONY: install format lint test data train experiments pipeline mlflow-ui clean docker-build docker-run help clearml-server-up clearml-server-down clearml-pipeline clearml-experiments docs-serve docs-build docs-deploy

# Цвета для вывода
GREEN  := \033[0;32m
YELLOW := \033[0;33m
RESET  := \033[0m

help: ## Показать это сообщение помощи
	@echo "$(GREEN)Доступные команды:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-15s$(RESET) %s\n", $$1, $$2}'

install: ## Установить все зависимости
	@echo "$(GREEN)Установка зависимостей...$(RESET)"
	poetry install
	poetry run pre-commit install
	@echo "$(GREEN)✓ Зависимости установлены$(RESET)"

format: ## Форматировать код (Black, isort)
	@echo "$(GREEN)Форматирование кода...$(RESET)"
	poetry run black src/ tests/
	poetry run isort src/ tests/
	@echo "$(GREEN)✓ Код отформатирован$(RESET)"

lint: ## Проверить код (Ruff, MyPy, Bandit)
	@echo "$(GREEN)Проверка кода...$(RESET)"
	poetry run ruff check src/ tests/
	poetry run mypy src/
	poetry run bandit -r src/
	@echo "$(GREEN)✓ Проверка завершена$(RESET)"

test: ## Запустить тесты
	@echo "$(GREEN)Запуск тестов...$(RESET)"
	poetry run pytest tests/ -v --cov=src --cov-report=html --cov-report=term-missing
	@echo "$(GREEN)✓ Тесты выполнены$(RESET)"

data: ## Обновить данные через DVC (repro + push)
	@echo "$(GREEN)Пересчитываем пайплайн DVC...$(RESET)"
	poetry run dvc repro
	poetry run dvc push
	@echo "$(GREEN)✓ Данные обновлены и отправлены в remote$(RESET)"

train: ## Обучить модель с MLflow логированием
	@echo "$(GREEN)Обучение модели...$(RESET)"
	poetry run python -m src.models.train_model
	@echo "$(GREEN)✓ Обучение завершено, артефакты в mlruns$(RESET)"

pipeline: ## Полный DVC пайплайн (split -> train -> experiments) + push
	@echo "$(GREEN)Запуск полного DVC пайплайна...$(RESET)"
	poetry run dvc repro
	poetry run dvc push
	@echo "$(GREEN)✓ Пайплайн выполнен и отправлен в remote$(RESET)"

mlflow-ui: ## Запустить MLflow UI (порт 5000)
	@echo "$(GREEN)Стартуем MLflow UI на http://localhost:5000$(RESET)"
	poetry run mlflow ui --backend-store-uri sqlite:///mlflow.db --default-artifact-root file:./mlruns --host 0.0.0.0 --port 5000

experiments: ## Запустить пакет из 15+ экспериментов (логирование в MLflow)
	@echo "$(GREEN)Запускаем серию экспериментов...$(RESET)"
	poetry run python -m src.pipelines.run_hydra_pipeline algorithms=full
	@echo "$(GREEN)✓ Эксперименты залогированы в MLflow и сохранены артефакты$(RESET)"

pre-commit: ## Запустить pre-commit на всех файлах
	@echo "$(GREEN)Запуск pre-commit hooks...$(RESET)"
	poetry run pre-commit run --all-files
	@echo "$(GREEN)✓ Pre-commit завершен$(RESET)"

clean: ## Удалить временные файлы
	@echo "$(GREEN)Очистка временных файлов...$(RESET)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov/ .coverage
	@echo "$(GREEN)✓ Очистка завершена$(RESET)"

docker-build: ## Собрать Docker образ
	@echo "$(GREEN)Сборка Docker образа...$(RESET)"
	docker build -t wine-quality-ml:latest .
	@echo "$(GREEN)✓ Образ собран$(RESET)"

docker-run: ## Запустить Docker контейнер
	@echo "$(GREEN)Запуск Docker контейнера...$(RESET)"
	docker run -it --rm \
		-v $(PWD)/data:/app/data \
		-v $(PWD)/models:/app/models \
	wine-quality-ml:latest
	@echo "$(GREEN)✓ Контейнер завершил работу$(RESET)"

clearml-server-up: ## Поднять ClearML Server (docker-compose)
	@echo "$(GREEN)Поднимаем ClearML Server...$(RESET)"
	docker compose --env-file .env.clearml -f infra/clearml/docker-compose.yml up -d
	@echo "$(GREEN)✓ ClearML доступен на http://localhost:8080$(RESET)"

clearml-server-down: ## Остановить ClearML Server
	@echo "$(GREEN)Останавливаем ClearML Server...$(RESET)"
	docker compose --env-file .env.clearml -f infra/clearml/docker-compose.yml down
	@echo "$(GREEN)✓ ClearML остановлен$(RESET)"

clearml-pipeline: ## Запустить ClearML пайплайн (вариант quick)
	@echo "$(GREEN)Запуск ClearML пайплайна (quick)...$(RESET)"
	poetry run python -m src.pipelines.clearml_pipeline --variant quick
	@echo "$(GREEN)✓ Пайплайн завершён, результаты в ClearML UI$(RESET)"

clearml-experiments: ## Запустить ClearML пайплайн (полный набор экспериментов)
	@echo "$(GREEN)Запуск ClearML пайплайна (full)...$(RESET)"
	poetry run python -m src.pipelines.clearml_pipeline --variant full
	@echo "$(GREEN)✓ Эксперименты залогированы в ClearML UI$(RESET)"

clearml-cleanup: ## Очистить старые данные Elasticsearch (30 дней)
	@echo "$(GREEN)Очистка Elasticsearch...$(RESET)"
	@powershell -ExecutionPolicy Bypass -File infra/clearml/cleanup-elastic.ps1
	@echo "$(GREEN)✓ Очистка завершена$(RESET)"

clearml-disk-usage: ## Показать использование диска ClearML компонентами
	@echo "$(GREEN)Использование диска ClearML:$(RESET)"
	@du -sh infra/clearml/data/mongo 2>/dev/null || echo "MongoDB: N/A"
	@du -sh infra/clearml/data/elastic 2>/dev/null || echo "Elasticsearch: N/A"
	@du -sh infra/clearml/data/redis 2>/dev/null || echo "Redis: N/A"
	@du -sh infra/clearml/files 2>/dev/null || echo "Files: N/A"
	@echo "$(YELLOW)Для детальной информации: docker system df$(RESET)"

setup: install ## Полная настройка проекта
	@echo "$(GREEN)Проект настроен и готов к работе!$(RESET)"
	@echo "$(YELLOW)Запустите 'make help' для списка команд$(RESET)"

all: format lint test ## Запустить все проверки
	@echo "$(GREEN)✓ Все проверки пройдены$(RESET)"

# ============ Documentation ============

docs-serve: ## Запустить локальный сервер документации
	@echo "$(GREEN)Запуск MkDocs сервера на http://localhost:8000$(RESET)"
	poetry run mkdocs serve

docs-build: ## Собрать документацию
	@echo "$(GREEN)Сборка документации...$(RESET)"
	poetry run mkdocs build --strict
	@echo "$(GREEN)✓ Документация собрана в site/$(RESET)"

docs-deploy: ## Опубликовать документацию на GitHub Pages
	@echo "$(GREEN)Публикация документации на GitHub Pages...$(RESET)"
	poetry run mkdocs gh-deploy --force
	@echo "$(GREEN)✓ Документация опубликована на https://7Askar7.github.io/EPML-ITMO/$(RESET)"
