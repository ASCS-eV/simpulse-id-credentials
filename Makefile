# SimpulseID Credentials Makefile
# ================================

.PHONY: setup install generate validate lint format test story check all clean help \
	release-artifacts \
	_help_general _help_setup _help_install _help_validate _help_lint _help_format _help_test _help_story \
	_setup_default _setup_submodules _install_default _install_dev _install_docs \
	_validate_all _validate_simpulseid _validate_harbour \
	_lint_default _lint_md _format_default _format_md \
	_test_all _test_harbour _test_simpulseid _test_cov \
	_story_all _story_simpulseid _story_harbour _story_sign _story_verify

OMB_SUBMODULE_DIR := submodules/harbour-credentials/submodules/ontology-management-base
HARBOUR_SUBMODULE_DIR := submodules/harbour-credentials
LINKML_SUBMODULE_DIR := $(OMB_SUBMODULE_DIR)/submodules/linkml/packages/linkml
# Absolute path to repo root — used when cd'ing into submodules to reference
# back to top-level paths (avoids fragile ../../../../ paths).
REPO_ROOT := $(abspath .)

# Allow callers to override the venv path/tooling.
VENV ?= .venv

# OS detection for cross-platform support (Windows vs Unix)
ifeq ($(OS),Windows_NT)
    ifndef CI
        ifneq ($(wildcard ../../.venv/Scripts/python.exe),)
            VENV := ../../.venv
        endif
    endif
    VENV_BIN := $(VENV)/Scripts
    VENV_PYTHON := $(VENV_BIN)/python.exe
    ifdef CI
        PYTHON ?= python
    else
        PYTHON ?= $(VENV_PYTHON)
    endif
    BOOTSTRAP_PYTHON ?= python
    ACTIVATE_SCRIPT := $(VENV_BIN)/activate
    ACTIVATE_HINT := PowerShell: $(subst /,\,$(VENV_BIN))\Activate.ps1; Git Bash: source $(ACTIVATE_SCRIPT)
    PYTHONPATH_SEP := ;
else
    ifneq ($(wildcard ../../.venv/bin/python3),)
        VENV := ../../.venv
    endif
    VENV_BIN := $(VENV)/bin
    VENV_PYTHON := $(VENV_BIN)/python3
    ifdef CI
        PYTHON ?= python3
    else
        PYTHON ?= $(VENV_PYTHON)
    endif
    BOOTSTRAP_PYTHON ?= python3
    ACTIVATE_SCRIPT := $(VENV_BIN)/activate
    ACTIVATE_HINT := source $(ACTIVATE_SCRIPT)
    PYTHONPATH_SEP := :
endif

# Absolute path to Python (for use after cd into subdirectories).
# In CI, PYTHON is a bare command ('python3') so resolve via PATH;
# locally it is a relative venv path so abspath works.
# When a parent Makefile passes an already-absolute Windows path
# (containing ':'), $(abspath) would mangle it — skip in that case.
ifdef CI
    PYTHON_ABS := $(shell command -v $(PYTHON))
else ifneq ($(findstring :,$(PYTHON)),)
    PYTHON_ABS := $(PYTHON)
else
    PYTHON_ABS := $(abspath $(PYTHON))
endif

# Tooling inside the selected virtual environment
PIP := "$(PYTHON)" -m pip
PRECOMMIT := "$(PYTHON)" -m pre_commit
PYTEST := "$(PYTHON)" -m pytest

# Check if dev environment is set up (skipped in CI)
define check_dev_setup
	@if [ -z "$$CI" ] && [ ! -f "$(PYTHON)" ]; then \
		echo ""; \
		echo "ERROR: Development environment not set up."; \
		echo ""; \
		echo "Please run first:"; \
		echo "  make setup"; \
		echo ""; \
		exit 1; \
	fi
	@if ! "$(PYTHON)" -c "import linkml, harbour; from importlib.metadata import version; version('credentials'); version('ontology-management-base')" 2>/dev/null; then \
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
SIMPULSEID_VALIDATE_PATH ?=
GROUPED_COMMANDS := setup install validate lint format test story
PRIMARY_GOAL := $(firstword $(MAKECMDGOALS))
SUBCOMMAND_GOALS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))

