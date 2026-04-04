# ParticipantCredential

The **ParticipantCredential** attests to an organization's identity within the SimpulseID ecosystem. It is the foundational credential for legal entities such as companies, research institutions, or associations.

## Overview

- **Credential type**: `simpulseid:ParticipantCredential`
- **Subject type**: `simpulseid:Participant`
- **Subject identifier**: `did:ethr` (on-chain DID of the organization)
- **Extends**: `HarbourCredential` (harbour baseline)

The subject references a Harbour Gaia-X credential via the `harbourCredential` IRI, which provides the baseline of trust including Gaia-X `LegalPerson` compliance data.

## Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `harbourCredential` | URI | ✅ | IRI reference to the Harbour Gaia-X baseline credential |
| `name` | string | — | Legal name of the organization |
| `legalForm` | enum | — | Legal form (e.g., `AG`, `GmbH`, `LLC`) |
| `duns` | string | — | DUNS number |
| `email` | string | — | Contact email |
| `url` | URI | — | Organization website |
| `participant` | object | — | Nested Gaia-X `LegalPerson` compliance data |
| `termsAndConditions` | object[] | — | Accepted terms (`gx:TermsAndConditions`) |

### Legal Form Values

The `legalForm` field accepts values from the `SimpulseIdLegalForm` enum:

`AG`, `GmbH`, `LLC`, `Corporation`, `LimitedPartnership`, `NonprofitCorporation`, `Einzelunternehmen`, `GbR`, `OHG`, `KG`, `UG`, `SoleTrader`, `UnincorporatedAssociation`, `Partnership`, `Trust`, `LimitedCompany`, `LLP`, `CIC`, `CIO`, `CooperativeSociety`, `BenCom`, `other`

## SD-JWT-VC Claim Mapping

When issued as an SD-JWT-VC, claims are mapped as follows:

| Always Disclosed | Selectively Disclosed |
|------------------|-----------------------|
| `name`, `legalForm`, `harbourCredential` | `email`, `url`, `duns` |

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
  "type": ["VerifiableCredential", "simpulseid:ParticipantCredential"],
  "issuer": "did:ethr:0x14a34:0x50916c8e454722d2357916d4250500102288bb03",
  "validFrom": "2025-08-06T10:15:22Z",
  "credentialSubject": {
    "id": "did:ethr:0x14a34:0x9d273DCaC2f6367968d61caf69A7E3177fd81048",
    "type": "simpulseid:Participant",
    "name": "Bayerische Motoren Werke Aktiengesellschaft",
    "harbourCredential": "urn:uuid:a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "legalForm": "AG",
    "duns": "313995269",
    "email": "imprint@bmw.com",
    "url": "https://www.bmwgroup.com/"
  }
}
```

## Schema Definition

Defined in [`linkml/simpulseid-core.yaml`](https://github.com/ASCS-eV/credentials/blob/main/linkml/simpulseid-core.yaml) (class `SimpulseidParticipant`) and [`linkml/simpulseid-credentials.yaml`](https://github.com/ASCS-eV/credentials/blob/main/linkml/simpulseid-credentials.yaml) (class `ParticipantCredential`).

## See Also

- [Credential Relationships](../credential-relationships.md) — Entity graph and issuance flow
- [Harbour Integration](../integration/harbour.md) — Signing with harbour-credentials
- [Example: Participant Credential](https://github.com/ASCS-eV/credentials/blob/main/examples/simpulseid-participant-credential.json)
