.PHONY: help test test-verbose clean lint format install install-dev

help:
	@echo "Available commands:"
	@echo "  make help         - Show this help message"
	@echo "  make test         - Run tests"
	@echo "  make test-verbose - Run tests with verbose output"
	@echo "  make clean        - Remove Python cache files"
	@echo "  make lint         - Run linting checks"
	@echo "  make format       - Format code"
	@echo "  make install      - Install production dependencies"
	@echo "  make install-dev  - Install development dependencies"

test:
	PYTHONPATH=. pytest

test-verbose:
	PYTHONPATH=. pytest -v

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "*.egg" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +

lint:
	uv run pyright .
	uv run ruff check .

format:
	uv run ruff format .
	uv run ruff check --fix .

install:
	uv sync --no-default-groups

install-dev:
	uv sync
