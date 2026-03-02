# Credential Types

This section documents the verifiable credential types defined in this repository.

## Available Types

| Credential Type | Description | Schema |
|-----------------|-------------|--------|
| [ParticipantCredential](participant.md) | Organization/company identity | `simpulseid:ParticipantCredential` |
| [UserCredential](user.md) | Individual user identity | `simpulseid:UserCredential` |
| [AdministratorCredential](administrator.md) | Admin role attestation | `simpulseid:AdministratorCredential` |
| [MembershipCredential](membership.md) | Membership in organization | `simpulseid:MembershipCredential` |

## Schema Structure

All credentials follow the W3C Verifiable Credentials Data Model v2.0:

```json
{
  "@context": [
    "https://www.w3.org/ns/credentials/v2",
    "<domain-context>"
  ],
  "type": ["VerifiableCredential", "<credential-type>"],
  "issuer": "<did>",
  "validFrom": "<iso-datetime>",
  "credentialSubject": {
    "id": "<subject-did>",
    // type-specific claims
  }
}
```

## LinkML Definitions

Credential types are defined in LinkML YAML files under `linkml/`:

- `linkml/simpulseid.yaml` — Main schema with credential classes
- `linkml/harbour-core-credential.yaml` — Harbour core types (imported via `importmap.json`)

## Generating Artifacts

After modifying LinkML schemas, regenerate artifacts:

```bash
make generate
```
