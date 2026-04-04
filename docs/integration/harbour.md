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

The nonce uses the `HARBOUR_DELEGATE` challenge format from harbour's delegation module, binding the evidence to the specific credential issuance. The challenge is `<random> HARBOUR_DELEGATE <SHA-256(TransactionData)>` with the `credential.issue` action type. This follows [EVES-009](https://github.com/ASCS-eV/EVES/blob/main/EVES/EVES-009/eves-009.md) and [OID4VP §8.4](https://openid.net/specs/openid-4-verifiable-presentations-1_0.html).

## SD-JWT-VC Structured Selective Disclosure

Harbour's SD-JWT-VC implementation supports structured (nested) selective disclosure
per [RFC 9901 §6.2](https://www.rfc-editor.org/rfc/rfc9901#section-6). Credentials
keep their nested W3C VCDM structure — only individual attribute values are hidden:

```python
from harbour.sd_jwt import issue_sd_jwt_vc

sd_jwt = issue_sd_jwt_vc(
    credential["credentialSubject"],
    private_key,
    vct="https://w3id.org/ascs-ev/simpulse-id/v1/ParticipantCredential",
    disclosable=["credentialSubject.email", "credentialSubject.duns"],
)
```

The credential structure (types, nesting) stays visible — only sensitive values
(email, DUNS, etc.) are hidden behind `_sd` digests at the appropriate nesting level.

See individual credential type pages for disclosure policy details:

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