# Grouped command mode: treat trailing goals as subcommands
ifneq ($(filter $(PRIMARY_GOAL),$(GROUPED_COMMANDS)),)
.PHONY: $(SUBCOMMAND_GOALS)

$(SUBCOMMAND_GOALS):
	@:
else
help: ## Show this help
	@"$(MAKE)" --no-print-directory _help_general
endif

# Default target
_help_general:
	@echo "SimpulseID Credentials - Available Commands"
	@echo ""
	@echo "Installation:"
	@echo "  make setup        - Create venv, install all dependencies, setup submodules"
	@echo "  make setup help   - Show setup subcommands"
	@echo "  make install      - Install package (user mode)"
	@echo "  make install help - Show install subcommands"
	@echo ""
	@echo "Artifacts:"
	@echo "  make generate     - Generate OWL/SHACL/context from LinkML"
	@echo "  make validate     - Run Harbour + SimpulseID validation"
	@echo "  make validate help - Show validate subcommands"
	@echo "  make check        - Generate + validate"
	@echo ""
	@echo "Linting:"
	@echo "  make lint         - Run pre-commit checks"
	@echo "  make lint help    - Show lint subcommands"
	@echo "  make format       - Format code with ruff"
	@echo "  make format help  - Show format subcommands"
	@echo ""
	@echo "Testing:"
	@echo "  make test         - Run all tests"
	@echo "  make test help    - Show test subcommands"
	@echo "  make story        - Run the full Harbour + SimpulseID signing/verification storyline"
	@echo "  make story help   - Show story subcommands"
	@echo ""
	@echo "Compound:"
	@echo "  make all          - Full end-to-end: setup, lint, check, test"
	@echo ""
	@echo "Cleaning:"
	@echo "  make clean        - Remove generated artifacts and caches"

_help_setup:
	@echo "Setup subcommands:"
	@echo "  make setup             - Create venv, install dependencies, and setup submodules"
	@echo "  make setup submodules  - Setup the Harbour + ontology submodules in the active environment"

_help_install:
	@echo "Install subcommands:"
	@echo "  make install      - Install package (user mode)"
	@echo "  make install dev  - Install with dev dependencies + pre-commit"
	@echo "  make install docs - Install with docs dependencies (MkDocs)"

_help_validate:
	@echo "Validate subcommands:"
	@echo "  make validate             - Run Harbour + SimpulseID validation"
	@echo "  make validate harbour     - Run Harbour SHACL validation in the submodule"
	@echo "  make validate simpulseid  - Run top-level SimpulseID SHACL validation"
	@echo "  make validate simpulseid SIMPULSEID_VALIDATE_PATH=examples/... - Validate one SimpulseID .json/.jsonld file or folder"

_help_lint:
	@echo "Lint subcommands:"
	@echo "  make lint      - Run pre-commit checks"
	@echo "  make lint md   - Lint Markdown files with markdownlint-cli2"

_help_format:
	@echo "Format subcommands:"
	@echo "  make format      - Format code with ruff"
	@echo "  make format md   - Auto-fix Markdown lint violations"

_help_test:
	@echo "Test subcommands:"
	@echo "  make test             - Run all tests"
	@echo "  make test harbour     - Run harbour-credentials tests only"
	@echo "  make test simpulseid  - Run top-level SimpulseID tests only"
	@echo "  make test cov         - Run tests with coverage report"

_help_story:
	@echo "Story subcommands:"
	@echo "  make story             - Run the full Harbour + SimpulseID storyline"
	@echo "  make story harbour     - Run the Harbour storyline in the submodule"
	@echo "  make story simpulseid  - Generate, validate, sign, and verify SimpulseID examples"
	@echo "  make story sign        - Write ignored signed SimpulseID artifacts to examples/signed/"
	@echo "  make story verify      - Verify the signed SimpulseID artifacts with the real verifier"

