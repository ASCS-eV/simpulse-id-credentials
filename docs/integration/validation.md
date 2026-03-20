# Validation

Credentials are validated against SHACL shapes generated from the LinkML schemas. The validation pipeline uses [ontology-management-base](https://github.com/ASCS-eV/ontology-management-base) as the validation engine.

## Quick Start

Validate all example credentials:

```bash
make validate
```

Or validate specific files:

```bash
python3 -m src.tools.validators.validation_suite \
  --run check-data-conformance \
  --data-paths examples/simpulseid-participant-credential.json \
  --artifacts artifacts submodules/harbour-credentials/artifacts
```

## How It Works

The validation pipeline:

1. **Loads SHACL shapes** from artifact directories (both harbour and simpulseid)
2. **Parses credentials** as JSON-LD into RDF graphs
3. **Validates** each credential graph against the combined SHACL shapes
4. **Reports** conformance results with violation details

### Artifact Registration

Two sets of SHACL artifacts are required:

| Artifact Set | Location | Validates |
|-------------|----------|-----------|
| Harbour | `submodules/harbour-credentials/artifacts/` | Credential envelope (issuer, validFrom, evidence, etc.) |
| SimpulseID | `artifacts/simpulseid-core/` | Domain-specific subject types (Participant, User, etc.) |

Harbour shapes validate the credential structure via RDFS inference (all SimpulseID credentials extend `HarbourCredential`), while SimpulseID shapes validate the `credentialSubject` fields.

## Python API

Use the validation API directly in Python:

```python
from pathlib import Path
from src.tools.utils.registry_resolver import RegistryResolver
from src.tools.validators.shacl.validator import ShaclValidator

repo_root = Path(".")
omb_root = repo_root / "submodules" / "harbour-credentials" / "submodules" / "ontology-management-base"

# Register artifact directories
resolver = RegistryResolver(root_dir=omb_root)
resolver.register_artifact_directory(repo_root / "submodules" / "harbour-credentials" / "artifacts")
resolver.register_artifact_directory(repo_root / "artifacts")

# Validate
validator = ShaclValidator(root_dir=omb_root, verbose=False, resolver=resolver)
result = validator.validate([Path("examples/simpulseid-participant-credential.json")])

if result.conforms:
    print("✅ Valid")
else:
    print(f"❌ Violations:\n{result.report_text}")
```

## Writing Invalid Test Data

The `tests/data/invalid/` directory contains credentials with intentionally missing required fields, used to verify that SHACL shapes correctly reject malformed data:

| Test File | Missing Field |
|-----------|---------------|
| `participant-missing-harbourCredential.json` | `harbourCredential` |
| `participant-missing-issuer.json` | `issuer` |
| `participant-missing-validFrom.json` | `validFrom` |
| `user-missing-validFrom.json` | `validFrom` |
| `administrator-missing-givenName.json` | `givenName` |
| `base-membership-missing-member.json` | `member` |
| `envited-missing-baseMembershipCredential.json` | `baseMembershipCredential` |

## Interpreting Results

A validation result includes:

- **`conforms`**: `True` if the credential passes all SHACL constraints
- **`report_text`**: Human-readable violation report
- **Violation details**: Which shape was violated, on which node, and why

Common violations:

- **Missing required field**: `sh:minCount` violation — a required property is absent
- **Wrong type**: `sh:datatype` violation — value has incorrect datatype (e.g., string instead of URI)
- **Extra properties**: `sh:closed` violation — unexpected property on a closed shape

## See Also

- [Quick Start](../getting-started/quickstart.md) — End-to-end workflow including validation
- [LinkML Schemas](../reference/linkml.md) — Schema definitions that generate SHACL shapes
- [Harbour Integration](harbour.md) — Signing credentials after validation
