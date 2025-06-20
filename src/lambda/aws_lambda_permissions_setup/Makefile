# Makefile for aws_lambda_permissions_setup Lambda function
# Provides commands for development and testing

# Variables
PYTHON = python3
VENV_DIR = venv
VENV_PYTHON = $(VENV_DIR)/bin/python
VENV_PIP = $(VENV_PYTHON) -m pip
PIP = $(PYTHON) -m pip
PYTEST = $(VENV_PYTHON) -m pytest
COVERAGE = $(VENV_PYTHON) -m coverage
PYLINT = $(VENV_PYTHON) -m pylint
FLAKE8 = $(VENV_PYTHON) -m flake8
BLACK = $(VENV_PYTHON) -m black

# Default target
.PHONY: help
help:
	@echo "Available targets:"
	@echo "  help             - Show this help message"
	@echo "  venv             - Create virtual environment"
	@echo "  install          - Install dependencies in virtual environment"
	@echo "  test             - Run unit tests"
	@echo "  coverage         - Run tests with coverage report"
	@echo "  lint             - Run linting checks"
	@echo "  clean            - Remove build artifacts and caches"
	@echo "  clean-venv       - Remove virtual environment"
	@echo "  all              - Run lint, test, coverage, and package"

# Create virtual environment
.PHONY: venv
venv:
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "Creating virtual environment..."; \
		$(PYTHON) -m venv $(VENV_DIR); \
		echo "Virtual environment created at $(VENV_DIR)"; \
	else \
		echo "Virtual environment already exists at $(VENV_DIR)"; \
	fi

# Install dependencies
.PHONY: install
install: venv
	@echo "Installing dependencies in virtual environment..."
	$(VENV_PIP) install --upgrade pip
	$(VENV_PIP) install -r requirements.txt
	$(VENV_PIP) install pytest-cov pytest-mock pylint flake8 black
	@echo "Dependencies installed successfully"

# Run unit tests
.PHONY: test
test: install
	@echo "Running unit tests..."
	$(PYTEST) -v

# Run tests with coverage
.PHONY: coverage
coverage: install
	@echo "Running tests with coverage..."
	$(PYTEST) --cov=. --cov-report=term --cov-report=xml --cov-report=html

# Run linting
.PHONY: lint
lint: install
	@echo "Running linting checks..."
	$(FLAKE8) *.py
	$(PYLINT) --disable=C0111,C0103,C0303 *.py

# Clean build artifacts and caches
.PHONY: clean
clean:
	rm -rf .pytest_cache
	rm -rf __pycache__
	rm -rf .coverage
	rm -rf htmlcov
	rm -f coverage.xml
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete

# Remove virtual environment
.PHONY: clean-venv
clean-venv:
	@if [ -d "$(VENV_DIR)" ]; then \
		echo "Removing virtual environment..."; \
		rm -rf $(VENV_DIR); \
		echo "Virtual environment removed"; \
	else \
		echo "No virtual environment found"; \
	fi

# Comprehensive check 
.PHONY: all
all: lint test coverage package
	@echo "All checks completed successfully! Ready for deployment."

# Install dev dependencies
.PHONY: dev-install
dev-install: install
	$(VENV_PIP) install pytest-mock pytest-cov pylint flake8 black

# Format code 
.PHONY: format
format: install
	$(BLACK) *.py