# ---------- Setup ----------

setup: ## Create venv, install deps, setup submodules
	@set -- $(filter-out $@,$(MAKECMDGOALS)); \
	subcommand="$${1:-default}"; \
	if [ "$$#" -gt 1 ]; then \
		echo "ERROR: Too many subcommands for 'make setup': $(filter-out $@,$(MAKECMDGOALS))"; \
		echo "Run 'make setup help' for available options."; \
		exit 1; \
	fi; \
	case "$$subcommand" in \
		default) "$(MAKE)" --no-print-directory _setup_default ;; \
		submodules) "$(MAKE)" --no-print-directory _setup_submodules ;; \
		help) "$(MAKE)" --no-print-directory _help_setup ;; \
		*) echo "ERROR: Unknown setup subcommand '$$subcommand'"; echo "Run 'make setup help' for available options."; exit 1 ;; \
	esac

_setup_default:
	@echo "Setting up development environment..."
	@echo "Checking Python virtual environment and dependencies..."
ifdef CI
	@set -e; \
	if "$(PYTHON)" -c "import pre_commit, linkml, harbour; from importlib.metadata import version; version('credentials'); version('ontology-management-base')" >/dev/null 2>&1; then \
		echo "OK: Python environment and dependencies are ready via $(PYTHON)"; \
	else \
		echo "CI environment missing dependencies; bootstrapping..."; \
		"$(MAKE)" --no-print-directory setup submodules; \
		$(PIP) install -e ".[dev]"; \
		$(PRECOMMIT) install; \
	fi
else
	@set -e; \
	if [ ! -f "$(PYTHON)" ]; then \
		echo "Python virtual environment not found; bootstrapping..."; \
		"$(MAKE)" --no-print-directory "$(ACTIVATE_SCRIPT)"; \
	elif "$(PYTHON)" -c "import pre_commit, linkml, harbour; from importlib.metadata import version; version('credentials'); version('ontology-management-base')" >/dev/null 2>&1; then \
		echo "OK: Python virtual environment and dependencies are ready at $(VENV)"; \
	else \
		echo "Python virtual environment found but dependencies are missing; bootstrapping..."; \
		"$(MAKE)" --no-print-directory -B "$(ACTIVATE_SCRIPT)"; \
	fi
endif
	@echo ""
	@echo "Setup complete. Activate with: $(ACTIVATE_HINT)"

$(VENV_PYTHON):
	@echo "Creating Python virtual environment at $(VENV)..."
	@"$(BOOTSTRAP_PYTHON)" -m venv "$(VENV)"
	@$(PIP) install --upgrade pip
	@echo "OK: Python virtual environment ready"

$(ACTIVATE_SCRIPT): $(VENV_PYTHON)
	@echo "Installing submodule dependencies..."
	@"$(MAKE)" --no-print-directory setup submodules
	@echo "Installing Python dependencies..."
	@$(PIP) install -e ".[dev]"
	@$(PRECOMMIT) install
	@echo "OK: Python development environment ready"

# Setup submodules using the same active venv (pip install preferred, make -C fallback)
_setup_submodules:
	@echo "Setting up LinkML from OMB submodule (single source of truth)..."
	@set -e; \
	if [ -f "$(LINKML_SUBMODULE_DIR)/pyproject.toml" ]; then \
		$(PIP) install -e "$(LINKML_SUBMODULE_DIR)"; \
		echo "OK: LinkML (ASCS-eV fork) installed from submodule"; \
	else \
		echo "WARNING: LinkML submodule not found at $(LINKML_SUBMODULE_DIR)"; \
	fi
	@echo "Setting up harbour-credentials submodule..."
	@set -e; \
	if [ -f "$(HARBOUR_SUBMODULE_DIR)/pyproject.toml" ]; then \
		$(PIP) install -e "$(HARBOUR_SUBMODULE_DIR)[dev]"; \
		echo "OK: harbour-credentials submodule setup complete"; \
	elif [ -f "$(HARBOUR_SUBMODULE_DIR)/Makefile" ]; then \
		"$(MAKE)" --no-print-directory -C "$(HARBOUR_SUBMODULE_DIR)" setup \
			VENV="$(abspath $(VENV))" \
			PYTHON="$(PYTHON_ABS)"; \
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
		"$(MAKE)" --no-print-directory -C "$(OMB_SUBMODULE_DIR)" setup \
			VENV="$(abspath $(VENV))" \
			PYTHON="$(PYTHON_ABS)"; \
		echo "OK: ontology-management-base submodule setup complete"; \
	else \
		echo "WARNING: Skipping ontology-management-base submodule setup (not found)"; \
	fi

