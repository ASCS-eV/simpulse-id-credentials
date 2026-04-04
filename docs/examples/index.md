# Examples Gallery

This page showcases example verifiable credentials from the `examples/`
directory. Each example follows the
[W3C VC Data Model v2.0](https://www.w3.org/TR/vc-data-model-2.0/)
envelope structure and conforms to the
[Credential Data Model](../reference/credential-model.md).

## Credential Examples

| File | Credential Type | Subject Type | Description |
|------|----------------|-------------|-------------|
| `simpulseid-participant-credential.json` | `ParticipantCredential` | `SimpulseidParticipant` | Organisation identity with Gaia-X compliance |
| `simpulseid-user-credential.json` | `UserCredential` | `SimpulseidUser` | Individual user with membership |
| `simpulseid-administrator-credential.json` | `AdministratorCredential` | `SimpulseidAdministrator` | Person with elevated permissions |
| `simpulseid-ascs-base-membership-credential.json` | `AscsBaseMembershipCredential` | `AscsBaseMembership` | ASCS e.V. base membership |
| `simpulseid-ascs-envited-membership-credential.json` | `AscsEnvitedMembershipCredential` | `AscsEnvitedMembership` | ENVITED membership (references base) |

### Common Envelope Structure

Every credential shares this W3C VC v2.0 envelope:

```json
{
  "@context": ["https://www.w3.org/ns/credentials/v2", "..."],
  "type": ["VerifiableCredential", "<CredentialType>"],
  "id": "urn:uuid:...",
  "issuer": "did:ethr:0x14a34:...",
  "validFrom": "2025-08-06T10:15:22Z",
  "validUntil": "2030-08-05T00:00:00Z",
  "credentialSubject": { "..." },
  "credentialStatus": { "..." },
  "evidence": [{ "..." }]
}
```

### Trust Chain in Examples

The participant credential carries a `harbourCredential` IRI that points
to the underlying Harbour Gaia-X credential (the trust anchor). The ENVITED
membership credential carries a `baseMembershipCredential` IRI that points
to the base membership credential:

```text
harbourCredential (IRI)  ←── ParticipantCredential
                               ↑ issuer DID
                         BaseMembershipCredential
                               ↑ baseMembershipCredential (IRI)
                         EnvitedMembershipCredential
```

## Signed Examples

Pre-signed JWTs are available in `examples/signed/`:

| File | Format | Algorithm |
|------|--------|-----------|
| `*.vc.jwt` | VC-JOSE-COSE | ES256 (P-256) |
| `*.sd-jwt` | SD-JWT-VC | ES256 with selective disclosure |

## Validating Examples

```bash
# Validate all examples against SHACL shapes
make validate

# Validate a specific file
python3 -m src.tools.validators.validation_suite \
  --run check-data-conformance \
  --data-paths examples/simpulseid-user-credential.json
```

!!! tip
    All example credentials use synthetic placeholder URIs for the
    `harbourCredential` field. In production, these would point to
    real Harbour Gaia-X credentials issued by the ecosystem operator.
