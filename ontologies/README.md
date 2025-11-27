# SimpulseID Ontologies

This folder contains the RDF/OWL ontologies that define the formal semantics
for all classes and properties used in SimpulseID credentials. These ontologies
provide the canonical IRIs that are referenced by the JSON-LD contexts in
`../contexts` and interpreted by verifiers, wallets, and backend services.

## Purpose

The ontology defines:

- The **SimpulseID credential model** (Participant, Memberships, User, Admin)
- The **relationships** between these classes
- Alignment with:
  - **Gaia‑X Trust Framework**
  - **schema.org**
  - **vCard**
  - **SKOS vocabularies** (e.g., legal form code list)

By using shared IRIs and clear semantics, SimpulseID ensures interoperability
across the ENVITED Ecosystem and other data spaces.

## Files

### `SimpulseIdOntology.ttl`

Defines:

- Classes:

  - `simpulseid:Participant`
  - `simpulseid:AscsBaseMembership`
  - `simpulseid:AscsEnvitedMembership`
  - `simpulseid:Administrator`
  - `simpulseid:User`
  - Program classes for Base and ENVITED memberships

- Properties:
  - `simpulseid:legalForm`
  - `simpulseid:termsAndConditions`
  - `simpulseid:baseMembership`
  - Address fields using Gaia‑X and vCard IRIs
  - Organizational membership relations (`schema:memberOf`)

### Legal Form Vocabulary

The ontology references the SKOS vocabulary defined in:

```txt
../contexts/legalForm-v1.jsonld
```

This vocabulary provides IRIs for legal forms (AG, GmbH, LLC, CIC, etc.).

## Why Ontologies Matter

- JSON-LD contexts define _mapping_
- Ontologies define _meaning_
- Together, they create a robust, machine‑interpretable credential model

These ontologies are essential for:

- Trust interoperability
- Schema validation
- EVES compliance
- Gaia‑X compatibility
