# AdministratorCredential

The **AdministratorCredential** attests to a natural person with elevated permissions within the [ENVITED-X Data Space](https://staging.envited-x.net). Administrators can manage organizational credentials, approve memberships, and perform privileged operations. Issued by [ASCS e.V.](https://ascs.digital) at [identity.ascs.digital](https://identity.ascs.digital). Specified in [EVES-008 §2.2](https://github.com/ASCS-eV/EVES/blob/main/EVES/EVES-008/eves-008.md).

## Overview

- **Credential type**: `simpulseid:AdministratorCredential`
- **Subject type**: `simpulseid:Administrator`
- **Subject identifier**: `did:ethr` (on-chain DID of the person)
- **Extends**: `HarbourCredential` (harbour baseline)

## Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `harbourCredential` | URI | ✅ | IRI reference to the Harbour baseline credential |
| `givenName` | string | ✅ | First name |
| `familyName` | string | ✅ | Last name |
| `email` | string | ✅ | Email address |
| `name` | string | — | Display name |
| `memberOf` | URI[] | — | Organizations the administrator belongs to (list of DIDs) |
| `participant` | object | — | Nested Gaia-X `Participant` compliance data |

!!! note
    Unlike the [UserCredential](user.md), the AdministratorCredential requires `givenName`, `familyName`, and `email` to be present. This ensures administrators are always identifiable.

## SD-JWT-VC Claim Mapping

When issued as an SD-JWT-VC, personal data is selectively disclosable:

| Always Disclosed | Selectively Disclosed |
|------------------|-----------------------|
| `memberOf`, `harbourCredential` | `givenName`, `familyName`, `email` |

## Example

```json
{
  "@context": [
    "https://www.w3.org/ns/credentials/v2",
    "https://w3id.org/gaia-x/development#",
    "https://w3id.org/reachhaven/harbour/core/v1/",
    "https://w3id.org/reachhaven/harbour/gx/v1/",
    "https://w3id.org/ascs-ev/simpulse-id/v1/"
  ],
  "type": ["VerifiableCredential", "simpulseid:AdministratorCredential"],
  "issuer": "did:ethr:0x14a34:0x50916c8e454722d2357916d4250500102288bb03",
  "validFrom": "2025-08-06T10:15:22Z",
  "credentialSubject": {
    "id": "did:ethr:0x14a34:0xb2F78332cF29Bd4dBB04Dea2EF59439F43F0b39a",
    "type": "simpulseid:Administrator",
    "harbourCredential": "urn:uuid:b2c3d4e5-f6a7-8901-bcde-f23456789012",
    "givenName": "Andreas",
    "familyName": "Admin",
    "email": "andreas.admin@bmw.com",
    "memberOf": [
      "did:ethr:0x14a34:0x9d273DCaC2f6367968d61caf69A7E3177fd81048"
    ]
  }
}
```

## Comparison with UserCredential

The `AdministratorCredential` and [`UserCredential`](user.md) share the same field structure. The distinction is semantic — the credential type signals the holder's elevated role. Verifiers and access-control systems use the `simpulseid:AdministratorCredential` type to grant privileged access.

## Schema Definition

Defined in [`linkml/simpulseid-core.yaml`](https://github.com/ASCS-eV/credentials/blob/main/linkml/simpulseid-core.yaml) (class `SimpulseidAdministrator`) and [`linkml/simpulseid-credentials.yaml`](https://github.com/ASCS-eV/credentials/blob/main/linkml/simpulseid-credentials.yaml) (class `AdministratorCredential`).

## See Also

- [UserCredential](user.md) — Standard user variant
- [Credential Relationships](../credential-relationships.md) — Entity graph and issuance flow
- [Example: Administrator Credential](https://github.com/ASCS-eV/credentials/blob/main/examples/simpulseid-administrator-credential.json)
