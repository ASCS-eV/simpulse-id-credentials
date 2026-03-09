# SimpulseID Credentials Makefile
# ================================

.PHONY: setup install install-dev install-docs submodule-setup generate validate lint format test test-harbour test-cov check all clean help

OMB_SUBMODULE_DIR := submodules/harbour-credentials/submodules/ontology-management-base
HARBOUR_SUBMODULE_DIR := submodules/harbour-credentials

# In CI, use system Python; locally, prefer parent venv then local .venv
ifdef CI
    VENV := $(dir $(shell which python3))..
    PYTHON := python3
else
    ifneq ($(wildcard ../../.venv/bin/python3),)
        VENV := ../../.venv
    else
        VENV := .venv
    endif
    PYTHON := $(VENV)/bin/python3
endif

# Bootstrap interpreter used only to create the venv
BOOTSTRAP_PYTHON := python3

# Absolute path to Python (for use after cd into subdirectories).
# In CI, PYTHON is a bare command ('python3') so resolve via PATH;
# locally it is a relative venv path so abspath works.
ifdef CI
    PYTHON_ABS := $(shell which $(PYTHON))
else
    PYTHON_ABS := $(abspath $(PYTHON))
endif

# Tooling inside the selected virtual environment
PIP := $(PYTHON) -m pip
PRECOMMIT := $(PYTHON) -m pre_commit
PYTEST := $(PYTHON) -m pytest

# Check if dev environment is set up (skipped in CI)
define check_dev_setup
	@if [ -z "$$CI" ] && [ ! -x "$(PYTHON)" ]; then \
		echo ""; \
		echo "ERROR: Development environment not set up."; \
		echo ""; \
		echo "Please run first:"; \
		echo "  make setup"; \
		echo ""; \
		exit 1; \
	fi
	@if ! $(PYTHON) -c "import linkml, harbour; from importlib.metadata import version; version('credentials'); version('ontology-management-base')" 2>/dev/null; then \
		echo ""; \
		echo "ERROR: Dev dependencies not installed."; \
		echo ""; \
		echo "Please run:"; \
		echo "  make setup"; \
		echo ""; \
		exit 1; \
	fi
endef

EXAMPLES := $(wildcard examples/simpulseid-*.json)

# Default target
help: ## Show this help
	@echo "SimpulseID Credentials - Available Commands"
	@echo ""
	@echo "Installation:"
	@echo "  make setup        - Create venv, install all dependencies, setup submodules"
	@echo "  make install      - Install package (user mode)"
	@echo "  make install-dev  - Install with dev dependencies + pre-commit"
	@echo "  make install-docs - Install with docs dependencies (MkDocs)"
	@echo ""
	@echo "Artifacts:"
	@echo "  make generate     - Generate OWL/SHACL/context from LinkML"
	@echo "  make validate     - SHACL-validate example credentials"
	@echo "  make check        - Generate + validate"
	@echo ""
	@echo "Linting:"
	@echo "  make lint         - Run pre-commit checks"
	@echo "  make format       - Format code with black/isort"
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

# ---------- Setup ----------

setup: ## Create venv, install deps, setup submodules
	@echo "Setting up development environment..."
	@echo "Checking Python virtual environment and dependencies..."
	@set -e; \
	if [ ! -x "$(PYTHON)" ]; then \
		echo "Python virtual environment not found; bootstrapping..."; \
		$(MAKE) --no-print-directory $(VENV)/bin/activate; \
	elif $(PYTHON) -c "import pre_commit, linkml, harbour; from importlib.metadata import version; version('credentials'); version('ontology-management-base')" >/dev/null 2>&1; then \
		echo "OK: Python virtual environment and dependencies are ready at $(VENV)"; \
	else \
		echo "Python virtual environment found but dependencies are missing; bootstrapping..."; \
		$(MAKE) --no-print-directory -B $(VENV)/bin/activate; \
	fi
	@echo ""
	@echo "Setup complete. Activate with: source $(VENV)/bin/activate"

$(VENV)/bin/python3:
	@echo "Creating Python virtual environment at $(VENV)..."
	@$(BOOTSTRAP_PYTHON) -m venv $(VENV)
	@$(PIP) install --upgrade pip
	@echo "OK: Python virtual environment ready"

$(VENV)/bin/activate: $(VENV)/bin/python3
	@echo "Installing submodule dependencies..."
	@$(MAKE) --no-print-directory submodule-setup
	@echo "Installing Python dependencies..."
	@$(PIP) install -e ".[dev]"
	@$(PRECOMMIT) install
	@echo "OK: Python development environment ready"

