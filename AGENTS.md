# Repository Guidelines

## Instruction Files

Read these before making changes; they are authoritative for repo workflows.

| Topic              | File                                                               |
| ------------------ | ------------------------------------------------------------------ |
| Agent instructions | [.github/copilot-instructions.md](.github/copilot-instructions.md) |
| Documentation      | [docs/index.md](docs/index.md)                                     |

## Project Structure

- `linkml/` contains LinkML schema definitions for credential types
- `artifacts/` contains generated OWL, SHACL, and JSON-LD context files
- `examples/` contains example credential instances for testing
- `manifests/` contains wallet rendering manifests
- `src/` contains Python source code for the credentials pipeline
- `docs/` contains MkDocs source pages
- `tests/` contains pytest tests
- `submodules/` contains git submodules:
  - `harbour-credentials` — cryptographic signing/verification library
  - `ontology-management-base` — ontology validation pipeline
  - `service-characteristics` — Gaia-X service characteristics schemas
  - `w3id.org` — W3ID redirect rules

## Build, Test, and Development Commands

```bash
# Install dev dependencies
make setup
make install-dev

# Generate artifacts from LinkML schemas
make generate

# Lint and format
make lint
make format

# Run tests
make test

# Run validation pipeline
make validate
```

## Git Commit & Pull Request Policy

### Commit Requirements

- **Always sign commits** with `-s -S` flags (Signed-off-by + GPG signature)
- **Never include AI attribution** in commits — no `Co-Authored-By`, `Generated-By`, or similar headers mentioning AI assistants (Claude, Copilot, ChatGPT, etc.)
- **Never mention AI tools in commit messages** — do not reference that code was AI-generated or AI-assisted
- **Author must be a human developer** with their official email address
- **Use conventional commit format**: `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:`

```bash
# Correct commit command
git commit -s -S -m "feat: add new credential type"
```

### Preparing Commits and Pull Requests

When instructed to prepare a commit or PR, **do not commit directly**. Instead:

1. Create the `.playground/` directory (already in `.gitignore`)
2. Generate two markdown files:
   - `.playground/commit-message.md` — Conventional commit message(s)
   - `.playground/pr-description.md` — PR description following the repository's PR template

The human operator will review these files and either:
- Use them to manually commit/push and create a PR, or
- Use automated tooling with signed commits (`git commit -s -S`)

### Commit Message Format

```markdown
# .playground/commit-message.md

feat(linkml): add MembershipCredential schema

- Define membership credential with role claims
- Add selective disclosure annotations
- Include example instance

Refs: #123
```

### PR Description Format

Follow `.github/pull_request_template.md` if it exists, otherwise use:

```markdown
# .playground/pr-description.md

## Summary

Brief description of the changes.

## Changes

- List of specific changes made
- Another change

## Testing

- [ ] Tests pass locally (`make test`)
- [ ] Validation passes (`make validate`)

## Related Issues

Closes #123
```

## Coding Style

- Python 3.10+ with type hints
- Use `pathlib.Path` (not `os.path`)
- 4-space indentation
- Module docstrings required
- Run `make lint` before committing