# ---------- Install ----------

install:
	@set -- $(filter-out $@,$(MAKECMDGOALS)); \
	subcommand="$${1:-default}"; \
	if [ "$$#" -gt 1 ]; then \
		echo "ERROR: Too many subcommands for 'make install': $(filter-out $@,$(MAKECMDGOALS))"; \
		echo "Run 'make install help' for available options."; \
		exit 1; \
	fi; \
	case "$$subcommand" in \
		default) "$(MAKE)" --no-print-directory _install_default ;; \
		dev) "$(MAKE)" --no-print-directory _install_dev ;; \
		docs) "$(MAKE)" --no-print-directory _install_docs ;; \
		help) "$(MAKE)" --no-print-directory _help_install ;; \
		*) echo "ERROR: Unknown install subcommand '$$subcommand'"; echo "Run 'make install help' for available options."; exit 1 ;; \
	esac

_install_default: ## Install package (user mode)
	@echo "Installing package in editable mode..."
ifndef CI
	@"$(MAKE)" --no-print-directory "$(VENV_PYTHON)"
endif
	@$(PIP) install -e $(HARBOUR_SUBMODULE_DIR) -e $(OMB_SUBMODULE_DIR) -e .
	@echo "OK: Package installation complete"

_install_dev: ## Install with dev dependencies + pre-commit
	@echo "Installing development dependencies..."
ifndef CI
	@"$(MAKE)" --no-print-directory "$(VENV_PYTHON)"
endif
	@$(PIP) install -e "$(LINKML_SUBMODULE_DIR)" -e "$(HARBOUR_SUBMODULE_DIR)[dev]" -e $(OMB_SUBMODULE_DIR) -e ".[dev]"
ifndef CI
	@$(PRECOMMIT) install
endif
	@echo "OK: Development dependencies installed"

_install_docs: ## Install with docs dependencies (for MkDocs builds)
	@echo "Installing documentation dependencies..."
ifndef CI
	@"$(MAKE)" --no-print-directory "$(VENV_PYTHON)"
endif
	@$(PIP) install -e "$(HARBOUR_SUBMODULE_DIR)[dev]" -e $(OMB_SUBMODULE_DIR) -e ".[docs]"
	@echo "OK: Documentation dependencies installed"

# ---------- Lint ----------

lint:
	@set -- $(filter-out $@,$(MAKECMDGOALS)); \
	subcommand="$${1:-default}"; \
	if [ "$$#" -gt 1 ]; then \
		echo "ERROR: Too many subcommands for 'make lint': $(filter-out $@,$(MAKECMDGOALS))"; \
		echo "Run 'make lint help' for available options."; \
		exit 1; \
	fi; \
	case "$$subcommand" in \
		default) "$(MAKE)" --no-print-directory _lint_default ;; \
		md) "$(MAKE)" --no-print-directory _lint_md ;; \
		help) "$(MAKE)" --no-print-directory _help_lint ;; \
		*) echo "ERROR: Unknown lint subcommand '$$subcommand'"; echo "Run 'make lint help' for available options."; exit 1 ;; \
	esac

_lint_default: ## Run pre-commit (ruff, JSON-LD parse, Turtle parse, markdownlint)
	$(call check_dev_setup)
	@$(PRECOMMIT) run --all-files

_lint_md: ## Lint Markdown files with markdownlint-cli2
	@echo "Linting Markdown files..."
	@npx --yes markdownlint-cli2
	@echo "OK: Markdown lint complete"

