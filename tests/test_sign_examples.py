"""Sign and verify all example credentials from examples/."""

import pytest
from harbour.jose.signer import sign_vc, sign_vc_jose
from harbour.jose.verifier import VerificationError, verify_vc, verify_vc_jose

# ---------------------------------------------------------------------------
# VC-JOSE-COSE (ES256) — current format
# ---------------------------------------------------------------------------


def test_sign_and_verify_example_jose(
    example_vc, p256_private_key, p256_public_key, p256_did_key_vm
):
    """Sign an example VC as VC-JOSE-COSE JWT, then verify."""
    token = sign_vc_jose(example_vc, p256_private_key, kid=p256_did_key_vm)
    result = verify_vc_jose(token, p256_public_key)
    assert result["id"] == example_vc["id"]
    assert result["type"] == example_vc["type"]


def test_tamper_detection_jose(
    example_vc, p256_private_key, p256_public_key, p256_did_key_vm
):
    """Sign, tamper with JWT payload, verify detection."""
    import base64
    import json

    token = sign_vc_jose(example_vc, p256_private_key, kid=p256_did_key_vm)
    parts = token.split(".")

    payload = json.loads(base64.urlsafe_b64decode(parts[1] + "=="))
    payload["credentialSubject"]["id"] = "did:web:evil.example.com"
    tampered_payload = (
        base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b"=").decode()
    )
    tampered_token = f"{parts[0]}.{tampered_payload}.{parts[2]}"

    with pytest.raises(VerificationError):
        verify_vc_jose(tampered_token, p256_public_key)


def test_verify_signed_jwt(signed_jwt, p256_public_key):
    """Verify a pre-generated signed JWT from examples/signed/."""
    result = verify_vc_jose(signed_jwt, p256_public_key)
    assert "type" in result
    assert "VerifiableCredential" in result["type"]


# ---------------------------------------------------------------------------
# Legacy Ed25519Signature2018 — backwards compatibility
# ---------------------------------------------------------------------------


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_sign_and_verify_example_legacy(
    example_vc, private_key, public_key, did_key_vm
):
    """Sign an example VC with legacy format, then verify."""
    signed = sign_vc(example_vc, private_key, did_key_vm)
    assert verify_vc(signed, public_key) is True
