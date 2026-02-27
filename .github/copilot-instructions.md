# Credentials Repository - AI Assistant Instructions

This repository contains LinkML schemas for verifiable credentials and generated ontology artifacts.

## Build, Test, and Lint Commands

```bash
# Install dev dependencies
make setup
make install-dev

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

```
simpulse-id-credentials/
├── linkml/           # LinkML schema definitions (.yaml)
├── artifacts/        # Generated OWL, SHACL, JSON-LD context files
├── examples/         # Example credential instances
├── manifests/        # Wallet rendering manifests
├── src/              # Python source code
├── tests/            # Pytest tests
├── docs/             # MkDocs source pages
└── submodules/
    ├── harbour-credentials/      # Signing and verification library
    ├── ontology-management-base/ # Ontology validation pipeline
    └── w3id.org/                 # W3ID redirect rules
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

When instructed to prepare a commit or PR, **do not commit directly**. Instead:

1. Create files in the `.playground/` directory (already in `.gitignore`)
2. Generate two markdown files:
   - `.playground/commit-message.md` — Conventional commit message(s)
   - `.playground/pr-description.md` — PR description

The human operator will review these files and either:
- Use them to manually commit/push and create a PR, or
- Use automated tooling with signed commits (`git commit -s -S`)

## Common Mistakes to Avoid

- ❌ **Don't edit generated files** — Regenerate with `make generate`
- ❌ **Don't use `os.path`** — Use `pathlib.Path` instead
- ❌ **Don't forget validation** — Run `make validate` before committing
- ❌ **Don't commit without signing** — Always use `-s -S`
