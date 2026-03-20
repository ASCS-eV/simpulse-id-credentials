# Credential Types

This section documents the verifiable credential types defined in this repository.

## Available Types

| Credential Type | Description | Schema |
|-----------------|-------------|--------|
| [ParticipantCredential](participant.md) | Organization/company identity | `simpulseid:ParticipantCredential` |
| [UserCredential](user.md) | Individual user identity | `simpulseid:UserCredential` |
| [AdministratorCredential](administrator.md) | Admin role attestation | `simpulseid:AdministratorCredential` |
| [Membership Credentials](membership.md) | ASCS membership programs | `simpulseid:AscsBaseMembershipCredential`, `simpulseid:AscsEnvitedMembershipCredential` |

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

- `linkml/simpulseid-core.yaml` — Subject types (Participant, Administrator, User, Memberships)
- `linkml/simpulseid-credentials.yaml` — Credential type definitions (is_a: HarbourCredential)
- `linkml/importmap.json` — Import resolution for harbour-credentials and Gaia-X schemas

## Generating Artifacts

After modifying LinkML schemas, regenerate artifacts:

```bash
make generate
```
