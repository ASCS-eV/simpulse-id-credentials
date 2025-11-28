# JSON-LD Contexts for SimpulseID Credentials

This folder contains the JSON-LD context documents used by SimpulseID
credentials in the ENVITED Ecosystem. These contexts define how JSON properties,
classes, and identifiers in credentials are expanded into stable IRIs and how
they map to the SimpulseID ontology, Gaia-X definitions, schema.org and vCard.

All contexts in this folder are intended to be hosted under:

```txt
<https://schema.ascs.digital/name/v1>
```

with the following MIME type:

```txt
Content-Type: application/ld+json
```

Hosting contexts in this way ensures:

- OIDC4VP clients can dereference the contexts reliably
- SSI wallets can resolve schemas consistently
- JSON-LD processors interpret IRIs deterministically

---

## Included Contexts

### `SimpulseIdCredentials.json`

The main JSON-LD context.  
It defines all SimpulseID-specific classes and properties:

- Participant (`simpulseid:Participant`)
- ASCS Base Membership (`simpulseid:AscsBaseMembership`)
- ASCS ENVITED Membership (`simpulseid:AscsEnvitedMembership`)
- Administrator (`simpulseid:Administrator`)
- User (`simpulseid:User`)

It maps JSON fields to:

- SimpulseID ontology terms
- Gaia-X identity primitives (`gx:LegalPerson`, `gx:Address`, `gx:VatID`, etc.)
- vCard properties for address modelling (`street-address`, `locality`, `region`)
- Legal form vocabulary entries
- Terms & conditions references (`simpulseid:termsAndConditions`)

The context uses `@protected: true` to guarantee a stable schema.

---

### `HarbourCredentials.json`

Context for revocation metadata following the Harbour Status model.

Defines:

- `harbour:CRSetEntry`
- `statusPurpose` (typed as `xsd:string`)
- `harbour:VerifiableCredential`

Each SimpulseID credential uses this context in `credentialStatus`.

---

### `legalForm-v1.jsonld`

A SKOS vocabulary for legal forms, containing entries such as:

- AG
- GmbH
- LLC
- CIC
- BenCom
- etc.

Each entry is a `skos:Concept` inside the `simpulseid:LegalForm` concept scheme.

Credentials reference these IRIs like:

```txt
<https://schema.ascs.digital/SimpulseIdOntology/v1/legalForm#AG>
```

---

## Why Gaia-X Terms Are Used (`gx:*`)

The Gaia-X Trust Framework provides well-defined, audited semantic identifiers
for legal entities, natural persons, addresses, registration numbers and
terms & conditions.

SimpulseID reuses these Gaia-X IRIs because:

1. **Strong interoperability**  
   Credentials can be reused across Gaia-X–aligned ecosystems and data spaces.

2. **Regulatory alignment**  
   Gaia-X definitions follow European governance requirements.

3. **Semantic completeness**  
   Classes such as `gx:LegalPerson`, `gx:NaturalPerson`, `gx:Address`,
   `gx:VatID` exactly match ENVITED membership needs.

4. **RDF correctness**  
   JSON-LD expansion produces a clean RDF graph aligned with the Gaia-X
   Credential Format.

5. **Reusability in EVES**  
   The ENVITED Ecosystem Specifications intentionally align with Gaia-X, so
   reusing these IRIs avoids duplicating definitions.

---

## How These Contexts Work Together

- `SimpulseIdCredentials.json`  
  → Defines SimpulseID credential structure

- `HarbourCredentials.json`  
  → Adds revocation support fully compatible with VC Data Model v2

- `legalForm-v1.jsonld`  
  → Provides the vocabulary for legal form codes

- Gaia-X IRIs  
  → Provide standardized identity semantics

Together, they allow wallets, OIDC bridges, and verifiers to interpret
SimpulseID credentials correctly.

---

## Relation to Ontologies

These contexts directly reference terms defined in:

```txt
/ontologies/SimpulseIdOntology.ttl
```

and the legal form code list.

The ontology defines **semantics**,  
the contexts define **how JSON maps to those semantics**.

---

These context documents form the foundation for all credentials issued or
verified by **identity.ascs.digital** and the broader ENVITED Ecosystem.
