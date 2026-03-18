# SimpulseID Credentials for the ENVITED Ecosystem

This repository contains the **Verifiable Credential (VC)** building blocks used by  
[https://identity.ascs.digital/](https://identity.ascs.digital/)  
to manage identities and memberships in the **ENVITED Ecosystem** of the  
_Automotive Solution Center for Simulation e.V. (ASCS e.V.)_.

The repository provides:

- JSON-LD **contexts** for all SimpulseID credential types
- Example **Verifiable Credentials** (VC v2, OIDC4VP-ready)
- Example **`did:ethr` DID documents** for participants, programs, users, and admins (on Base)
- **Wallet manifests** for card rendering in SSI wallets (e.g. Altme)
- RDF/OWL **ontologies** and SKOS vocabularies aligning with the Gaia-X Trust Framework and ENVITED Ecosystem Specifications (EVES)

All of this is intended to be **publicly hostable** and consumable by wallets, verifiers and services in the ENVITED ecosystem.

---

## Cloning with submodules

This repository depends on git submodules, including nested submodules pulled in
via `submodules/harbour-credentials`, so clone and update it recursively:

```bash
# First time
git clone --recurse-submodules https://github.com/ASCS-eV/credentials.git
cd credentials

# If you already cloned without submodules
git submodule update --init --recursive

# Pull all changes including nested submodules
git pull
git submodule update --init --recursive
```

---

## Development setup

Use the supported Makefile bootstrap instead of creating the virtual environment
and installing editable dependencies by hand:

```bash
# Create/update .venv, install the root package and submodule deps,
# and install the pre-commit hooks
make setup

# Optional: reinstall dev dependencies in the managed environment
make install dev

# Optional: run the hooks once across the repository
make lint
```

`make setup` already creates `.venv/`, installs `credentials`,
`harbour-credentials`, and `ontology-management-base` in editable mode, and
runs `pre-commit install`.

If you want to activate the managed environment in your shell after `make setup`,
use `.\.venv\Scripts\Activate.ps1` in Windows PowerShell, or
`source .venv/bin/activate` on macOS, Linux, and Git Bash.

---

## Generate, validate, and run the storyline

```bash
# Generate all LinkML-derived artifacts (Harbour + SimpulseID)
make generate

# Validate both Harbour and SimpulseID from the repository root
make validate

# Validate only the top-level SimpulseID examples through OMB
make validate simpulseid

# Validate only the Harbour examples through the submodule
make validate harbour

# See the available validate subcommands
make validate help

# Run the Harbour example storyline in the submodule:
# - signs the Harbour examples into ignored examples/**/signed/ folders
# - verifies the generated JWTs and evidence VPs
# - runs SHACL validation on the Harbour examples
make story harbour

# Run only the SimpulseID storyline:
# - generates artifacts
# - validates the SimpulseID examples
# - signs the SimpulseID examples into ignored examples/signed/
# - verifies the generated JWTs and evidence VPs
make story simpulseid

# Run both storylines in sequence from the root repository
make story

# See the available storyline subcommands
make story help
```

The storyline commands intentionally write signed artifacts into git-ignored
folders:

- root repo: `examples/signed/`
- Harbour submodule: `submodules/harbour-credentials/examples/signed/`
- Harbour Gaia-X examples: `submodules/harbour-credentials/examples/gaiax/signed/`

That keeps the checked-in example JSON human-readable while still giving you a
real end-to-end signing and verification run with concrete JWT outputs.

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

- `https://w3id.org/ascs-ev/simpulse-id/...`

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

#### `examples/did-ethr/`

Example **`did:ethr` DID documents** that correspond to identifiers used in the credentials.
All identities are managed on-chain via a custom ERC-1056 EthereumDIDRegistry on **Base**
(chain ID `84532` / `0x14a34` for testnet, `8453` / `0x2105` for mainnet).

These demonstrate:

- How participant and user DIDs expose their primary P-256 signing key as a
  local `#controller` `JsonWebKey`
- How optional secondary P-256 keys are exposed as `#delegate-N`
  verification methods
- How service and program DIDs are modelled as externally controlled resources
  via the root DID Core `controller` property
- How metadata endpoints are exposed as `#service-N` service entries

The examples assume a project-specific Base resolver profile: the contract state
anchors the DID, while the resolved DID document surfaces P-256 controller keys
instead of a synthetic secp256k1 recovery method.

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
- The issuer DID of the manifest (typically the ASCS `did:ethr`)

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
3. Individual administrators and users receive **Admin/User VCs**, bound to opaque `did:ethr` identifiers on Base.
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

```text

```
