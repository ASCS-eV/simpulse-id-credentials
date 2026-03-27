# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Credentials Repository** — Central repository for verifiable credential schemas and artifacts for the ENVITED-X Ecosystem. Contains LinkML schema definitions, generated OWL/SHACL/JSON-LD artifacts, and example credentials.

**Key submodules:**

- `submodules/harbour-credentials` — Cryptographic signing/verification library (Python + TypeScript)
  - `submodules/harbour-credentials/submodules/ontology-management-base` — Ontology validation pipeline (nested)
  - `submodules/harbour-credentials/submodules/w3id.org` — W3ID redirect rules (nested)
  - `submodules/harbour-credentials/submodules/ontology-management-base/submodules/service-characteristics` — Gaia-X service characteristics schemas (deeply nested)

## Essential Commands

**Always use `make` targets** — never call generators, linters, or test runners
directly (e.g. `gen-owl`, `gen-shacl`, `python -m`). Each repository in the
submodule chain has its own `Makefile` with a consistent command surface. Run
`make help` to discover available targets.

```bash
# Install dev dependencies
make setup
make install dev

# Generate artifacts from LinkML schemas
make generate                  # all domains
make generate DOMAIN=<name>    # single domain (OMB)
make generate gx               # Gaia-X from service-characteristics (OMB)

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

The `make` targets handle virtualenv activation, correct flags, line-ending
normalisation, and cross-platform path issues. Bypassing them risks producing
artifacts with wrong line endings, missing flags, or inconsistent output.

## Architecture

### Directory Structure

```text
credentials/
├── linkml/           # LinkML schema definitions (.yaml)
├── artifacts/        # Generated OWL, SHACL, JSON-LD context files
├── examples/         # Example credential instances
├── src/              # Python source code
├── tests/            # Pytest tests
├── docs/             # MkDocs documentation
├── manifests/        # Wallet rendering manifests
└── submodules/
    └── harbour-credentials/                                # Signing library
        ├── submodules/ontology-management-base/           # Validation pipeline (nested)
        │   └── submodules/service-characteristics/        # Gaia-X schemas (nested)
        └── submodules/w3id.org/                           # W3ID redirect rules (nested)
```

### LinkML Schema Pipeline

1. Define credential types in `linkml/*.yaml`
2. Run `make generate` to produce:
   - `artifacts/{domain}/{type}.owl.ttl` — OWL ontology
   - `artifacts/{domain}/{type}.shacl.ttl` — SHACL shapes
   - `artifacts/{domain}/{type}.context.jsonld` — JSON-LD context
3. Create example instances in `examples/`
4. Validate with `make validate`

## Key Imports

```python
# From harbour-credentials (after pip install -e submodules/harbour-credentials)
from harbour.keys import generate_p256_keypair, p256_public_key_to_did_key
from harbour.signer import sign_vc_jose
from harbour.verifier import verify_vc_jose
from harbour.sd_jwt import issue_sd_jwt_vc, verify_sd_jwt_vc

# From credentials modules
from src.generate_artifacts import main as generate_artifacts
```

## Coding Conventions

- **Python 3.12+** with type hints on public APIs
- **pathlib.Path** (never `os.path`)
- **4-space indentation**
- **Conventional commits** — `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:`

## Git Commit Policy

**STRICT REQUIREMENTS:**

- ✅ **Always sign commits** with `-s -S` flags (Signed-off-by + GPG signature)
- ❌ **Never include AI attribution** — no `Co-Authored-By`, `Generated-By`, or similar headers mentioning AI assistants (Claude, Copilot, ChatGPT, etc.)
- ❌ **Never mention AI tools in commit messages** — do not reference that code was AI-generated or AI-assisted
- ✅ **Author must be the human developer** with official email address

```bash
# Correct commit command
git commit -s -S -m "feat: add new credential type"
```

## Change Documentation

When making changes to the codebase, create/update these files in `.playground/` (gitignored):

| File | Purpose |
|------|---------|
| `.playground/commit-message.md` | Conventional commit message, ready for `git commit -s -S` |
| `.playground/pr-description.md` | PR description following any existing PR template |

**When instructed to prepare a commit or PR, default to updating these files first.**
After explicit human confirmation in the current session, the agent may use
them to create the signed commit, push the branch, and open the PR directly.
Otherwise, create these files for human review. The operator will either:

- Use them to manually commit/push and create a PR,
- Ask the agent to perform the signed commit/push/PR flow directly after explicit confirmation, or
- Use automated tooling with signed commits (`git commit -s -S`)

## Instruction Files

Read these before making changes:

| Topic | File |
|-------|------|
| Agent instructions | [AGENTS.md](AGENTS.md) |
| Documentation | [docs/index.md](docs/index.md) |

## Common Mistakes to Avoid

- ❌ Modifying generated files in `artifacts/` directly (regenerate with `make generate`)
- ❌ Calling generators directly (`gen-owl`, `gen-shacl`, `python -m`) — always use `make` targets
- ❌ Forgetting to update examples when changing schemas
- ❌ Using `os.path` instead of `pathlib.Path`
- ❌ Committing without signing (`-s -S`)
- ❌ Pushing without running `make test` / `make validate` locally first
- ❌ Cascading submodule pins before the inner layer's CI is green
- ❌ Accepting a solution as "done" without observing CI results

## Verification Before Push

**STRICT REQUIREMENT — never push without local verification.**

Before pushing any branch or accepting a solution as complete, the agent **must**:

1. **Run tests locally** (`make test`) in the affected repository and confirm they pass
2. **Run validation locally** (`make validate`) when schemas or artifacts changed
3. **Run lint locally** (`make lint`) to catch formatting issues
4. **Regenerate artifacts** (`make generate`) when LinkML schemas changed, and
   verify the generated output is as expected
5. **Check submodule CI** — after pushing a submodule branch, observe the CI
   pipeline (GitHub Actions / GitLab CI) and wait for it to go green before
   cascading pins to the next layer. Do **not** assume CI will pass; check it.

For the multi-layer submodule chain (service-characteristics → OMB →
harbour-credentials → credentials), this means:

- Fix and test at the **innermost** affected layer first
- Push that layer, **observe its CI**, confirm green
- Only then update the submodule pin in the next layer up
- Repeat until all layers are green

**Never skip local testing** with the assumption that CI will catch issues.
CI is a safety net, not a substitute for local verification.
