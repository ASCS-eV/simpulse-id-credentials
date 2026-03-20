# Credentials Documentation

Welcome to the **Credentials** repository documentation. This repository contains verifiable credential schemas and artifacts for the ENVITED-X ecosystem.

## Overview

This repository provides:

- **LinkML Schemas** — Credential type definitions in LinkML format
- **Generated Artifacts** — OWL ontologies, SHACL shapes, JSON-LD contexts
- **Example Credentials** — Sample verifiable credentials for testing
- **Validation Tools** — SHACL validation via ontology-management-base

## Quick Links

- [Installation](getting-started/installation.md)
- [Quick Start](getting-started/quickstart.md)
- [Credential Types](credentials/index.md)
- [Examples](examples/index.md)

## Credential Types

| Type | Description |
|------|-------------|
| [ParticipantCredential](credentials/participant.md) | Organization/company credentials |
| [UserCredential](credentials/user.md) | Individual user credentials |
| [AdministratorCredential](credentials/administrator.md) | Admin role credentials |
| [Membership Credentials](credentials/membership.md) | ASCS base and ENVITED membership attestations |

## Related Projects

- [harbour-credentials](https://github.com/ASCS-eV/harbour-credentials) — Cryptographic signing library
- [ontology-management-base](https://github.com/ASCS-eV/ontology-management-base) — Validation pipeline
