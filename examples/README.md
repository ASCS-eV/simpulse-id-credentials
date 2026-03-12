# SimpulseID Credential Examples

This folder contains **reference examples** for all Verifiable Credentials used in the  
ENVITED Ecosystem operated by ASCS e.V.

These examples demonstrate:

- the JSON-LD structure using the public contexts in `/contexts`
- the semantics defined in `/ontologies`
- correct use of `did:ethr` identifiers for:
  - participants (organizations)
  - ASCS programs (base membership, ENVITED membership)
  - users and administrators (opaque non-PII identifiers)
- correct Gaia-X–compatible modelling of addresses, legal forms, and terms & conditions
- revocation status entries using the Harbour Credentials context

The examples serve as a canonical blueprint for services integrating with  
**<https://identity.ascs.digital/>**.

> **Note on `harbourCredential` IRIs:** The `harbourCredential` values in
> these examples (e.g., `urn:uuid:a1b2c3d4-e5f6-7890-abcd-ef1234567890`)
> are synthetic placeholders. In production, each SimpulseID credential
> references an actual Harbour Gaia-X baseline credential issued and
> retrievable via the Trust Anchor's `LinkedCredentialService` endpoint
> (see the DID document examples).

---

## Structure of the Examples

### 1. Verifiable Credentials

Each credential in this folder uses:

- `https://www.w3.org/2018/credentials#` (VC Data Model v2)
- `simpulseid_context.jsonld` (main context)
- `harbour_context.jsonld` (credential status)
- `harbour:CRSetEntry` with `statusPurpose: "revocation"`

Types included:

- **Participant Credential**
  Identity of an organization (e.g., BMW). References a Harbour Gaia-X credential
  via `harbourCredential` IRI as the baseline of trust.

- **ASCS Base Membership Credential**  
  Proof of base membership in ASCS e.V.

- **ENVITED Membership Credential**  
  Extends the base membership and links to a program DID.

- **Administrator Credential**  
  Natural person with elevated rights, issued and controlled by ASCS.

- **User Credential**  
  Natural person affiliated with a participant, issued by the participant’s admin.

All credentials use **`did:ethr` subject identifiers** (on Base Sepolia) for users and admins:

- opaque
- non-PII
- key-rotation capable (via ERC-1056 on-chain key management)

**Note on membership credential subjects:** Membership credentials
(`AscsBaseMembershipCredential`, `AscsEnvitedMembershipCredential`) use
`urn:uuid:` subject identifiers instead of DIDs. This is intentional —
memberships are abstract resources (not DID-resolvable entities). The
`member` field within the credential subject provides the link to the
participant's DID (`did:ethr:...`). Per **W3C VCDM 2.0 §4.3**, `urn:uuid:`
is a valid URI for credentialSubject.id.

All credentials include the **Gaia-X development context**
(`https://w3id.org/gaia-x/development#`) to enable `gxParticipant`
composition with `gx:LegalPerson` or `gx:Participant` properties per
**Gaia-X ICAM 25.11**.

All credentials use the `evidence` field to show that the credential was requested by an admin before being signed by the service. The evidence nonce follows the harbour delegation challenge format: `<random_hex> <sha256_payload_hash>` per **OID4VP §8.4**. Checking this is possible by:

- checking the cryptographic and syntactical integrity of the `evidence`
- retrieving the issuer's DID document (a participant `did:ethr`)
- verifying the `kid` in the JWT header resolves to a key in the issuer's `assertionMethod` (per **W3C VC-JOSE-COSE §3.3.2**)
- verifying the delegation nonce matches the SHA-256 hash of the credential payload

---

## 2. did:ethr DID Documents

Examples under `examples/did-ethr/` illustrate:

- Participant DIDs controlled by organizations
  (e.g., `did:ethr:0x14a34:0x50916c8e454722d2357916d4250500102288bb03`)

- Program and service DIDs controlled by the ASCS participant DID via the root
  DID Core `controller` property

- User and Administrator DIDs:
  Opaque, privacy-preserving identifiers that expose only P-256 verification keys.

Signer DID documents support:

- A local `#controller` `JsonWebKey` (the primary ES256 signing key)
- Optional additional P-256 delegates (`#delegate-N`)
- Key rotation (through ERC-1056 `setAttribute` / `revokeAttribute`)

Resource DID documents (programs and services) omit local signing keys and
instead point their root `controller` property at the owning participant DID.

No DID document contains personal data.

---

## 3. Wallet Rendering Manifests

The manifests in `/manifests` define how SSI wallets such as **Altme** render cards using the  
Decentralized Identity Foundation **Wallet Rendering Specification**.

Each manifest:

- references the correct SimpulseID credential type
- defines which properties appear on the card
- includes human-readable fallback titles
- is issued by the ASCS organizational DID (`did:ethr:0x14a34:0x50916c8e454722d2357916d4250500102288bb03`)

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
These credentials use an opaque user DID under `did.ascs.digital` to support:

- privacy (no PII in DID)
- key rotation (via ERC-1056 on-chain attribute management)
- Base chain account binding

---

## 5. Revocation

Example credentials reference a `credentialStatus` entry:

- `harbour:CRSetEntry`
- `statusPurpose: "revocation"`
- `id` pointing to a `did:ethr` revocation registry fragment

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
