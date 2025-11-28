# SimpulseID Credential Examples

This folder contains **reference examples** for all Verifiable Credentials used in the  
ENVITED Ecosystem operated by ASCS e.V.

These examples demonstrate:

- the JSON-LD structure using the public contexts in `/contexts`
- the semantics defined in `/ontologies`
- correct use of did:web identifiers for:
  - participants (organizations)
  - ASCS programs (base membership, ENVITED membership)
  - users and administrators (opaque non-PII identifiers)
- correct Gaia-X–compatible modelling of addresses, legal forms, and terms & conditions
- revocation status entries using the Harbour Credentials context

The examples serve as a canonical blueprint for services integrating with  
**<https://identity.ascs.digital/>**.

---

## Structure of the Examples

### 1. Verifiable Credentials

Each credential in this folder uses:

- `https://www.w3.org/ns/credentials/v2` (VC Data Model v2)
- `SimpulseIdCredentials.json` (main context)
- `HarbourCredentials.json` (credential status)
- `harbour:CRSetEntry` with `statusPurpose: "revocation"`

Types included:

- **Participant Credential**  
  Identity of an organization (e.g., BMW), aligned with Gaia-X `gx:LegalPerson`.

- **ASCS Base Membership Credential**  
  Proof of base membership in ASCS e.V.

- **ENVITED Membership Credential**  
  Extends the base membership and links to a program DID.

- **Administrator Credential**  
  Natural person with elevated rights, issued and controlled by ASCS.

- **User Credential**  
  Natural person affiliated with a participant, issued by the participant’s admin.

All credentials use **did:web subject identifiers** for users and admins:

- opaque  
- non-PII  
- key-rotation capable  
- hosted under:  
  `https://did.identity.ascs.digital/users/...`

---

## 2. did:web Documents

Examples under `examples/did-web/` illustrate:

- Participant DIDs controlled by organizations  
  (`did:web:did.identity.ascs.digital:participants:ascs`, `participants:bmw`, …)

- Program DIDs controlled by ASCS  
  (`did:web:did.identity.ascs.digital:programs:ascs-base-membership`, …)

- User and Administrator DIDs:  
  Opaque, privacy-preserving identifiers that *only* expose verification keys.

Each DID document supports:

- Tezos account (did:pkh)
- Etherlink/EVM account (`blockchainAccountId: eip155:42793:...`)
- Key rotation (through verificationMethod lists)

No DID document contains personal data.

---

## 3. Wallet Rendering Manifests

The manifests in `/manifests` define how SSI wallets such as **Altme** render cards using the  
Decentralized Identity Foundation **Wallet Rendering Specification**.

Each manifest:

- references the correct SimpulseID credential type  
- defines which properties appear on the card  
- includes human-readable fallback titles  
- is issued by the ASCS organizational DID (`did:web:did.identity.ascs.digital:participants:ascs`)

---

## 4. Notes on Issuance Model

### Participant Credentials  

Issued by ASCS upon onboarding of an organization into the ENVITED ecosystem.

### Program Membership Credentials  

Base membership and ENVITED membership are issued by ASCS.

### Administrator Credentials  

Issued by ASCS to individuals acting on behalf of ASCS or participants.

### User Credentials  

Issued by participant administrators to individuals.  
These credentials use an opaque user DID under `did.identity.ascs.digital` to support:

- privacy (no PII in DID)
- key rotation
- multi-chain keys (Tezos + Etherlink)

---

## 5. Revocation

Example credentials reference a `credentialStatus` entry:

- `harbour:CRSetEntry`
- `statusPurpose: "revocation"`
- `id` pointing to a `did:web` revocation registry fragment

The DID document for the registry includes a **service endpoint** pointing to the actual registry.

---

## 6. Tooling

You may use:

- **jsonld-cli** for JSON-LD normalization and checking
- **didkit** for signing / verifying VC Data Model v2 credentials
- **jq** for inspection and debugging
- **JSON Schema** for linting examples where applicable

---

This folder is meant as a **reference implementation** for developers integrating  
SimpulseID credentials into ENVITED applications and services.
