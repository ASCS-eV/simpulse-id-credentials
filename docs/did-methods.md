# DID Methods

This document clarifies the Decentralized Identifier (DID) methods used across
the SimpulseID / ENVITED ecosystem and the Harbour credentials library.

## Supported DID Methods

| Method     | Spec                                                  | Root of Trust      | Used By              |
|------------|-------------------------------------------------------|--------------------|----------------------|
| `did:web`  | [W3C CCG](https://w3c-ccg.github.io/did-method-web/) | DNS / TLS (Web PKI)| SimpulseID examples  |
| `did:webs` | [WebOfTrust](https://trustoverip.github.io/tswg-did-method-webs-specification/) | KERI (cryptographic)| Harbour examples     |
| `did:key`  | [W3C CCG](https://w3c-ccg.github.io/did-method-key/) | Self-certifying    | Ephemeral / evidence |

## Policy

### SimpulseID Production (`did:web`)

All DID documents under `did.ascs.digital` use the `did:web` method:

```
did:web:did.ascs.digital:participants:ascs    ← ASCS (trust anchor operator)
did:web:did.ascs.digital:participants:bmw     ← Participant
did:web:did.ascs.digital:users:{uuid}         ← Natural person
did:web:did.ascs.digital:services:{name}      ← Infrastructure service
did:web:did.ascs.digital:programs:{name}      ← Program definition
```

Resolution: `did:web:did.ascs.digital:participants:ascs` resolves to
`https://did.ascs.digital/participants/ascs/did.json`.

Trust: Anchored in DNS ownership of `did.ascs.digital` + TLS certificate.
Per **DID-CORE-1.1 §8.1** and **GX-ICAM-25.11**, `did:web` is a supported
DID method for Gaia-X credential issuers.

### Harbour Library (`did:webs`)

Harbour's own examples use `did:webs` (KERI-anchored variant):

```
did:webs:harbour.reachhaven.com:{KERI_AID}
did:webs:participants.harbour.reachhaven.com:legal-persons:{uuid}:{KERI_AID}
```

Trust: Anchored in a KERI Autonomic Identifier (AID). The web domain provides
discoverability; the KERI event log provides cryptographic root of trust.

### Evidence Holders (`did:key`)

Ephemeral evidence VP holders may use `did:key` for self-certifying identity
that does not require DID document hosting.

## Verifier Requirements

A verifier processing SimpulseID credentials needs to support `did:web`
resolution (HTTPS fetch of `did.json`). Support for `did:webs` is only
required when processing Harbour-native credentials from `reachhaven.com`.

## References

- [W3C DID Core v1.1](https://www.w3.org/TR/did-1.1/)
- [W3C DID Resolution v0.3](https://www.w3.org/TR/did-resolution/)
- [did:web Method Specification](https://w3c-ccg.github.io/did-method-web/)
- [Gaia-X ICAM 25.11](https://docs.gaia-x.eu/technical-committee/identity-credential-access-management/25.11/)
