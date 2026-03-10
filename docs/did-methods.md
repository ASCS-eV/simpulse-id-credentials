# DID Methods

This document clarifies the Decentralized Identifier (DID) methods used across
the SimpulseID / ENVITED ecosystem and the Harbour credentials library.

## Supported DID Methods

| Method     | Spec                                                                                       | Root of Trust                   | Used By              |
|------------|--------------------------------------------------------------------------------------------|---------------------------------|----------------------|
| `did:ethr` | [ERC-1056](https://eips.ethereum.org/EIPS/eip-1056) / [did:ethr spec](../references/did-ethr-method-spec.md) | EVM smart contract (on-chain)   | SimpulseID + Harbour |
| `did:key`  | [W3C CCG](https://w3c-ccg.github.io/did-method-key/)                                      | Self-certifying                 | Ephemeral / evidence |

## Policy

### SimpulseID Production (`did:ethr`)

All identities are managed on-chain via a custom ERC-1056 EthereumDIDRegistry
smart contract deployed on **Base** (L2 rollup).

- **Testnet**: Base Sepolia (chain ID `84532`, hex `0x14a34`)
- **Mainnet**: Base (chain ID `8453`, hex `0x2105`)

DID format:

```text
did:ethr:0x14a34:<ethereum-address>
```

Entity types:

```text
did:ethr:0x14a34:0x5091...bb03  ← ASCS (trust anchor operator)
did:ethr:0x14a34:0x9d27...1048  ← Participant (e.g., BMW)
did:ethr:0x14a34:0xb2F7...b39a  ← Natural person (user/admin)
did:ethr:0x14a34:0x4612...46d1  ← Infrastructure service (revocation registry)
did:ethr:0x14a34:0x28b9...422D  ← Program definition (membership)
```

**Key Management**: P-256 keys are registered as on-chain attributes via
`setAttribute()` on the EthereumDIDRegistry contract. The resolved DID Document
includes these keys as `JsonWebKey2020` verification methods. The contract
controller address manages identity ownership.

**Resolution**: DID Documents are built by reading on-chain events
(`DIDOwnerChanged`, `DIDDelegateChanged`, `DIDAttributeChanged`) from the
ERC-1056 registry contract. No web server hosting required.

**Trust**: Anchored in the EVM smart contract state — immutable, auditable,
and verifiable on-chain. The controller contract governs all identity
operations.

### Evidence Holders (`did:key`)

Ephemeral evidence VP holders may use `did:key` for self-certifying identity
that does not require DID document hosting or on-chain registration.

## Verifier Requirements

A verifier processing SimpulseID credentials needs to:

1. Resolve `did:ethr` identifiers by reading the ERC-1056 registry on Base
2. Verify that the `kid` in the JWT header resolves to a key in the issuer's
   `assertionMethod` (per **W3C VC-JOSE-COSE §3.3.2**)
3. Support ES256 (P-256) signature verification

## References

- [W3C DID Core v1.1](https://www.w3.org/TR/did-1.1/)
- [W3C DID Resolution v0.3](https://www.w3.org/TR/did-resolution/)
- [did:ethr Method Specification](../references/did-ethr-method-spec.md)
- [ERC-1056: Ethereum Lightweight Identity](https://eips.ethereum.org/EIPS/eip-1056)
- [EthereumDIDRegistry](https://github.com/uport-project/ethr-did-registry)
- [Gaia-X ICAM 25.11](https://docs.gaia-x.eu/technical-committee/identity-credential-access-management/25.11/)
