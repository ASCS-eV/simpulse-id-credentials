# Specifications

SimpulseID implements the following ENVITED-X Ecosystem Specifications (EVES), maintained at [github.com/ASCS-eV/EVES](https://github.com/ASCS-eV/EVES).

## EVES-008: SimpulseID Credential and Identity Framework

[EVES-008](https://github.com/ASCS-eV/EVES/blob/main/EVES/EVES-008/eves-008.md) defines the identity, membership, and credential architecture for the ENVITED-X Data Space. It specifies:

- Five credential types (Participant, Administrator, User, Base Membership, ENVITED Membership)
- `did:ethr` identifiers anchored on Base (ERC-1056) with P-256 key management
- JSON-LD context ordering and `w3id.org` persistent identifier resolution
- Credential subject semantics (`member` vs `memberOf`, `urn:uuid:` for memberships)
- Revocation via `harbour:CRSetEntry`
- Schema-first approach using LinkML as the single source of truth

This repository is the reference implementation of EVES-008.

## EVES-009: Evidence-Based Consent Using Verifiable Presentations

[EVES-009](https://github.com/ASCS-eV/EVES/blob/main/EVES/EVES-009/eves-009.md) defines the protocol for generating and verifying cryptographic evidence of user consent. SimpulseID credentials use this protocol for evidence VPs:

- Evidence VPs use the `HARBOUR_DELEGATE` challenge format with the `credential.issue` action type
- The challenge binds consent to a specific credential via SHA-256 over canonical `TransactionData`
- Verification follows OID4VP with KB-JWT `transaction_data_hashes` for message binding
- SD-JWT VCs are the recommended format for selective disclosure

The evidence protocol is implemented by [harbour-credentials](https://github.com/reachhaven/harbour-credentials) (`delegation.py`, `sd_jwt_vp.py`). SimpulseID uses it via `src/sign_examples.py`.

## External Standards

| Standard | Version | Usage |
|----------|---------|-------|
| [W3C VC Data Model](https://www.w3.org/TR/vc-data-model-2.0/) | v2.0 | Credential envelope structure |
| [W3C DID Core](https://www.w3.org/TR/did-core/) | v1.1 | Decentralized identifier resolution |
| [did:ethr Method](https://github.com/decentralized-identity/ethr-did-resolver/blob/master/doc/did-method-spec.md) | — | On-chain identity via ERC-1056 |
| [Gaia-X Trust Framework](https://docs.gaia-x.eu/) | 25.11 (Loire) | LegalPerson/NaturalPerson compliance |
| [OID4VP](https://openid.net/specs/openid-4-verifiable-presentations-1_0.html) | 1.0 | Evidence VP presentation protocol |
| [RFC 9901 (SD-JWT-VC)](https://www.rfc-editor.org/rfc/rfc9901) | — | Selective disclosure credentials |
| [LinkML](https://linkml.io/) | — | Schema definition language |
| [schema.org](https://schema.org/) | — | Vocabulary for program metadata |