format:
	@set -- $(filter-out $@,$(MAKECMDGOALS)); \
	subcommand="$${1:-default}"; \
	if [ "$$#" -gt 1 ]; then \
		echo "ERROR: Too many subcommands for 'make format': $(filter-out $@,$(MAKECMDGOALS))"; \
		echo "Run 'make format help' for available options."; \
		exit 1; \
	fi; \
	case "$$subcommand" in \
		default) "$(MAKE)" --no-print-directory _format_default ;; \
		md) "$(MAKE)" --no-print-directory _format_md ;; \
		help) "$(MAKE)" --no-print-directory _help_format ;; \
		*) echo "ERROR: Unknown format subcommand '$$subcommand'"; echo "Run 'make format help' for available options."; exit 1 ;; \
	esac

_format_default: ## Format code with ruff
	$(call check_dev_setup)
	@"$(PYTHON)" -m ruff check --fix src/ tests/
	@"$(PYTHON)" -m ruff format src/ tests/

_format_md: ## Auto-fix Markdown lint violations
	@echo "Fixing Markdown files..."
	@npx --yes markdownlint-cli2 --fix
	@echo "OK: Markdown formatting complete"

# ---------- Generate ----------

generate: ## Generate JSON-LD contexts, SHACL shapes, OWL ontologies from LinkML
	$(call check_dev_setup)
	@echo "Generating harbour artifacts..."
	@cd "$(HARBOUR_SUBMODULE_DIR)" && PYTHONPATH="src/python$(PYTHONPATH_SEP)$$PYTHONPATH" "$(PYTHON_ABS)" src/python/harbour/generate_artifacts.py
	@echo "Generating simpulseid artifacts..."
	@"$(PYTHON)" src/generate_artifacts.py

# ---------- Validate ----------

validate:
	@set -- $(filter-out $@,$(MAKECMDGOALS)); \
	subcommand="$${1:-default}"; \
	if [ "$$#" -gt 1 ]; then \
		echo "ERROR: Too many subcommands for 'make validate': $(filter-out $@,$(MAKECMDGOALS))"; \
		echo "Run 'make validate help' for available options."; \
		exit 1; \
	fi; \
	case "$$subcommand" in \
		default) "$(MAKE)" --no-print-directory _validate_all ;; \
		harbour) "$(MAKE)" --no-print-directory _validate_harbour ;; \
		simpulseid) "$(MAKE)" --no-print-directory _validate_simpulseid ;; \
		help) "$(MAKE)" --no-print-directory _help_validate ;; \
		*) echo "ERROR: Unknown validate subcommand '$$subcommand'"; echo "Run 'make validate help' for available options."; exit 1 ;; \
	esac

_validate_simpulseid: ## SHACL-validate top-level SimpulseID examples
	$(call check_dev_setup)
	@if [ -z "$(SIMPULSEID_VALIDATE_PATH)" ] && [ -z "$(EXAMPLES)" ]; then \
		echo "No example files found."; \
		exit 0; \
	fi
	@echo "Running SHACL data conformance check on SimpulseID examples..."
	@cd "$(OMB_SUBMODULE_DIR)" && \
		if [ -n "$(SIMPULSEID_VALIDATE_PATH)" ]; then \
			target_path="$(REPO_ROOT)/$(SIMPULSEID_VALIDATE_PATH)" ; \
			if [ -d "$$target_path" ]; then \
				json_count=$$(find "$$target_path" -maxdepth 1 -type f \( -name '*.json' -o -name '*.jsonld' \) | wc -l) ; \
				if [ "$$json_count" -eq 0 ]; then \
					echo "ERROR: No .json or .jsonld files found under $$target_path" ; \
					exit 1 ; \
				fi ; \
			elif [ -f "$$target_path" ]; then \
				case "$$target_path" in \
					*.json|*.jsonld) ;; \
					*) echo "ERROR: SimpulseID SHACL validation only supports .json/.jsonld files or directories: $$target_path" ; exit 1 ;; \
				esac ; \
			else \
				echo "ERROR: Validation path not found: $$target_path" ; \
				exit 1 ; \
			fi ; \
			"$(PYTHON_ABS)" -m src.tools.validators.validation_suite \
				--run check-data-conformance \
				--data-paths "$$target_path" \
				--artifacts $(REPO_ROOT)/artifacts $(REPO_ROOT)/$(HARBOUR_SUBMODULE_DIR)/artifacts ; \
		else \
			"$(PYTHON_ABS)" -m src.tools.validators.validation_suite \
				--run check-data-conformance \
				--data-paths $(addprefix $(REPO_ROOT)/,$(EXAMPLES)) \
				--artifacts $(REPO_ROOT)/artifacts $(REPO_ROOT)/$(HARBOUR_SUBMODULE_DIR)/artifacts ; \
		fi

