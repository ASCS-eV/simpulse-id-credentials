# SimpulseID did:ethr DID Documents

This directory contains example `did:ethr` DID documents for the ENVITED
ecosystem. The examples assume a project-specific Base resolver profile:
signer DIDs expose their P-256 key material directly in the resolved document,
while resource DIDs (programs and services) point to an external controller DID.

At the on-chain layer, these identities are managed as deterministic keyless
addresses controlled through an `IdentityController` contract. That contract
verifies relayed P-256-signed instructions and updates ERC-1056 state; the JSON
files in this directory show the **resolved verifier-facing DID documents**
produced from that state.

## Network

- **Testnet**: Base Sepolia — chain ID `84532` (hex `0x14a34`)
- **Mainnet**: Base — chain ID `8453` (hex `0x2105`)

All example DIDs use the testnet chain ID: `did:ethr:0x14a34:<address>`

## Controller Model

The examples use two DID document patterns:

1. **Signer DIDs** (participants and users) expose a local P-256
   `JsonWebKey` as `#controller`. This is the primary ES256 signing key and
   the `kid` used by the example JWTs.
2. **Resource DIDs** (programs and infrastructure services) do not invent a
   local signing key. Instead they use the root DID Core `controller`
   property to point at the ASCS participant DID that governs them.

Additional P-256 keys may still appear as `#delegate-N` verification methods
when the examples need secondary keys. Chain anchoring and recovery semantics
belong to the Base contract and resolver metadata, not to a synthetic
secp256k1 verification method in these example documents.

Natural participants therefore use standard SSI wallets for P-256 signatures,
while a relay can submit the resulting authorized instruction on-chain without
requiring the user to hold an Ethereum private key.

## Entity Types

### Participants (Organizations)

| File | DID | Organization |
|------|-----|--------------|
| `simpulseid-participant-ascs-did.json` | `did:ethr:0x14a34:0x50916c8e454722d2357916d4250500102288bb03` | ASCS e.V. |
| `simpulseid-participant-bmw-did.json` | `did:ethr:0x14a34:0x9d273DCaC2f6367968d61caf69A7E3177fd81048` | BMW |

### Services

| File | DID | Purpose |
|------|-----|---------|
| `simpulseid-service-trust-anchor-did.json` | `did:ethr:0x14a34:0xcfD184a45d55F14cA554E4F65Bf23BF26824564B` | Trust anchor |
| `simpulseid-service-revocation-registry-did.json` | `did:ethr:0x14a34:0x4612FbF84Ef87dfBc363c6077235A475502346d1` | Revocation registry |

### Programs

| File | DID | Program |
|------|-----|---------|
| `simpulseid-program-administrator-did.json` | `did:ethr:0x14a34:0x34d8ED7DA77f3f522465E1A18Dd4fFe482021112` | Administrator |
| `simpulseid-program-ascs-base-membership-did.json` | `did:ethr:0x14a34:0x28b9692eD6f6Bcfeb81f544acB54FB6e780a422D` | Base membership |
| `simpulseid-program-ascs-envited-membership-did.json` | `did:ethr:0x14a34:0xF84945fB99BD70Cfe527a2cb2c368DbA4fB55bC9` | ENVITED membership |
| `simpulseid-program-user-did.json` | `did:ethr:0x14a34:0xA80e2AB10F9B708af7C880C15BD378ba3b707A38` | User |

### Users

| File | DID | Role |
|------|-----|------|
| `simpulseid-user-21c7c8bc-...-did.json` | `did:ethr:0x14a34:0xb2F78332cF29Bd4dBB04Dea2EF59439F43F0b39a` | Administrator (Andreas) |
| `simpulseid-user-44b982bb-...-did.json` | `did:ethr:0x14a34:0x0f4Dc6903A4B92C6563DD3551421ebb7ACa7d4fC` | User (Max) |

## Key Management

- **`#controller`** on signer DIDs is the primary P-256 `JsonWebKey`
- **`#delegate-N`** entries are optional additional P-256 keys
- **Program and service DIDs** are externally controlled by the ASCS participant DID
- Key rotation remains an on-chain concern handled through contract state and resolver logic

## Scope Boundary

This repository **does not**:

- Deploy or interact with the Base contract
- Resolve `did:ethr` identifiers at runtime
- Manage on-chain key registration

Integrators must deploy the contract and implement DID resolution against the
registered Base state for this custom profile.

## References

- [did:ethr Method Specification](../../docs/references/did-ethr-method-spec.md)
- [ERC-1056: Ethereum Lightweight Identity](https://eips.ethereum.org/EIPS/eip-1056)
- [EthereumDIDRegistry](https://github.com/uport-project/ethr-did-registry)
