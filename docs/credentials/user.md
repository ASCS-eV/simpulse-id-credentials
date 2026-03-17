# UserCredential

The **UserCredential** attests to a natural person's identity within the SimpulseID ecosystem. It is used for standard users such as employees, researchers, or individual participants.

## Overview

- **Credential type**: `simpulseid:UserCredential`
- **Subject type**: `simpulseid:User`
- **Subject identifier**: `did:ethr` (on-chain DID of the person)
- **Extends**: `HarbourCredential` (harbour baseline)

## Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `harbourCredential` | URI | ✅ | IRI reference to the Harbour baseline credential |
| `givenName` | string | — | First name |
| `familyName` | string | — | Last name |
| `email` | string | — | Email address |
| `name` | string | — | Display name |
| `memberOf` | URI[] | — | Organizations the user belongs to (list of DIDs) |
| `participant` | object | — | Nested Gaia-X `Participant` compliance data |

## SD-JWT-VC Claim Mapping

When issued as an SD-JWT-VC, personal data is selectively disclosable:

| Always Disclosed | Selectively Disclosed |
|------------------|-----------------------|
| `memberOf`, `harbourCredential` | `givenName`, `familyName`, `email` |

This protects personal information while allowing verifiers to confirm organizational membership without learning the holder's identity.

## Example

```json
{
  "@context": [
    "https://www.w3.org/ns/credentials/v2",
    "https://w3id.org/gaia-x/development#",
    "https://w3id.org/reachhaven/harbour/core/v1/",
    "https://w3id.org/reachhaven/harbour/gx/v1/",
    "https://w3id.org/ascs-ev/simpulse-id/credentials/v1/"
  ],
  "type": ["VerifiableCredential", "simpulseid:UserCredential"],
  "issuer": "did:ethr:0x14a34:0x50916c8e454722d2357916d4250500102288bb03",
  "validFrom": "2025-08-06T10:15:22Z",
  "credentialSubject": {
    "id": "did:ethr:0x14a34:0x0f4Dc6903A4B92C6563DD3551421ebb7ACa7d4fC",
    "type": "simpulseid:User",
    "harbourCredential": "urn:uuid:c3d4e5f6-a7b8-9012-cdef-345678901234",
    "givenName": "Max",
    "familyName": "User",
    "email": "max.user@bmw.com",
    "memberOf": [
      "did:ethr:0x14a34:0x9d273DCaC2f6367968d61caf69A7E3177fd81048"
    ]
  }
}
```

## Comparison with AdministratorCredential

The `UserCredential` and [`AdministratorCredential`](administrator.md) share the same field structure. The distinction is semantic — an `AdministratorCredential` grants elevated permissions within the ecosystem, while a `UserCredential` represents standard access.

## Schema Definition

Defined in [`linkml/simpulseid.yaml`](https://github.com/ASCS-eV/credentials/blob/main/linkml/simpulseid.yaml) (class `SimpulseidUser`) and [`linkml/simpulseid-credentials.yaml`](https://github.com/ASCS-eV/credentials/blob/main/linkml/simpulseid-credentials.yaml) (class `UserCredential`).

## See Also

- [AdministratorCredential](administrator.md) — Elevated role variant
- [Credential Relationships](../credential-relationships.md) — Entity graph and issuance flow
- [Example: User Credential](https://github.com/ASCS-eV/credentials/blob/main/examples/simpulseid-user-credential.json)
