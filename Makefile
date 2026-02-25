.PHONY: init up down restart logs clean test lint format check

VENV = .venv
PYTHON = $(VENV)/bin/python
UV = uv

init:
	$(UV) venv $(VENV)
	$(UV) sync --all-extras --dev --frozen
	$(VENV)/bin/pre-commit install

up:
	docker compose up -d

down:
	docker compose down

build:
	docker compose build

restart:
	docker compose restart

logs:
	docker compose logs -f

test:
	$(VENV)/bin/pytest --cov=src --cov-branch --cov-report=term-missing

lint:
	$(VENV)/bin/ruff check .
	$(VENV)/bin/ruff format --check .
	$(VENV)/bin/mypy . --explicit-package-bases

check: lint test

format:
	$(VENV)/bin/ruff format .
	$(VENV)/bin/ruff check --fix .

clean:
	rm -rf .venv .pytest_cache .mypy_cache .ruff_cache .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} +
	docker image prune -f
