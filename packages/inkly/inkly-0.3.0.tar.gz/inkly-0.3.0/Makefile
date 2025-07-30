.PHONY: help install test lint format type-check build clean all dev-install
.DEFAULT_GOAL := help

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)Inkly - OpenAPI Code Generator$(NC)"
	@echo ""
	@echo "$(GREEN)Available commands:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-15s$(NC) %s\n", $$1, $$2}'

install: ## Install the package in development mode
	@echo "$(BLUE)Installing package in development mode...$(NC)"
	pip install -e .

dev-install: ## Install development dependencies
	@echo "$(BLUE)Installing development dependencies...$(NC)"
	pip install -e ".[dev]"

test: ## Run tests with pytest
	@echo "$(BLUE)Running tests...$(NC)"
	python -m pytest tests/ -v --cov=inkly --cov-report=html --cov-report=xml --cov-report=term-missing

test-fast: ## Run tests without coverage
	@echo "$(BLUE)Running fast tests...$(NC)"
	python -m pytest tests/ -v

lint: ## Run ruff linter
	@echo "$(BLUE)Running ruff linter...$(NC)"
	python -m ruff check inkly/ tests/

lint-fix: ## Run ruff linter with auto-fix
	@echo "$(BLUE)Running ruff linter with auto-fix...$(NC)"
	python -m ruff check inkly/ tests/ --fix

format: ## Format code with ruff
	@echo "$(BLUE)Formatting code with ruff...$(NC)"
	python -m ruff format inkly/ tests/

format-check: ## Check code formatting
	@echo "$(BLUE)Checking code formatting...$(NC)"
	python -m ruff format inkly/ tests/ --check

type-check: ## Run pyright type checker
	@echo "$(BLUE)Running pyright type checker...$(NC)"
	python -m pyright inkly/ tests/

build: ## Build package
	@echo "$(BLUE)Building package...$(NC)"
	python -m build

build-clean: clean build ## Clean and build package

clean: ## Clean build artifacts and cache
	@echo "$(BLUE)Cleaning build artifacts...$(NC)"
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytype/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

check: ## Run all checks (lint, format-check, type-check)
	@echo "$(BLUE)Running all checks...$(NC)"
	$(MAKE) lint
	$(MAKE) format-check  
	$(MAKE) type-check

test-all: ## Run all tests and checks
	@echo "$(BLUE)Running all tests and checks...$(NC)"
	$(MAKE) check
	$(MAKE) test

ci: ## Run CI pipeline (all checks and tests)
	@echo "$(BLUE)Running CI pipeline...$(NC)"
	$(MAKE) dev-install
	$(MAKE) test-all

# Development workflow
dev: ## Setup development environment
	@echo "$(BLUE)Setting up development environment...$(NC)"
	$(MAKE) dev-install
	@echo "$(GREEN)Development environment ready!$(NC)"
	@echo "Run '$(YELLOW)make help$(NC)' to see available commands"

# Generate example code
generate-example: ## Generate example client and server code
	@echo "$(BLUE)Generating example code...$(NC)"
	python -m inkly generate examples/petstore.yaml --output client_example/
	python -m inkly generate-server examples/petstore.yaml --output server_example/

# Serve mock server
serve: ## Start mock server for petstore example
	@echo "$(BLUE)Starting mock server...$(NC)"
	python -m inkly serve examples/petstore.yaml --mock

# Package management
publish-test: build ## Publish to test PyPI
	@echo "$(BLUE)Publishing to test PyPI...$(NC)"
	python -m twine upload --repository testpypi dist/*

publish: build ## Publish to PyPI
	@echo "$(YELLOW)⚠️  Publishing to PyPI...$(NC)"
	python -m twine upload dist/*

# Documentation
docs: ## Generate documentation (placeholder)
	@echo "$(BLUE)Generating documentation...$(NC)"
	@echo "$(YELLOW)Documentation generation not implemented yet$(NC)"

# Version management
version: ## Show current version
	@echo "$(BLUE)Current version:$(NC)"
	python -c "import inkly; print(inkly.__version__)"

install-req: ## Install from requirements.txt
	@echo "$(BLUE)Installing from requirements.txt...$(NC)"
	pip install -r requirements.txt

install-dev-req: ## Install from requirements-dev.txt
	@echo "$(BLUE)Installing from requirements-dev.txt...$(NC)"
	pip install -r requirements-dev.txt

install-build-req: ## Install build requirements
	@echo "$(BLUE)Installing build requirements...$(NC)"
	pip install -r requirements-build.txt

# Quick development commands
quick-test: lint-fix test-fast ## Quick development test (fix lint + fast test)

all: clean dev-install test-all build ## Run complete workflow 
