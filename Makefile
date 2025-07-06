.PHONY: all help install format lint test build run local clean clean-venv

all: help

help:
	@echo "Usage: make <target>"
	@echo "Targets:"
	@echo "  install       - Install dependencies with Poetry"
	@echo "  format        - Run code formatter using black"
	@echo "  lint          - Run pylint linter"
	@echo "  test          - Run tests and coverage using pytest"
	@echo "  build         - Build docker container"
	@echo "  run           - Run docker container"
	@echo "  clean         - Clean up unnecessary files"
	@echo "  clean-venv    - Remove Poetry virtual environment"

# Use Poetry for dependency management
install:
	poetry lock && poetry install

# Run locally
local:
	poetry run uvicorn src.app:app --host 0.0.0.0 --port 8000 --reload

# Run tests and coverage using pytest
test:
	dotenv -f src/.env run -- poetry run coverage run -m pytest -v
	dotenv -f src/.env run -- poetry run coverage report -m

# Run code formatter using black
format:
	poetry run black .

# Run linter using pylint
lint:
	poetry run pylint --recursive=y .

# Build docker container
build:
	docker build -t techcorp .

# Run docker container
run:
	docker run -p 8080:8080 techcorp

# Clean up unnecessary files
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} +
	docker system prune -f

# Remove Poetry virtual environment
clean-venv:
	poetry env remove $$(poetry env list --full-path | head -n 1) 