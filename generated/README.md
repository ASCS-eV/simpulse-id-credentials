# SimpulseID Generated Artefacts: Contexts & Ontologies

This folder contains the downstream artefacts (JSON-LD contexts, SHACL shapes, and RDF/OWL ontologies) generated from the LinkML schemas. These files define the formal semantics and JSON mappings for SimpulseID credentials in the ENVITED Ecosystem.

## Directory Structure

Artefacts are generated into subfolders based on their schema model:

```txt
generated/
├── simpulseid/
│   ├── simpulseid_context.jsonld
│   ├── simpulseid_ontology.ttl
│   └── simpulseid_shacl.ttl
├── harbour/
│   ├── harbour_context.jsonld
│   ├── harbour_ontology.ttl
│   └── harbour_shacl.ttl
└── core/
    ├── core_context.jsonld
    ├── core_ontology.ttl
    └── core_shacl.ttl
```

---

## 1. JSON-LD Contexts

The JSON-LD context documents define how JSON properties, classes, and identifiers in credentials are expanded into stable IRIs and how they map to the SimpulseID ontology, Gaia-X definitions, schema.org, and vCard.

All contexts are intended to be hosted under:

```txt
<https://schema.ascs.digital/name/v1>
```

with the following MIME type:

```txt
Content-Type: application/ld+json
```

Hosting contexts in this way ensures:

- OIDC4VP clients can dereference the contexts reliably.
- SSI wallets can resolve schemas consistently.
- JSON-LD processors interpret IRIs deterministically.

### `simpulseid/simpulseid_context.jsonld`

The main JSON-LD context for SimpulseID credentials. It defines all SimpulseID-specific classes and properties:

- Participant (`simpulseid:Participant`)
- ASCS Base Membership (`simpulseid:AscsBaseMembership`)
- ASCS ENVITED Membership (`simpulseid:AscsEnvitedMembership`)
- Administrator (`simpulseid:Administrator`)
- User (`simpulseid:User`)

It maps JSON fields to:

- SimpulseID ontology terms.
- Gaia-X identity primitives (`gx:LegalPerson`, `gx:Address`, `gx:VatID`, etc.).
- vCard properties for address modelling (`street-address`, `locality`, `region`).
- Legal form vocabulary entries.
- Terms & conditions references (`simpulseid:termsAndConditions`).

The context uses `@protected: true` to guarantee a stable schema.

### `harbour/harbour_context.jsonld`

Context for revocation metadata following the Harbour Status model.

Defines:

- `harbour:CRSetEntry`
- `statusPurpose` (typed as `xsd:string`)
- `harbour:VerifiableCredential`

Each SimpulseID credential uses this context in `credentialStatus`.

### `legalForm-v1.jsonld` (Vocabulary)

A SKOS vocabulary for legal forms (e.g., AG, GmbH, LLC, CIC, BenCom). Each entry is a `skos:Concept` inside the `simpulseid:LegalForm` concept scheme.

Credentials reference these IRIs like:

```txt
<https://schema.ascs.digital/SimpulseId/v1/legalForm/AG>
```

---

## 2. RDF/OWL Ontologies

The ontologies define the formal semantics for all classes and properties used in SimpulseID credentials. They provide the canonical IRIs referenced by the JSON-LD contexts and are interpreted by verifiers, wallets, and backend services.

### Purpose

The ontology defines:

- The **SimpulseID credential model** (Participant, Memberships, User, Admin).
- The **relationships** between these classes.
- Alignment with:
  - **Gaia‑X Trust Framework**
  - **schema.org**
  - **vCard**
  - **SKOS vocabularies**

By using shared IRIs and clear semantics, SimpulseID ensures interoperability across the ENVITED Ecosystem and other data spaces.

### `simpulseid/simpulseid_ontology.ttl`

Defines:

- **Classes:**
  - `simpulseid:Participant`
  - `simpulseid:AscsBaseMembership`
  - `simpulseid:AscsEnvitedMembership`
  - `simpulseid:Administrator`
  - `simpulseid:User`
- **Properties:**
  - `simpulseid:legalForm`
  - `simpulseid:termsAndConditions`
  - `simpulseid:baseMembership`
  - Address fields using Gaia‑X and vCard IRIs.
  - Organizational membership relations (`schema:memberOf`).

---

## Why Gaia-X Terms Are Used (`gx:*`)

The Gaia-X Trust Framework provides well-defined, audited semantic identifiers for legal entities, natural persons, addresses, registration numbers, and terms & conditions. SimpulseID reuses these IRIs because:

1. **Strong interoperability:** Credentials can be reused across Gaia-X–aligned ecosystems.
2. **Regulatory alignment:** Gaia-X definitions follow European governance requirements.
3. **Semantic completeness:** Classes such as `gx:LegalPerson` and `gx:VatID` match ENVITED needs.
4. **RDF correctness:** JSON-LD expansion produces a clean RDF graph aligned with the Gaia-X Credential Format.
5. **Reusability in EVES:** The ENVITED Ecosystem Specifications align with Gaia-X to avoid duplicating definitions.

## Relation between Contexts and Ontologies

- **JSON-LD Contexts** define the _mapping_ (how JSON keys become IRIs).
- **Ontologies** define the _meaning_ (relations, hierarchy, and properties of those IRIs).
- Together, they create a robust, machine‑interpretable credential model essential for trust interoperability and schema validation.
