# Installation

## Prerequisites

- Python 3.10+
- Git (for submodules)

## Quick Install

```bash
# Clone with submodules
git clone --recurse-submodules https://github.com/ASCS-eV/credentials.git
cd credentials

# Create virtual environment and install
make setup
```

## Manual Installation

```bash
# Clone repository
git clone https://github.com/ASCS-eV/credentials.git
cd credentials

# Initialize submodules
git submodule update --init --recursive

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e "./submodules/harbour-credentials[dev]" \
            -e ./submodules/ontology-management-base \
            -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

## Verify Installation

```bash
# Generate artifacts
make generate

# Run validation
make validate

# Run tests
make test
```
