.PHONY: setup lint generate validate check test test-harbour all clean

VENV      := .venv
PYTHON    := $(VENV)/bin/python3
PIP       := $(VENV)/bin/pip
PRECOMMIT := $(VENV)/bin/pre-commit

EXAMPLES  := $(wildcard examples/*.json examples/*.jsonld)

# ---------- Setup ----------

$(VENV)/bin/activate:
	python3 -m venv $(VENV)

setup: $(VENV)/bin/activate ## Create venv, install deps, install pre-commit hooks
	$(PIP) install -e "./submodules/harbour-credentials[dev]" -e ./submodules/ontology-management-base -e ".[dev]"
	$(PRECOMMIT) install

# ---------- Lint ----------

lint: ## Run pre-commit (black, isort, flake8, JSON-LD parse, Turtle parse)
	$(PRECOMMIT) run --all-files

# ---------- Generate ----------

generate: ## Generate JSON-LD contexts, SHACL shapes, OWL ontologies from LinkML
	$(PYTHON) src/generate_from_linkml.py

# ---------- Validate ----------

validate: ## SHACL-validate all example credentials
	@if [ -z "$(EXAMPLES)" ]; then \
		echo "No example files found."; \
		exit 0; \
	fi
	$(PYTHON) -m src.tools.validators.validation_suite --run check-data-conformance \
		--path $(EXAMPLES) --no-catalog \
		|| $(VENV)/bin/onto-validate --run check-data-conformance \
			--path $(EXAMPLES) --no-catalog

# ---------- Test ----------

test-harbour: ## Run harbour-credentials JOSE tests
	cd submodules/harbour-credentials && $(abspath $(PYTHON)) -m pytest tests/ -v

test: test-harbour ## Run all tests (harbour + main repo)
	$(PYTHON) -m pytest tests/ -v

# ---------- Compound targets ----------

check: generate validate ## Generate artifacts then validate examples

all: setup lint check test ## Full end-to-end: setup, lint, generate, validate, test

# ---------- Clean ----------

clean: ## Remove generated artifacts (keeps venv)
	rm -rf artifacts/simpulseid
	rm -rf submodules/harbour-credentials/artifacts/core
	rm -rf submodules/harbour-credentials/artifacts/harbour

# ---------- Help ----------

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
