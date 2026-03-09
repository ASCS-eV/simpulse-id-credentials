# Harbour Credentials Integration

The [harbour-credentials](https://github.com/reachhaven/harbour-credentials) library provides the cryptographic foundation for SimpulseID credentials — keypair generation, JOSE signing/verification, and SD-JWT-VC issuance.

## Setup

harbour-credentials is included as a git submodule and installed during setup:

```bash
make setup
```

Or install manually:

```bash
pip install -e submodules/harbour-credentials[dev]
```

## Keypair Generation

Generate a P-256 keypair and derive a `did:key` identifier:

```python
from harbour.keys import generate_p256_keypair, p256_public_key_to_did_key

private_key, public_key = generate_p256_keypair()
did = p256_public_key_to_did_key(public_key)
kid = f"{did}#{did.split(':')[-1]}"
```

The `kid` (Key ID) follows the `did:key` fragment convention per [VC-JOSE-COSE §3.3.2](https://www.w3.org/TR/vc-jose-cose/).

## Signing Credentials (JOSE)

Sign a W3C VCDM v2 credential as a `vc+jwt`:

```python
from harbour.signer import sign_vc_jose

signed_jwt = sign_vc_jose(credential, private_key, kid=kid)
```

The result is a compact JWT with:

- Header: `{"alg": "ES256", "typ": "vc+jwt", "kid": "<did>#<fragment>"}`
- Payload: The credential JSON

## Verifying Credentials

```python
from harbour.verifier import verify_vc_jose

payload = verify_vc_jose(signed_jwt, public_key)
```

## Evidence VP Signing

Credentials with evidence (e.g., delegation proofs) require signing the evidence Verifiable Presentation before signing the outer credential:

```python
from harbour.signer import sign_vp_jose

# Sign the evidence VP with the holder's key
evidence_vp_jwt = sign_vp_jose(
    evidence_vp,
    holder_private_key,
    holder_kid=holder_kid,
    nonce=nonce,
)
```

The nonce is computed as a SHA-256 hash of the issuer's payload, binding the evidence to the specific credential issuance per [OID4VP §8.4](https://openid.net/specs/openid-4-verifiable-presentations-1_0.html).

## SD-JWT-VC Claim Mapping

The `claim_mapping` module converts between W3C VCDM JSON-LD and flat SD-JWT-VC claims:

```python
from src.claim_mapping import vc_to_sd_jwt_claims, get_mapping_for_vc

mapping = get_mapping_for_vc(credential)
flat_claims, disclosable = vc_to_sd_jwt_claims(credential, mapping)
```

Each credential type defines which claims are always disclosed vs. selectively disclosed. See individual credential type pages for mapping details:

- [ParticipantCredential](../credentials/participant.md)
- [UserCredential](../credentials/user.md)
- [AdministratorCredential](../credentials/administrator.md)
- [Membership Credentials](../credentials/membership.md)

## Signing Examples

The `sign_examples.py` script processes all example credentials:

```bash
python3 src/sign_examples.py
```

This generates signed JWTs in `examples/signed/`, replacing evidence nonce placeholders with computed values.

## See Also

- [Quick Start](../getting-started/quickstart.md) — End-to-end workflow
- [Validation](validation.md) — SHACL validation of credentials
- [harbour-credentials repository](https://github.com/reachhaven/harbour-credentials)
