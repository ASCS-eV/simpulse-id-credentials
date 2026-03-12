# DID Methods

This document clarifies the Decentralized Identifier (DID) methods used across
the SimpulseID / ENVITED ecosystem and the Harbour credentials library.

## Supported DID Methods

| Method     | Spec                                                                                       | Root of Trust                 | Used By              |
|------------|--------------------------------------------------------------------------------------------|-------------------------------|----------------------|
| `did:ethr` | [ERC-1056](https://eips.ethereum.org/EIPS/eip-1056) / [did:ethr spec](references/did-ethr-method-spec.md) | Base contract + resolver      | SimpulseID + Harbour |
| `did:key`  | [W3C CCG](https://w3c-ccg.github.io/did-method-key/)                                      | Self-certifying               | Ephemeral / evidence |

## Policy

### SimpulseID Production (`did:ethr`)

All identities are anchored on **Base** via a custom `did:ethr` deployment and
resolver profile.

- **Testnet**: Base Sepolia (chain ID `84532`, hex `0x14a34`)
- **Mainnet**: Base (chain ID `8453`, hex `0x2105`)

DID format:

```text
did:ethr:0x14a34:<ethereum-address>
```

Depending on resolver/tooling, production DIDs may also be rendered with an
explicit EIP-155 segment such as `did:ethr:eip155:8453:<address>`. The checked-in
examples use the hexadecimal chain-ID form emitted by the current fixture set.

Entity types:

```text
did:ethr:0x14a34:0x5091...bb03  ← ASCS participant / operator
did:ethr:0x14a34:0x9d27...1048  ← Participant (e.g., BMW)
did:ethr:0x14a34:0xb2F7...b39a  ← Natural person (user/admin)
did:ethr:0x14a34:0x4612...46d1  ← Infrastructure service (revocation registry)
did:ethr:0x14a34:0x28b9...422D  ← Program definition (membership)
```

**Key Management**: Signer DID documents expose the primary P-256 signing key as
a local `#controller` `JsonWebKey`. Optional secondary P-256 keys are published
as `#delegate-N` methods. Non-signing service and program DIDs do not synthesize
local signing keys; instead they use the root DID Core `controller` property to
point at the participant DID that governs the resource.

**Resolution**: DID documents are reconstructed from Base contract state and
registered attributes by a project-specific resolver. No web server hosting is
required, but the resolved document is not assumed to match the default
`ethr-did-resolver` secp256k1 recovery-key shape.

In the underlying Harbour architecture, the managed DID addresses are
deterministic and keyless. An on-chain `IdentityController` contract owns the
ERC-1056 identities, verifies relayed P-256-signed instructions, and publishes
the DID attributes that the resolver turns into the verifier-facing JSON-LD
documents used in this repository.

**Trust**: Anchored in Base contract state and resolver logic — auditable,
verifiable on-chain, and aligned with the P-256 controllers used for ES256
credential signing.

### Evidence Holders (`did:key`)

Ephemeral evidence VP holders may use `did:key` for self-certifying identity
that does not require DID document hosting or on-chain registration.

## Verifier Requirements

A verifier processing SimpulseID credentials needs to:

1. Resolve `did:ethr` identifiers with the Base resolver profile
2. Verify that the `kid` in the JWT header resolves to a key in the issuer's
   `assertionMethod` (per **W3C VC-JOSE-COSE §3.3.2**)
3. Support ES256 (P-256) signature verification
4. Understand that the checked-in DID examples show resolved controller keys for
   verifiers, while on-chain control is mediated by the project-specific
   `IdentityController` layer

## References

- [W3C DID Core v1.1](https://www.w3.org/TR/did-1.1/)
- [W3C DID Resolution v0.3](https://www.w3.org/TR/did-resolution/)
- [did:ethr Method Specification](references/did-ethr-method-spec.md)
- [ERC-1056: Ethereum Lightweight Identity](https://eips.ethereum.org/EIPS/eip-1056)
- [EthereumDIDRegistry](https://github.com/uport-project/ethr-did-registry)
- [Gaia-X ICAM 25.11](https://docs.gaia-x.eu/technical-committee/identity-credential-access-management/25.11/)
