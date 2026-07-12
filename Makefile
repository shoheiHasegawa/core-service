.PHONY: setup test lint validate check-all

setup:
	@echo "Setting up uv environment..."
	uv sync

test:
	@echo "Running unit tests with coverage..."
	PYTHONPATH=src uv run pytest tests/ --cov=src --cov-report=term-missing --cov-fail-under=90

lint:
	@echo "Running static analysis (Ruff)..."
	uv run ruff check src tests scripts
	uv run ruff format src tests scripts

validate:
	@echo "Running Architecture & SDD Validator..."
	uv run python scripts/validate_sdd.py

check-all: test lint validate
	@echo "All checks passed! Ready for harvest."
