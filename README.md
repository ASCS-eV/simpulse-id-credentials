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

## Cloning with submodules

The repository depends on the follwing submodules:

```markdown
Root Project
├── Submodule A
│ └── Submodule B (Nested inside A)
└── Submodule C
```

````bash
# First time
git clone --recurse-submodules git@github.com:ASCS-eV/credentials.git
# Initialize after already having cloned
git submodule update --init --recursive
# Pull all changes also from submodules
git pull --recurse-submodules
```

---

## Installation

If you want to use the validation scripts from 📁 `ontology-management-base/src` then you need to isntall the following dependencies:

```bash
# On Windows use python instead of python3
sudo apt-get install python3-full

# 1. Create and activate a virtual environment
python3 -m venv .venv/
source .venv/bin/activate  # On Windows use: source .venv/Scripts/activate

# 2. Install dependencies (Submodule + Main Project + Dev Tools)
# This reads both pyproject.toml files and handles all versions automatically.
python3 -m pip install -e ./ontology-management-base -e ".[dev]"

# 3. Generate ontologies, SHACL shapes and Contexts from LinkML models
# We generate artifacts for core, harbour, and simpulseid so they are available in generated/
python3 src/generate_from_linkml.py  # Auto-discovers *.yaml in linkml/
#python3 src/generate_from_linkml.py --model linkml/core.yaml --model linkml/harbour.yaml --model linkml/simpulseid.yaml

# 4. Example check
# The script now automatically finds the 'generated/' folder and 'ontology-management-base/' submodule
python3 ontology-management-base/src/check_jsonld_against_shacl_schema.py examples/simpulseid-administrator-credential.json
```

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

- `https://www.w3.org/2018/credentials#` (VC Data Model v2)
- SimpulseID context from this repo
- Harbour context for `credentialStatus`
- `harbour:CRSetEntry` + `statusPurpose: "revocation"` for revocation status
- `gx:*` terms to stay compatible with the **Gaia-X Credential Format** and Trust Framework

#### `examples/did-web/`

Example **did:web DID documents** that correspond to identifiers used in the credentials, e.g.:

- Participants (`did:web:did.ascs.digital:participants:...`)
- Programs (`did:web:did.ascs.digital:programs:...`)
- Users & administrators (`did:web:did.ascs.digital:users:...`)
- Services (`did:web:did.ascs.digital:services:...`)

These demonstrate:

- How organizational DIDs (ASCS, ENVITED programs, participants) are modelled
- How user/admin DIDs are defined _without leaking personal data_
- How to support key rotation and multiple chains (e.g. Tezos + Etherlink/EVM) via `blockchainAccountId`

In production, these DID documents are intended to be hosted under:

- `https://did.ascs.digital/...`

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
3. Individual administrators and users receive **Admin/User VCs**, bound to opaque did:web identifiers under `did.ascs.digital`.
4. Wallets like Altme use the **contexts** and **manifests** from this repo to display these credentials.
5. Services behind `identity.ascs.digital` use the **ontologies** and **Gaia-X compatible structures** to perform trust and membership checks.

---

## References

Some relevant specifications and resources:

- W3C Verifiable Credentials Data Model v2
  <https://www.w3.org/TR/vc-data-model-2.0/>
- W3C Verifiable Credential Vocabulary (VC v2)
  <https://www.w3.org/2018/credentials#>
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
````
