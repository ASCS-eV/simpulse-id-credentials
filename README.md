# SimpulseID Credentials for the ENVITED Ecosystem

This repository contains the **Verifiable Credential (VC)** building blocks used by  
[https://identity.ascs.digital/](https://identity.ascs.digital/)  
to manage identities and memberships in the **ENVITED Ecosystem** of the  
_Automotive Solution Center for Simulation e.V. (ASCS e.V.)_.

The repository provides:

- JSON-LD **contexts** for all SimpulseID credential types
- Example **Verifiable Credentials** (VC v2, OIDC4VP-ready)
- Example **did:web** DID documents for participants, programs, users, and admins
- **Wallet manifests** for card rendering in SSI wallets (e.g. Altme)
- RDF/OWL **ontologies** and SKOS vocabularies aligning with the Gaia-X Trust Framework and ENVITED Ecosystem Specifications (EVES)

All of this is intended to be **publicly hostable** and consumable by wallets, verifiers and services in the ENVITED ecosystem.

---

## Repository structure

### `contexts/`

JSON-LD context documents used by SimpulseID credentials, for example:

- `SimpulseIdCredentials.json` – main context for:
  - `simpulseid:Participant`
  - `simpulseid:AscsBaseMembership`
  - `simpulseid:AscsEnvitedMembership`
  - `simpulseid:Administrator`
  - `simpulseid:User`
- `HarbourCredentials.json` – additional context for status / revocation information
- SKOS / code list contexts (e.g. legal form vocabulary)

These files are meant to be hosted under:

- `https://schema.ascs.digital/...`

and are referenced from the example credentials via their `@context` arrays.

---

### `examples/`

Example **Verifiable Credentials** that show how the contexts and ontologies are intended to be used.

Typical credential subjects include:

- **Participant** – organizational identity (e.g. BMW)
- **ASCS Base Membership** – base membership in ASCS e.V.
- **ASCS ENVITED Membership** – ENVITED program membership, linked to base membership
- **Administrator** – natural person with administrative rights in ENVITED / ASCS
- **User** – natural person with initial roles/rights in ENVITED ecosystem applications

Each VC uses:

- `https://www.w3.org/ns/credentials/v2` (VC Data Model v2)
- SimpulseID context from this repo
- Harbour context for `credentialStatus`
- `harbour:CRSetEntry` + `statusPurpose: "revocation"` for revocation status
- `gx:*` terms to stay compatible with the **Gaia-X Credential Format** and Trust Framework

#### `examples/did-web/`

Example **did:web DID documents** that correspond to identifiers used in the credentials, e.g.:

- Participants (`did:web:did.identity.ascs.digital:participants:...`)
- Programs (`did:web:did.identity.ascs.digital:programs:...`)
- Users & administrators (`did:web:did.identity.ascs.digital:users:...`)

These demonstrate:

- How organizational DIDs (ASCS, ENVITED programs, participants) are modelled
- How user/admin DIDs are defined _without leaking personal data_
- How to support key rotation and multiple chains (e.g. Tezos + Etherlink/EVM) via `blockchainAccountId`

In production, these DID documents are intended to be hosted under:

- `https://did.identity.ascs.digital/...`

---

### `manifests/`

Wallet **rendering manifests** for each credential type, following the  
[Decentralized Identity Foundation Wallet Rendering specification](https://identity.foundation/wallet-rendering/).

They are used by wallets like **Altme** to:

- Render credential “cards” with titles, subtitles and key properties
- Show important fields such as:
  - organization name, legal form, VAT ID
  - membership program and hosting organization
  - user/admin name, email, affiliation
  - links to terms & conditions and privacy policies
- Map `credentialSubject` properties and dates (`issuanceDate`, `expirationDate`) to UI elements

Each manifest references:

- A SimpulseID schema / type (e.g. `simpulseid:Participant`)
- The issuer DID of the manifest (typically an ASCS did:web)

---

### `ontologies/`

RDF/OWL ontologies and vocabularies that define the **formal semantics** of SimpulseID types and properties, aligned with:

- **Gaia-X Trust Framework 24.11**
- **ENVITED Ecosystem Specifications (EVES)**
- **schema.org** and **vCard** where appropriate

Key elements include:

- `SimpulseIdOntology.ttl`

  - Classes:
    - `simpulseid:Participant` ⊑ `gx:LegalPerson`, `schema:Organization`
    - `simpulseid:AscsBaseMembership`, `simpulseid:AscsEnvitedMembership` ⊑ `schema:ProgramMembership`
    - `simpulseid:Administrator`, `simpulseid:User` ⊑ `gx:NaturalPerson`, `schema:Person`
    - Program classes for base and ENVITED memberships
  - Properties:
    - `simpulseid:legalForm` → SKOS `simpulseid:LegalForm` concepts
    - `simpulseid:termsAndConditions` → `gx:TermsAndConditions` resources
    - `simpulseid:baseMembership` linking ENVITED membership to base membership
  - Address modelling:
    - `gx:Address` with **vCard** properties:
      - `vcard:street-address`
      - `vcard:postal-code`
      - `vcard:locality`
      - `vcard:region`
    - `gx:countryCode` for ISO country codes

- Legal form SKOS vocabulary (e.g. `legalForm-v1.jsonld`)
  - Code list of legal forms (`AG`, `GmbH`, `LLC`, `BenCom`, etc.)
  - Used via `simpulseid:LegalForm` and `simpulseid:legalForm` in credentials

These ontologies are the **ground truth** for what the JSON-LD contexts and examples mean at RDF level.

---

## Intended usage within `https://identity.ascs.digital/`

The artifacts in this repository are used by the **ENVITED Ecosystem identity services** to:

- Issue and verify **Gaia-X compatible** Verifiable Credentials
- Support **self-sovereign identity** login flows via the **SSI-to-OIDC bridge**
- Provide consistent semantics for:
  - ENVITED participants (organizations)
  - ASCS base memberships
  - ENVITED program memberships
  - Administrative and user roles
- Render credential cards in SSI wallets for a smooth UX

Typical flow:

1. A participant (organization) is onboarded and receives a **Participant VC**.
2. The organization receives **ASCS base membership** and optionally **ENVITED membership** credentials.
3. Individual administrators and users receive **Admin/User VCs**, bound to opaque did:web identifiers under `did.identity.ascs.digital`.
4. Wallets like Altme use the **contexts** and **manifests** from this repo to display these credentials.
5. Services behind `identity.ascs.digital` use the **ontologies** and **Gaia-X compatible structures** to perform trust and membership checks.

---

## References

Some relevant specifications and resources:

- W3C Verifiable Credentials Data Model v2  
  <https://www.w3.org/TR/vc-data-model-2.0/>
- W3C Verifiable Credential Vocabulary (VC v2)  
  <https://www.w3.org/ns/credentials/v2>
- Gaia-X Credential Format & Trust Framework (24.11)  
  <https://docs.gaia-x.eu/technical-committee/identity-credential-access-management/>
- DIF Wallet Rendering specification  
  <https://identity.foundation/wallet-rendering/>
- JSON-LD 1.1 & best practices  
  <https://json-ld.org/>  
  <https://w3c.github.io/json-ld-bp/>
- JSON Schema  
  <https://json-schema.org/specification>
- schema.org  
  <https://schema.org/>
