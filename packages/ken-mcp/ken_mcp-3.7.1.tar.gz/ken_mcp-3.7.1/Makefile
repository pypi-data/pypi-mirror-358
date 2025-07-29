.PHONY: help test install clean lint format

help:
	@echo "Available commands:"
	@echo "  make install    - Install KEN-MCP and dependencies"
	@echo "  make test       - Run test suite with coverage"
	@echo "  make lint       - Run linting checks"
	@echo "  make format     - Format code with black"
	@echo "  make clean      - Clean generated files"

install:
	pip install -e .
	pip install -e .[test]

test:
	python -m pytest -v --cov=ken_mcp --cov-report=term-missing --cov-report=html tests/

test-fast:
	python -m pytest -v tests/

lint:
	python -m pylint ken_mcp/
	python -m flake8 ken_mcp/

format:
	python -m black ken_mcp/ tests/

clean:
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf dist/
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete