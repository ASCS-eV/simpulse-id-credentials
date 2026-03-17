# Membership Credentials

Membership credentials attest to an organization's participation in ASCS e.V. programs. Two credential types form a hierarchical structure: a **base membership** is required before an **ENVITED membership** can be issued.

## Credential Types

| Credential Type | Subject Type | Description |
|-----------------|--------------|-------------|
| `simpulseid:AscsBaseMembershipCredential` | `simpulseid:AscsBaseMembership` | ASCS e.V. base membership |
| `simpulseid:AscsEnvitedMembershipCredential` | `simpulseid:AscsEnvitedMembership` | ASCS e.V. ENVITED program membership |

Both extend `HarbourCredential` and use `urn:uuid:` identifiers for the credential subject (not DIDs), because membership records are issuer-managed rather than self-sovereign.

## Base Membership

The `AscsBaseMembershipCredential` attests that an organization is a member of ASCS e.V.

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `member` | URI | ✅ | DID of the member organization |
| `programName` | string | — | Name of the membership program |
| `hostingOrganization` | URI | — | DID of the hosting organization (ASCS e.V.) |
| `memberSince` | date | — | Date membership was granted |

### Example

```json
{
  "@context": [
    "https://www.w3.org/ns/credentials/v2",
    "https://w3id.org/gaia-x/development#",
    "https://w3id.org/reachhaven/harbour/core/v1/",
    "https://w3id.org/reachhaven/harbour/gx/v1/",
    "https://w3id.org/ascs-ev/simpulse-id/credentials/v1/"
  ],
  "type": ["VerifiableCredential", "simpulseid:AscsBaseMembershipCredential"],
  "issuer": "did:ethr:0x14a34:0x50916c8e454722d2357916d4250500102288bb03",
  "validFrom": "2025-08-06T10:15:22Z",
  "credentialSubject": {
    "id": "urn:uuid:22423d4a-4281-4251-b1e4-1afaa96f1a15",
    "type": "simpulseid:AscsBaseMembership",
    "member": "did:ethr:0x14a34:0x9d273DCaC2f6367968d61caf69A7E3177fd81048",
    "programName": "ASCS e.V. Base Membership",
    "hostingOrganization": "did:ethr:0x14a34:0x50916c8e454722d2357916d4250500102288bb03",
    "memberSince": "2023-01-01"
  }
}
```

## ENVITED Membership

The `AscsEnvitedMembershipCredential` attests to participation in the ENVITED program. It **requires a reference** to an existing base membership credential.

### Additional Fields

In addition to all base membership fields:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `baseMembershipCredential` | URI | ✅ | IRI of the prerequisite `AscsBaseMembershipCredential` |

### Example

```json
{
  "@context": [
    "https://www.w3.org/ns/credentials/v2",
    "https://w3id.org/gaia-x/development#",
    "https://w3id.org/reachhaven/harbour/core/v1/",
    "https://w3id.org/reachhaven/harbour/gx/v1/",
    "https://w3id.org/ascs-ev/simpulse-id/credentials/v1/"
  ],
  "type": ["VerifiableCredential", "simpulseid:AscsEnvitedMembershipCredential"],
  "issuer": "did:ethr:0x14a34:0x50916c8e454722d2357916d4250500102288bb03",
  "validFrom": "2025-08-06T10:15:22Z",
  "credentialSubject": {
    "id": "urn:uuid:bac22d92-7de7-40e8-b887-d9daf00208a2",
    "type": "simpulseid:AscsEnvitedMembership",
    "member": "did:ethr:0x14a34:0x9d273DCaC2f6367968d61caf69A7E3177fd81048",
    "programName": "ASCS e.V. ENVITED Membership",
    "hostingOrganization": "did:ethr:0x14a34:0x50916c8e454722d2357916d4250500102288bb03",
    "memberSince": "2023-01-01",
    "baseMembershipCredential": "urn:uuid:7f3f7c6a-4b4d-4e9e-8f0a-9b1b2c3d4e5f"
  }
}
```

## SD-JWT-VC Claim Mapping

### Base Membership

| Always Disclosed | Selectively Disclosed |
|------------------|-----------------------|
| `member`, `programName` | `memberSince`, `hostingOrganization` |

### ENVITED Membership

| Always Disclosed | Selectively Disclosed |
|------------------|-----------------------|
| `member`, `programName`, `baseMembershipCredential` | `memberSince`, `hostingOrganization` |

## Issuance Flow

```mermaid
flowchart LR
    A[ParticipantCredential] -->|prerequisite| B[AscsBaseMembershipCredential]
    B -->|referenced by| C[AscsEnvitedMembershipCredential]
```

1. The organization must hold a `ParticipantCredential`
2. ASCS e.V. issues an `AscsBaseMembershipCredential` (the `member` field references the organization's DID)
3. ASCS e.V. issues an `AscsEnvitedMembershipCredential` that references the base membership via `baseMembershipCredential`

## Schema Definition

Defined in [`linkml/simpulseid.yaml`](https://github.com/ASCS-eV/credentials/blob/main/linkml/simpulseid.yaml) (classes `AscsBaseMembership`, `AscsEnvitedMembership`) and [`linkml/simpulseid-credentials.yaml`](https://github.com/ASCS-eV/credentials/blob/main/linkml/simpulseid-credentials.yaml) (classes `AscsBaseMembershipCredential`, `AscsEnvitedMembershipCredential`).

## See Also

- [Credential Relationships](../credential-relationships.md) — Full entity graph and member vs memberOf semantics
- [ParticipantCredential](participant.md) — Prerequisite for membership
