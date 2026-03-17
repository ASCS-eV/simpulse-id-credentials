# Installation

## Prerequisites

- Python 3.10+
- Git (for submodules)

## Quick Install

```bash
# Clone with submodules
git clone --recurse-submodules https://github.com/ASCS-eV/credentials.git
cd credentials

# Create/update .venv, install the root package and submodule deps,
# and install the pre-commit hooks
make setup
```

## Update an Existing Checkout

```bash
# Refresh nested submodules after pulling
git pull
git submodule update --init --recursive
```

## What `make setup` Does

- Creates `.venv/` if needed
- Installs `credentials`, `harbour-credentials`, and `ontology-management-base`
  in editable mode with development dependencies
- Installs the local `pre-commit` hooks

## Verify Installation

```bash
# Reinstall development dependencies if needed
make install dev

# Generate artifacts
make generate

# Run validation
make validate

# Run tests
make test
```
