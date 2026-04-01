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
    - `harbour-credentials/submodules/ontology-management-base` — ontology validation pipeline
    - `harbour-credentials/submodules/w3id.org` — W3ID redirect rules

## Build, Test, and Development Commands

**Always use `make` targets** — never call generators, linters, or test runners
directly. Each repository in the submodule chain has its own `Makefile` with a
consistent command surface. Run `make help` to discover available targets.

```bash
# Install dev dependencies
make setup
make install dev

# Generate artifacts from LinkML schemas
make generate                  # all domains
make generate DOMAIN=<name>    # single domain (OMB)
make generate gx               # Gaia-X from service-characteristics (OMB)

# Lint and format
make lint
make format

# Run tests
make test

# Run validation pipeline
make validate
```

The `make` targets handle virtualenv activation, correct flags, line-ending
normalisation, and cross-platform path issues. Bypassing them (e.g. calling
`gen-owl` or `python -m` directly) risks producing artifacts with wrong
line endings, missing flags, or inconsistent output.

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

When instructed to prepare a commit or PR, default to preparing the `.playground`
files first. After **explicit human confirmation in the current session**, the
agent may directly create the signed commit, push the branch, and open the PR
using the prepared `.playground` content. Otherwise:

1. Create the `.playground/` directory (already in `.gitignore`)
2. Generate two markdown files:
   - `.playground/commit-message.md` — Conventional commit message(s)
   - `.playground/pr-description.md` — PR description following the repository's PR template

The human operator will review these files and either:

- Use them to manually commit/push and create a PR,
- Ask the agent to perform the signed commit/push/PR flow directly after explicit confirmation, or
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

## Verification Before Push

**STRICT REQUIREMENT — never push without local verification.**

Before pushing any branch or accepting a solution as complete, the agent **must**:

1. **Run tests locally** (`make test`) in the affected repository and confirm they pass
2. **Run validation locally** (`make validate`) when schemas or artifacts changed
3. **Run lint locally** (`make lint`) to catch formatting issues
4. **Regenerate artifacts** (`make generate`) when LinkML schemas changed, and
   verify the generated output is as expected
5. **Run GitLab CI locally** when changing `.gitlab-ci.yml` or CI-related files
   in `service-characteristics`:

   ```bash
   # Requires: npm install -g gitlab-ci-local
   # Requires: rsync (via msys2: pacman -S rsync, or apt: apt install rsync)
   # Requires: Docker/Podman for container-based jobs
   gitlab-ci-local                    # run all jobs
   gitlab-ci-local --job test-shacl   # run a single job
   gitlab-ci-local --list             # list available jobs
   ```

   Note: On corporate networks, Docker image pulls may require proxy
   configuration. If `gitlab-ci-local` cannot pull images, verify the CI
   changes are correct by inspection and note the limitation in the PR.
6. **Check submodule CI** — after pushing a submodule branch, observe the CI
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

## Standards Compliance

**STRICT REQUIREMENT — all schemas, examples, and models must align with the
relevant W3C, IETF, and industry specifications.**

When defining or modifying LinkML schemas, JSON-LD examples, or DID documents:

1. **Cross-reference the spec copy in `docs/`.**  The LinkML schema files use
   bracketed tags (e.g. `[VCDM2]`, `[DID Core]`, `[OID4VP]`, `[SD-JWT]`) that
   cite specific spec sections.  Before changing a slot range, class hierarchy,
   or property definition, locate the corresponding spec document in `docs/`
   and verify the modeling choice against the normative text.
2. **Document the rationale in the schema.**  Every non-trivial modeling
   decision must have a YAML comment citing the spec section and briefly
   explaining *why* the chosen type/range/constraint is correct.  Example:

   ```yaml
   # [DID Core] §5.4 — serviceEndpoint is a URI, map, or set thereof.
   # Base range is uri (the common case); service-specific classes
   # override via slot_usage for structured endpoint objects.
   serviceEndpoint:
     slot_uri: didcore:serviceEndpoint
     range: uri
   ```

3. **Use standard vocabulary** (DID Core, VC Data Model 2.0, OID4VP, schema.org,
   Gaia-X Trust Framework) rather than inventing new terms.
4. **Never use `range: Any`** in LinkML slot definitions.  `linkml:Any` produces
   `rdfs:range linkml:Any` in OWL, which triggers closed-shape SHACL violations
   during RDFS inference.  Always choose a spec-aligned range:
   - `uri` for properties whose values are network addresses or identifiers
     (e.g. DID Core `serviceEndpoint`)
   - A named class for structured objects with a defined schema
     (e.g. OID4VP `TransactionData`)
5. **Validate examples against SHACL** (`make validate`) to catch inference
   issues before they reach CI.

| Spec area          | Key reference                                |
| ------------------ | -------------------------------------------- |
| DID documents      | W3C DID Core 1.1 (`docs/`)                   |
| Credentials        | W3C VC Data Model 2.0 (`docs/`)              |
| Delegated signing  | OID4VP 1.0 §8.4 (`docs/`)                    |
| Gaia-X compliance  | Gaia-X Trust Framework (`docs/`)             |
| Schema vocabulary  | schema.org (`imports/schema/`)               |

## Coding Style

- Python 3.12+ with type hints
- Use `pathlib.Path` (not `os.path`)
- 4-space indentation
- Module docstrings required
- Run `make lint` before committing