_validate_harbour: ## Run Harbour SHACL validation inside the submodule
	@echo "Running Harbour validation from root..."
	@"$(MAKE)" --no-print-directory -C "$(HARBOUR_SUBMODULE_DIR)" \
		validate shacl \
		VENV="$(abspath $(VENV))" \
		PYTHON="$(PYTHON_ABS)"
	@echo "OK: Harbour validation complete"

_validate_all: ## Run Harbour + SimpulseID validation
	@echo "Running full repository validation..."
	@"$(MAKE)" --no-print-directory _validate_harbour
	@"$(MAKE)" --no-print-directory _validate_simpulseid
	@echo "OK: Full repository validation complete"

# ---------- Test ----------

test:
	@set -- $(filter-out $@,$(MAKECMDGOALS)); \
	subcommand="$${1:-default}"; \
	if [ "$$#" -gt 1 ]; then \
		echo "ERROR: Too many subcommands for 'make test': $(filter-out $@,$(MAKECMDGOALS))"; \
		echo "Run 'make test help' for available options."; \
		exit 1; \
	fi; \
	case "$$subcommand" in \
		default) "$(MAKE)" --no-print-directory _test_all ;; \
		harbour) "$(MAKE)" --no-print-directory _test_harbour ;; \
		simpulseid) "$(MAKE)" --no-print-directory _test_simpulseid ;; \
		cov) "$(MAKE)" --no-print-directory _test_cov ;; \
		help) "$(MAKE)" --no-print-directory _help_test ;; \
		*) echo "ERROR: Unknown test subcommand '$$subcommand'"; echo "Run 'make test help' for available options."; exit 1 ;; \
	esac

_test_harbour: ## Run harbour-credentials JOSE tests (excludes interop — covered by harbour CI)
	@cd "$(HARBOUR_SUBMODULE_DIR)" && PYTHONPATH="src/python$(PYTHONPATH_SEP)$$PYTHONPATH" "$(PYTHON_ABS)" -m pytest tests/ -v --ignore=tests/interop

_test_simpulseid:
	$(call check_dev_setup)
	@PYTHONPATH="$(HARBOUR_SUBMODULE_DIR)/src/python$(PYTHONPATH_SEP)$$PYTHONPATH" $(PYTEST) tests/ -v

_test_all: ## Run all tests (harbour + main repo)
	@"$(MAKE)" --no-print-directory generate
	@"$(MAKE)" --no-print-directory _test_harbour
	@"$(MAKE)" --no-print-directory _test_simpulseid

_test_cov: ## Run tests with coverage report
	$(call check_dev_setup)
	@PYTHONPATH="$(HARBOUR_SUBMODULE_DIR)/src/python$(PYTHONPATH_SEP)$$PYTHONPATH" $(PYTEST) tests/ --cov=src --cov-report=html --cov-report=term

