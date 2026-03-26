# Credentials Repository - AI Assistant Instructions

This repository contains LinkML schemas for verifiable credentials and generated ontology artifacts.

## Build, Test, and Lint Commands

**Always use `make` targets** — never call generators, linters, or test runners
directly (e.g. `gen-owl`, `gen-shacl`, `python -m`). Each repository in the
submodule chain has its own `Makefile`. Run `make help` to discover targets.

```bash
# Install dev dependencies
make setup
make install dev

# Generate artifacts from LinkML schemas
make generate

# Run validation pipeline
make validate

# Lint and format
make lint
make format

# Run tests
make test

# Run tests with coverage
pytest tests/ --cov=src --cov-report=html
```

## Instruction Files

Read these BEFORE making changes:

| Topic              | File                   |
| ------------------ | ---------------------- |
| Agent instructions | [../AGENTS.md](../AGENTS.md) |
| Claude guidance    | [../CLAUDE.md](../CLAUDE.md) |
| Documentation      | [../docs/index.md](../docs/index.md) |

## Core Principles

1. **Schema-First**: Define credential types in LinkML, then generate artifacts
2. **Validation Required**: All examples must pass SHACL validation
3. **Submodule Separation**: Signing logic in `harbour-credentials`, validation in `ontology-management-base`

## Project Structure

```text
credentials/
├── linkml/           # LinkML schema definitions (.yaml)
├── artifacts/        # Generated OWL, SHACL, JSON-LD context files
├── examples/         # Example credential instances
├── manifests/        # Wallet rendering manifests
├── src/              # Python source code
├── tests/            # Pytest tests
├── docs/             # MkDocs source pages
└── submodules/
    └── harbour-credentials/                          # Signing and verification library
        ├── submodules/ontology-management-base/     # Ontology validation pipeline
        │   └── submodules/service-characteristics/  # Gaia-X schemas
        └── submodules/w3id.org/                     # W3ID redirect rules
```

## Key Conventions

- **LinkML schemas** define credential types with proper prefixes and annotations
- **Generated artifacts** should never be edited directly — regenerate with `make generate`
- **Examples** must validate against SHACL shapes
- **Conventional commits** — `feat:`, `fix:`, `docs:`, `chore:`

## Git Commit Policy

**STRICT REQUIREMENTS:**

- ✅ **Always sign commits** with `-s -S` flags (Signed-off-by + GPG signature)
- ❌ **Never include AI attribution** — no `Co-Authored-By`, `Generated-By`, or similar headers mentioning AI assistants (Claude, Copilot, ChatGPT, etc.)
- ❌ **Never mention AI tools in commit messages** — do not reference that code was AI-generated or AI-assisted
- ✅ **Author must be the human developer** — use official company email

```bash
# Correct commit command
git commit -s -S -m "feat: add new credential type"
```

## Preparing Commits and Pull Requests

When instructed to prepare a commit or PR, default to preparing the `.playground`
files first. After **explicit human confirmation in the current session**, the
agent may directly create the signed commit, push the branch, and open the PR
using the prepared `.playground` content. Otherwise:

1. Create files in the `.playground/` directory (already in `.gitignore`)
2. Generate two markdown files:
   - `.playground/commit-message.md` — Conventional commit message(s)
   - `.playground/pr-description.md` — PR description

The human operator will review these files and either:

- Use them to manually commit/push and create a PR,
- Ask the agent to perform the signed commit/push/PR flow directly after explicit confirmation, or
- Use automated tooling with signed commits (`git commit -s -S`)

## Common Mistakes to Avoid

- ❌ **Don't edit generated files** — Regenerate with `make generate`
- ❌ **Don't call generators directly** — Always use `make` targets, never `gen-owl`/`gen-shacl`/`python -m`
- ❌ **Don't use `os.path`** — Use `pathlib.Path` instead
- ❌ **Don't forget validation** — Run `make validate` before committing
- ❌ **Don't commit without signing** — Always use `-s -S`