# Setup submodules using the same active venv (pip install preferred, make -C fallback)
submodule-setup:
	@echo "Setting up harbour-credentials submodule..."
	@set -e; \
	if [ -f "$(HARBOUR_SUBMODULE_DIR)/pyproject.toml" ]; then \
		$(PIP) install -e "$(HARBOUR_SUBMODULE_DIR)[dev]"; \
		echo "OK: harbour-credentials submodule setup complete"; \
	elif [ -f "$(HARBOUR_SUBMODULE_DIR)/Makefile" ]; then \
		$(MAKE) --no-print-directory -C $(HARBOUR_SUBMODULE_DIR) setup \
			VENV="$(abspath $(VENV))" \
			PYTHON="$(abspath $(PYTHON))" \
			PIP="$(abspath $(PYTHON)) -m pip" \
			PRECOMMIT="$(abspath $(PYTHON)) -m pre_commit" \
			PYTEST="$(abspath $(PYTHON)) -m pytest"; \
		echo "OK: harbour-credentials submodule setup complete"; \
	else \
		echo "WARNING: Skipping harbour-credentials submodule setup (not found)"; \
	fi
	@echo "Setting up ontology-management-base submodule..."
	@set -e; \
	if [ -f "$(OMB_SUBMODULE_DIR)/pyproject.toml" ]; then \
		$(PIP) install -e "$(OMB_SUBMODULE_DIR)"; \
		echo "OK: ontology-management-base submodule setup complete"; \
	elif [ -f "$(OMB_SUBMODULE_DIR)/Makefile" ]; then \
		$(MAKE) --no-print-directory -C $(OMB_SUBMODULE_DIR) setup \
			VENV="$(abspath $(VENV))" \
			PYTHON="$(abspath $(PYTHON))" \
			PIP="$(abspath $(PYTHON)) -m pip" \
			PRECOMMIT="$(abspath $(PYTHON)) -m pre_commit" \
			PYTEST="$(abspath $(PYTHON)) -m pytest"; \
		echo "OK: ontology-management-base submodule setup complete"; \
	else \
		echo "WARNING: Skipping ontology-management-base submodule setup (not found)"; \
	fi

# ---------- Install ----------

install: ## Install package (user mode)
	@echo "Installing package in editable mode..."
ifndef CI
	@$(MAKE) --no-print-directory $(VENV)/bin/python3
endif
	@$(PIP) install -e $(HARBOUR_SUBMODULE_DIR) -e $(OMB_SUBMODULE_DIR) -e .
	@echo "OK: Package installation complete"

install-dev: ## Install with dev dependencies + pre-commit
	@echo "Installing development dependencies..."
ifndef CI
	@$(MAKE) --no-print-directory $(VENV)/bin/python3
endif
	@$(PIP) install -e "$(HARBOUR_SUBMODULE_DIR)[dev]" -e $(OMB_SUBMODULE_DIR) -e ".[dev]"
ifndef CI
	@$(PRECOMMIT) install
endif
	@echo "OK: Development dependencies installed"

install-docs: ## Install with docs dependencies (for MkDocs builds)
	@echo "Installing documentation dependencies..."
ifndef CI
	@$(MAKE) --no-print-directory $(VENV)/bin/python3
endif
	@$(PIP) install -e "$(HARBOUR_SUBMODULE_DIR)[dev]" -e $(OMB_SUBMODULE_DIR) -e ".[docs]"
	@echo "OK: Documentation dependencies installed"

# ---------- Lint ----------

lint: ## Run pre-commit (black, isort, flake8, JSON-LD parse, Turtle parse)
	$(call check_dev_setup)
	@$(PRECOMMIT) run --all-files

format: ## Format code with black and isort
	$(call check_dev_setup)
	@$(PYTHON) -m black src/ tests/
	@$(PYTHON) -m isort src/ tests/

# ---------- Generate ----------

generate: ## Generate JSON-LD contexts, SHACL shapes, OWL ontologies from LinkML
	$(call check_dev_setup)
	@echo "Generating harbour artifacts..."
	@cd $(HARBOUR_SUBMODULE_DIR) && PYTHONPATH=src/python:$$PYTHONPATH $(PYTHON_ABS) src/python/harbour/generate_artifacts.py
	@echo "Generating simpulseid artifacts..."
	@$(PYTHON) src/generate_artifacts.py

# ---------- Validate ----------

validate: ## SHACL-validate all example credentials
	$(call check_dev_setup)
	@if [ -z "$(EXAMPLES)" ]; then \
		echo "No example files found."; \
		exit 0; \
	fi
	@echo "Running SHACL data conformance check on examples..."
	@cd $(OMB_SUBMODULE_DIR) && \
		$(PYTHON_ABS) -m src.tools.validators.validation_suite \
			--run check-data-conformance \
			--data-paths $(addprefix ../../../../,$(EXAMPLES)) \
			--artifacts ../../../../artifacts ../../../../$(HARBOUR_SUBMODULE_DIR)/artifacts

# ---------- Test ----------

test-harbour: ## Run harbour-credentials JOSE tests (excludes interop — covered by harbour CI)
	@cd $(HARBOUR_SUBMODULE_DIR) && PYTHONPATH=src/python:$$PYTHONPATH $(PYTHON_ABS) -m pytest tests/ -v --ignore=tests/interop

test: generate test-harbour ## Run all tests (harbour + main repo)
	@PYTHONPATH=$(HARBOUR_SUBMODULE_DIR)/src/python:$$PYTHONPATH $(PYTEST) tests/ -v

test-cov: ## Run tests with coverage report
	$(call check_dev_setup)
	@PYTHONPATH=$(HARBOUR_SUBMODULE_DIR)/src/python:$$PYTHONPATH $(PYTEST) tests/ --cov=src --cov-report=html --cov-report=term

# ---------- Compound targets ----------

check: generate validate ## Generate artifacts then validate examples

all: setup lint check test ## Full end-to-end: setup, lint, generate, validate, test

# ---------- Clean ----------

clean: ## Remove generated artifacts (keeps venv)
	@echo "Cleaning generated files and caches..."
	@rm -rf artifacts/simpulseid
	@rm -rf build/ dist/ *.egg-info/
	@rm -rf .pytest_cache/ htmlcov .coverage
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "OK: Cleaned"
