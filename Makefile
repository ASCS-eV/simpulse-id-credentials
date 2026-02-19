.PHONY: setup install install-dev lint format generate validate check test test-harbour test-cov all clean help

VENV      := .venv

# Use venv if it exists, otherwise use system python
ifneq ($(wildcard $(VENV)/bin/python3),)
    PYTHON    := $(VENV)/bin/python3
    PIP       := $(VENV)/bin/pip
    PRECOMMIT := $(VENV)/bin/pre-commit
    PYTEST    := $(VENV)/bin/pytest
else
    PYTHON    := python3
    PIP       := python3 -m pip
    PRECOMMIT := pre-commit
    PYTEST    := pytest
endif

# Check if dev environment is set up
define check_dev_setup
	@if [ ! -d "$(VENV)" ]; then \
		echo ""; \
		echo "❌ Development environment not set up."; \
		echo ""; \
		echo "Please run first:"; \
		echo "  make setup"; \
		echo ""; \
		exit 1; \
	fi
	@if ! $(PYTHON) -c "import pre_commit" 2>/dev/null; then \
		echo ""; \
		echo "❌ Dev dependencies not installed."; \
		echo ""; \
		echo "Please run:"; \
		echo "  source $(VENV)/bin/activate"; \
		echo "  make install-dev"; \
		echo ""; \
		exit 1; \
	fi
endef

EXAMPLES  := $(wildcard examples/*.json examples/*.jsonld)

# ---------- Setup ----------

$(VENV)/bin/activate:
	@python3 -m venv $(VENV)

setup: $(VENV)/bin/activate ## Create venv, install deps, install pre-commit hooks
	@$(PIP) install --upgrade pip
	@$(PIP) install -e "./submodules/harbour-credentials[dev]" -e ./submodules/ontology-management-base -e ".[dev]"
	@$(PYTHON) -m pre_commit install
	@echo ""
	@echo "✅ Setup complete. Activate with: source $(VENV)/bin/activate"

# ---------- Install ----------

install: ## Install package (user mode)
	@$(PIP) install -e ./submodules/ontology-management-base -e ./submodules/harbour-credentials -e .

install-dev: ## Install with dev dependencies + pre-commit
	@$(PIP) install -e "./submodules/harbour-credentials[dev]" -e ./submodules/ontology-management-base -e ".[dev]"
	@$(PYTHON) -m pre_commit install

# ---------- Lint ----------

lint: ## Run pre-commit (black, isort, flake8, JSON-LD parse, Turtle parse)
	$(call check_dev_setup)
	@$(PYTHON) -m pre_commit run --all-files

format: ## Format code with black and isort
	$(call check_dev_setup)
	@$(PYTHON) -m black src/ tests/
	@$(PYTHON) -m isort src/ tests/

# ---------- Generate ----------

generate: ## Generate JSON-LD contexts, SHACL shapes, OWL ontologies from LinkML
	@$(PYTHON) src/generate_from_linkml.py

# ---------- Validate ----------

validate: ## SHACL-validate all example credentials
	@if [ -z "$(EXAMPLES)" ]; then \
		echo "No example files found."; \
		exit 0; \
	fi
	@$(PYTHON) -m src.tools.validators.validation_suite --run check-data-conformance \
		--data-paths $(EXAMPLES)

# ---------- Test ----------

test-harbour: ## Run harbour-credentials JOSE tests
	@cd submodules/harbour-credentials && PYTHONPATH=src/python:$$PYTHONPATH $(abspath $(PYTHON)) -m pytest tests/ -v

test: test-harbour ## Run all tests (harbour + main repo)
	@PYTHONPATH=submodules/harbour-credentials/src/python:$$PYTHONPATH $(PYTEST) tests/ -v

test-cov: ## Run tests with coverage report
	$(call check_dev_setup)
	@PYTHONPATH=submodules/harbour-credentials/src/python:$$PYTHONPATH $(PYTEST) tests/ --cov=src --cov-report=html --cov-report=term

# ---------- Compound targets ----------

check: generate validate ## Generate artifacts then validate examples

all: setup lint check test ## Full end-to-end: setup, lint, generate, validate, test

# ---------- Clean ----------

clean: ## Remove generated artifacts (keeps venv)
	@rm -rf artifacts/simpulseid
	@rm -rf submodules/harbour-credentials/artifacts/core
	@rm -rf submodules/harbour-credentials/artifacts/harbour
	@rm -rf build/ dist/ *.egg-info/
	@rm -rf .pytest_cache/ htmlcov .coverage
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cleaned"

# ---------- Help ----------

help: ## Show this help
	@echo "Credentials - Available Commands"
	@echo ""
	@echo "Installation:"
	@echo "  make setup        - Create venv and install all dependencies"
	@echo "  make install      - Install packages (user mode)"
	@echo "  make install-dev  - Install with dev dependencies + pre-commit"
	@echo ""
	@echo "Linting:"
	@echo "  make lint         - Run pre-commit checks"
	@echo "  make format       - Format code with black/isort"
	@echo ""
	@echo "Artifacts:"
	@echo "  make generate     - Generate OWL/SHACL/context from LinkML"
	@echo ""
	@echo "Validation:"
	@echo "  make validate     - SHACL-validate example credentials"
	@echo "  make check        - Generate + validate"
	@echo ""
	@echo "Testing:"
	@echo "  make test         - Run all tests"
	@echo "  make test-harbour - Run harbour-credentials tests only"
	@echo "  make test-cov     - Run tests with coverage report"
	@echo ""
	@echo "Compound:"
	@echo "  make all          - Full end-to-end: setup, lint, check, test"
	@echo ""
	@echo "Cleaning:"
	@echo "  make clean        - Remove generated artifacts and caches"
