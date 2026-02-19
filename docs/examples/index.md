# Examples Gallery

This page showcases example verifiable credentials from the `examples/` directory.

## Available Examples

| File | Type | Description |
|------|------|-------------|
| `simpulseid-participant-credential.json` | ParticipantCredential | Organization identity |
| `simpulseid-user-credential.json` | UserCredential | Individual user |
| `simpulseid-administrator-credential.json` | AdministratorCredential | Admin role |
| `simpulseid-base-membership-credential.json` | BaseMembershipCredential | Basic membership |
| `simpulseid-ascs-envited-membership-credential.json` | EnvitedMembershipCredential | ENVITED membership |

## Signed Examples

Pre-signed JWTs are available in `examples/signed/`:

| File | Format | Algorithm |
|------|--------|-----------|
| `*.vc.jwt` | VC-JOSE-COSE | ES256 (P-256) |
| `*.sd-jwt` | SD-JWT-VC | ES256 with selective disclosure |

## Validating Examples

```bash
# Validate all examples
make validate

# Validate specific file
python3 -m src.tools.validators.validation_suite \
  --run check-data-conformance \
  --data-paths examples/simpulseid-user-credential.json
```
