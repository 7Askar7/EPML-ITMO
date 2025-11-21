.PHONY: install format lint test clean docker-build docker-run help

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

setup: install ## Полная настройка проекта
	@echo "$(GREEN)Проект настроен и готов к работе!$(RESET)"
	@echo "$(YELLOW)Запустите 'make help' для списка команд$(RESET)"

all: format lint test ## Запустить все проверки
	@echo "$(GREEN)✓ Все проверки пройдены$(RESET)"