story:
	@set -- $(filter-out $@,$(MAKECMDGOALS)); \
	subcommand="$${1:-default}"; \
	if [ "$$#" -gt 1 ]; then \
		echo "ERROR: Too many subcommands for 'make story': $(filter-out $@,$(MAKECMDGOALS))"; \
		echo "Run 'make story help' for available options."; \
		exit 1; \
	fi; \
	case "$$subcommand" in \
		default) "$(MAKE)" --no-print-directory _story_all ;; \
		simpulseid) "$(MAKE)" --no-print-directory _story_simpulseid ;; \
		harbour) "$(MAKE)" --no-print-directory _story_harbour ;; \
		sign) "$(MAKE)" --no-print-directory _story_sign ;; \
		verify) "$(MAKE)" --no-print-directory _story_verify ;; \
		help) "$(MAKE)" --no-print-directory _help_story ;; \
		*) echo "ERROR: Unknown story subcommand '$$subcommand'"; echo "Run 'make story help' for available options."; exit 1 ;; \
	esac

_story_sign: ## Sign SimpulseID examples into ignored examples/signed/
	$(call check_dev_setup)
	@echo "Signing SimpulseID example storylines..."
	@rm -rf examples/signed
	@"$(PYTHON)" src/sign_examples.py
	@echo "OK: Signed example artifacts written to examples/signed/"

_story_verify: ## Verify signed SimpulseID example artifacts
	$(call check_dev_setup)
	@echo "Verifying SimpulseID signed example storylines..."
	@PYTHONPATH="$(HARBOUR_SUBMODULE_DIR)/src/python$(PYTHONPATH_SEP)$$PYTHONPATH" "$(PYTHON)" src/verify_signed_examples.py
	@echo "OK: Signed SimpulseID example artifacts verified"

_story_simpulseid: ## Generate, validate, sign, and verify SimpulseID storyline artifacts
	@echo "Running SimpulseID storyline..."
	@"$(MAKE)" --no-print-directory generate
	@"$(MAKE)" --no-print-directory validate simpulseid
	@"$(MAKE)" --no-print-directory _story_sign
	@"$(MAKE)" --no-print-directory _story_verify
	@echo "OK: SimpulseID storyline complete"

_story_harbour: ## Run the Harbour storyline inside the submodule
	@echo "Running Harbour storyline from root..."
	@"$(MAKE)" --no-print-directory -C "$(HARBOUR_SUBMODULE_DIR)" \
		story \
		VENV="$(abspath $(VENV))" \
		PYTHON="$(PYTHON_ABS)"
	@echo "OK: Harbour storyline complete"

_story_all: ## Run the full Harbour + SimpulseID storyline
	@echo "Running full repository storyline..."
	@"$(MAKE)" --no-print-directory generate
	@"$(MAKE)" --no-print-directory _story_harbour
	@"$(MAKE)" --no-print-directory _validate_simpulseid
	@"$(MAKE)" --no-print-directory _story_sign
	@"$(MAKE)" --no-print-directory _story_verify
	@echo "OK: Full repository storyline complete"

# ---------- Release Artifacts ----------

RELEASE_DIR ?= site/w3id/ascs-ev/simpulse-id

release-artifacts: ## Copy SimpulseID artifacts to w3id directory structure for GitHub Pages publishing
	@echo "Preparing w3id artifact structure..."
	@mkdir -p "$(RELEASE_DIR)/v1"
	@cp artifacts/simpulseid-core/simpulseid-core.owl.ttl "$(RELEASE_DIR)/v1/ontology.ttl"
	@cp artifacts/simpulseid-core/simpulseid-core.shacl.ttl "$(RELEASE_DIR)/v1/shapes.ttl"
	@cp artifacts/simpulseid-core/simpulseid-core.context.jsonld "$(RELEASE_DIR)/v1/context.jsonld"
	@echo "OK: Artifacts prepared in $(RELEASE_DIR)/"

# ---------- Compound targets ----------

check: generate validate ## Generate artifacts then validate examples

all: setup lint check test ## Full end-to-end: setup, lint, generate, validate, test

# ---------- Clean ----------

clean: ## Remove generated artifacts (keeps venv)
	@echo "Cleaning generated files and caches..."
	@rm -rf artifacts/simpulseid-core
	@rm -rf build/ dist/ *.egg-info/
	@rm -rf .pytest_cache/ htmlcov .coverage
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "OK: Cleaned"
