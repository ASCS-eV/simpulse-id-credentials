# SimpulseID Credentials

SimpulseID is the credential and identity framework for the **ENVITED-X Data Space**, operated by the [Automotive Solution Center for Simulation e.V. (ASCS e.V.)](https://ascs.digital). It is deployed at [identity.ascs.digital](https://identity.ascs.digital).

SimpulseID enables verifiable onboarding of organizations and users, program membership verification, and secure authentication across ENVITED-X services using W3C Verifiable Credentials v2 and `did:ethr` identifiers.

## Architecture

SimpulseID is built as a **domain layer on top of [harbour-credentials](https://github.com/reachhaven/harbour-credentials)** (by [Haven](https://www.reachhaven.com)). Harbour provides the ecosystem-agnostic cryptographic infrastructure (signing, verification, SD-JWT, delegation), while SimpulseID adds ENVITED-specific credential types, membership chains, and Gaia-X Trust Framework alignment.

```text
+------------------------------------------------------+
|  SimpulseID (this repo)                              |
|  - 5 credential types + subject schemas              |
|  - Membership chains, program metadata               |
|  - ENVITED-X governance (ASCS e.V.)                  |
+------------------------------------------------------+
|  Harbour Credentials (submodule)                     |
|  - W3C VC v2 base types (HarbourCredential, CRSet)   |
|  - Gaia-X LegalPerson / NaturalPerson composition    |
|  - JOSE signing, SD-JWT-VC, delegation evidence      |
|  - did:ethr key management                           |
+------------------------------------------------------+
```

Each SimpulseID credential subject carries a mandatory `harbourCredential` IRI linking to a Harbour Gaia-X compliance credential, which serves as the baseline of trust.

## Specifications

This repository is the reference implementation of two ENVITED-X Ecosystem Specifications (EVES):

- **[EVES-008](https://github.com/ASCS-eV/EVES/blob/main/EVES/EVES-008/eves-008.md)** --- SimpulseID Credential and Identity Framework
- **[EVES-009](https://github.com/ASCS-eV/EVES/blob/main/EVES/EVES-009/eves-009.md)** --- Evidence-Based Consent Using Verifiable Presentations

See the [Specifications](specifications.md) page for details and external standards.

## Credential Types

All credentials are issued by ASCS e.V. as the trust anchor for the ENVITED-X Data Space.

| Type | Description | Issuer |
|------|-------------|--------|
| [ParticipantCredential](credentials/participant.md) | Organization identity (gx:LegalPerson) | ASCS e.V. |
| [AdministratorCredential](credentials/administrator.md) | Elevated-permission natural person | ASCS e.V. |
| [UserCredential](credentials/user.md) | Standard natural person | ASCS e.V. |
| [Base Membership](credentials/membership.md) | ASCS e.V. base membership | ASCS e.V. |
| [ENVITED Membership](credentials/membership.md) | ENVITED research cluster membership | ASCS e.V. |

## Quick Links

- [Installation](getting-started/installation.md)
- [Quick Start](getting-started/quickstart.md)
- [Credential Relationships](credential-relationships.md)
- [Examples](examples/index.md)
- [Specifications](specifications.md)

## Related Projects

- [harbour-credentials](https://github.com/reachhaven/harbour-credentials) --- Cryptographic signing library (by Haven)
- [ontology-management-base](https://github.com/ASCS-eV/ontology-management-base) --- SHACL validation pipeline
- [EVES](https://github.com/ASCS-eV/EVES) --- ENVITED-X Ecosystem Specifications
