# SimpulseID did:ethr DID Documents

This directory contains example `did:ethr` DID documents for the ENVITED
ecosystem. These documents represent what the ERC-1056 EthereumDIDRegistry
on **Base** (L2 rollup) would resolve for each identity.

## Network

- **Testnet**: Base Sepolia — chain ID `84532` (hex `0x14a34`)
- **Mainnet**: Base — chain ID `8453` (hex `0x2105`)

All example DIDs use the testnet chain ID: `did:ethr:0x14a34:<address>`

## Smart Contract Controller

All identities are managed by a custom ERC-1056 contract that creates
`did:ethr` identities from P-256 keys.

Controller contract: `did:ethr:0x14a34:0xC0FFEEbabe000000000000000000000000000001`

## DID Document Structure

Each resolved DID document contains:

1. **`#controller`** — `EcdsaSecp256k1RecoveryMethod2020` with `blockchainAccountId`
   pointing to the identity's on-chain address (`eip155:84532:<address>`)
2. **P-256 verification keys** — Registered as on-chain attributes via
   `setAttribute("did/pub/EC/veriKey/jwk", ...)`, appearing as `JsonWebKey`
   entries in `verificationMethod`
3. **Service endpoints** — Registered via `setAttribute("did/svc/...", ...)`

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

- **P-256 keys** are the primary signing keys (ES256), registered on-chain
  as DID attributes
- **`#controller`** entry is the ERC-1056 identity owner (secp256k1 recovery)
- Key rotation is managed on-chain via `setAttribute` / `revokeAttribute`
- The smart contract controller governs all identity ownership

## Scope Boundary

This repository **does not**:

- Deploy or interact with the ERC-1056 smart contract
- Resolve `did:ethr` identifiers at runtime
- Manage on-chain key registration

Integrators must deploy the EthereumDIDRegistry contract and implement
DID resolution by reading on-chain events.

## References

- [did:ethr Method Specification](../../docs/references/did-ethr-method-spec.md)
- [ERC-1056: Ethereum Lightweight Identity](https://eips.ethereum.org/EIPS/eip-1056)
- [EthereumDIDRegistry](https://github.com/uport-project/ethr-did-registry)
