# Makefile for Box Packer development

# Variables
PYTHON = python
PIP = pip
VENV = .venv
VENV_ACTIVATE = $(VENV)\Scripts\activate

# Default target
help:
	@echo "Available targets:"
	@echo "  setup        - Set up development environment"
	@echo "  install      - Install dependencies"
	@echo "  test         - Run unit tests"
	@echo "  run          - Run the application"
	@echo "  clean        - Clean up cache files"
	@echo "  lint         - Run code linting (if flake8 is installed)"
	@echo "  format       - Format code (if black is installed)"
	@echo "  requirements - Update requirements.txt"
	@echo "  package      - Build distribution package"

# Set up development environment
setup:
	$(PYTHON) -m venv $(VENV)
	$(VENV_ACTIVATE) && $(PIP) install --upgrade pip
	$(VENV_ACTIVATE) && $(PIP) install -r requirements.txt

# Install dependencies
install:
	$(PIP) install -r requirements.txt

# Run unit tests
test:
	$(PYTHON) -m unittest discover -s tests -p "test_*.py" -v

# Run the application
run:
	$(PYTHON) main.py

# Clean up cache files
clean:
	if exist "__pycache__" rmdir /s /q "__pycache__"
	if exist "algorithms\__pycache__" rmdir /s /q "algorithms\__pycache__"
	if exist "models\__pycache__" rmdir /s /q "models\__pycache__"
	if exist "utils\__pycache__" rmdir /s /q "utils\__pycache__"
	if exist "tests\__pycache__" rmdir /s /q "tests\__pycache__"
	if exist "build" rmdir /s /q "build"
	if exist "dist" rmdir /s /q "dist"
	if exist "*.egg-info" rmdir /s /q "*.egg-info"

# Run linting (if flake8 is installed)
lint:
	-$(PYTHON) -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	-$(PYTHON) -m flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

# Format code (if black is installed)
format:
	-$(PYTHON) -m black .

# Update requirements.txt
requirements:
	$(PIP) freeze > requirements.txt

# Build distribution package
package:
	$(PYTHON) setup.py sdist bdist_wheel

.PHONY: help setup install test run clean lint format requirements package
