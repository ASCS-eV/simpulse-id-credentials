"""Tests for the evidence proof chain in SimpulseID credentials.

Verifies that:
1. Empty evidence VPs (holder + nonce, no inner VCs) can be signed and verified
2. Outer credentials with JWT evidence can be signed and verified
3. The full chain (outer VC -> evidence VP) is decodable
"""

import base64
import json
from pathlib import Path

import pytest
from harbour.signer import sign_vc_jose, sign_vp_jose
from harbour.verifier import verify_vc_jose, verify_vp_jose

EXAMPLES_DIR = Path(__file__).parent.parent / "examples"


def _b64url_decode(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def _decode_jwt(token: str) -> dict:
    parts = token.split(".")
    header = json.loads(_b64url_decode(parts[0]))
    payload = json.loads(_b64url_decode(parts[1]))
    return {"header": header, "payload": payload}


def _load_example(name: str) -> dict:
    path = EXAMPLES_DIR / name
    return json.loads(path.read_text())


def _get_evidence_vp(vc: dict) -> dict | None:
    """Extract the first expanded evidence VP from a credential."""
    for ev in vc.get("evidence", []):
        vp = ev.get("verifiablePresentation")
        if isinstance(vp, dict):
            return vp
    return None


# ---------------------------------------------------------------------------
# Evidence VP signing
# ---------------------------------------------------------------------------


_ALL_CREDENTIAL_FILES = sorted(EXAMPLES_DIR.glob("simpulseid-*.json"))


class TestEvidenceVPSigning:
    """Test signing of empty evidence VPs extracted from example credentials."""

    @pytest.mark.parametrize(
        "path", _ALL_CREDENTIAL_FILES, ids=[f.stem for f in _ALL_CREDENTIAL_FILES]
    )
    def test_sign_evidence_vp(
        self, path, p256_private_key, p256_public_key, p256_did_key_vm
    ):
        """Sign an evidence VP from each credential type and verify it."""
        vc = json.loads(path.read_text())
        vp = _get_evidence_vp(vc)
        assert vp is not None, f"Expected evidence VP in {path.name}"

        signed_vp = {
            "@context": vp["@context"],
            "type": vp["type"],
        }
        if "holder" in vp:
            signed_vp["holder"] = vp["holder"]

        nonce = vp.get("nonce")
        vp_jwt = sign_vp_jose(
            signed_vp, p256_private_key, kid=p256_did_key_vm, nonce=nonce
        )

        result = verify_vp_jose(vp_jwt, p256_public_key, expected_nonce=nonce)
        assert "VerifiablePresentation" in result["type"]

    def test_evidence_vp_has_holder(
        self, p256_private_key, p256_public_key, p256_did_key_vm
    ):
        """Evidence VP should carry the holder DID after signing."""
        vc = _load_example("simpulseid-participant-credential.json")
        vp = _get_evidence_vp(vc)

        signed_vp = {
            "@context": vp["@context"],
            "type": vp["type"],
            "holder": vp["holder"],
        }
        nonce = vp.get("nonce")
        vp_jwt = sign_vp_jose(
            signed_vp, p256_private_key, kid=p256_did_key_vm, nonce=nonce
        )

        result = verify_vp_jose(vp_jwt, p256_public_key, expected_nonce=nonce)
        assert result["holder"] == vp["holder"]
        assert result["holder"].startswith("did:")

    def test_evidence_vp_has_nonce(
        self, p256_private_key, p256_public_key, p256_did_key_vm
    ):
        """Evidence VP should carry the nonce after signing.

        The nonce is injected at signing time (not in the pre-signed skeleton)
        because the harbour VerifiablePresentation SHACL shape is closed and
        does not permit extra properties like nonce.
        """
        vc = _load_example("simpulseid-participant-credential.json")
        vp = _get_evidence_vp(vc)
        nonce = "test-nonce-12345"

        signed_vp = {
            "@context": vp["@context"],
            "type": vp["type"],
            "holder": vp["holder"],
        }
        vp_jwt = sign_vp_jose(
            signed_vp, p256_private_key, kid=p256_did_key_vm, nonce=nonce
        )

        result = verify_vp_jose(vp_jwt, p256_public_key, expected_nonce=nonce)
        assert "nonce" in result


# ---------------------------------------------------------------------------
# Full proof chain
# ---------------------------------------------------------------------------


class TestFullProofChain:
    """Test the full signing chain: evidence VP -> outer VC."""

    @pytest.fixture()
    def signed_participant(self, p256_private_key, p256_public_key, p256_did_key_vm):
        """Sign the participant credential with empty evidence VP."""
        import copy

        vc = _load_example("simpulseid-participant-credential.json")
        vc_copy = copy.deepcopy(vc)

        evidence_vp_jwt = None
        for ev in vc_copy.get("evidence", []):
            vp = ev.get("verifiablePresentation")
            if isinstance(vp, dict):
                signed_vp = {
                    "@context": vp["@context"],
                    "type": vp["type"],
                }
                if "holder" in vp:
                    signed_vp["holder"] = vp["holder"]
                nonce = vp.get("nonce")
                evidence_vp_jwt = sign_vp_jose(
                    signed_vp,
                    p256_private_key,
                    kid=p256_did_key_vm,
                    nonce=nonce,
                )
                ev["verifiablePresentation"] = evidence_vp_jwt

        vc_jwt = sign_vc_jose(vc_copy, p256_private_key, kid=p256_did_key_vm)
        return vc_jwt, evidence_vp_jwt

    def test_outer_vc_verifies(self, signed_participant, p256_public_key):
        """The outer VC JWT should verify."""
        vc_jwt, _ = signed_participant
        result = verify_vc_jose(vc_jwt, p256_public_key)
        assert result["type"] == [
            "VerifiableCredential",
            "simpulseid:ParticipantCredential",
        ]

    def test_evidence_vp_is_jwt_in_outer(self, signed_participant, p256_public_key):
        """The evidence VP should be a JWT string in the outer VC."""
        vc_jwt, _ = signed_participant
        result = verify_vc_jose(vc_jwt, p256_public_key)
        ev = result["evidence"][0]
        vp_str = ev["verifiablePresentation"]
        assert isinstance(vp_str, str)
        assert vp_str.count(".") == 2  # compact JWS

    def test_evidence_vp_verifies(self, signed_participant, p256_public_key):
        """The evidence VP JWT should verify."""
        _, evidence_vp_jwt = signed_participant
        assert evidence_vp_jwt is not None
        result = verify_vp_jose(evidence_vp_jwt, p256_public_key)
        assert "VerifiablePresentation" in result["type"]

    def test_full_chain_decoded(self, signed_participant):
        """Decode the full chain and verify structure."""
        vc_jwt, evidence_vp_jwt = signed_participant

        # Decode outer VC
        outer = _decode_jwt(vc_jwt)
        assert outer["header"]["typ"] == "vc+jwt"
        assert outer["header"]["alg"] == "ES256"

        # Decode evidence VP
        vp = _decode_jwt(evidence_vp_jwt)
        assert vp["header"]["typ"] == "vp+jwt"
        # Empty VP — no verifiableCredential array
        assert "verifiableCredential" not in vp["payload"]

    def test_issuer_is_string_did(self, signed_participant, p256_public_key):
        """The issuer should be a string DID (not an object)."""
        vc_jwt, _ = signed_participant
        result = verify_vc_jose(vc_jwt, p256_public_key)
        assert isinstance(result["issuer"], str)
        assert result["issuer"].startswith("did:")

    def test_credential_subject_has_harbour_credential(
        self, signed_participant, p256_public_key
    ):
        """The credential subject should have a harbourCredential IRI."""
        vc_jwt, _ = signed_participant
        result = verify_vc_jose(vc_jwt, p256_public_key)
        subject = result["credentialSubject"]
        assert "harbourCredential" in subject
        assert subject["harbourCredential"].startswith("urn:uuid:")


# ---------------------------------------------------------------------------
# Sign-verify fixture
# ---------------------------------------------------------------------------


class TestSignVerifyFixture:
    """Test using the committed sign-verify fixture."""

    @pytest.fixture()
    def fixture_data(self):
        path = Path(__file__).parent / "fixtures" / "participant-sign-verify.json"
        if not path.exists():
            pytest.skip("Sign-verify fixture not found")
        return json.loads(path.read_text())

    def test_sign_fixture_vc(
        self, fixture_data, p256_private_key, p256_public_key, p256_did_key_vm
    ):
        """Sign the fixture input VC and verify expected output values."""
        vc = fixture_data["input"]["vc"]
        expected = fixture_data["output"]

        token = sign_vc_jose(vc, p256_private_key, kid=p256_did_key_vm)
        decoded = _decode_jwt(token)

        assert decoded["header"]["typ"] == expected["decoded_header_typ"]
        assert decoded["header"]["alg"] == expected["decoded_header_alg"]
        assert decoded["payload"]["type"] == expected["decoded_payload_type"]
        assert decoded["payload"]["id"] == expected["decoded_payload_id"]

    def test_verify_fixture_roundtrip(
        self, fixture_data, p256_private_key, p256_public_key, p256_did_key_vm
    ):
        """Sign and verify the fixture VC round-trips correctly."""
        vc = fixture_data["input"]["vc"]
        token = sign_vc_jose(vc, p256_private_key, kid=p256_did_key_vm)
        result = verify_vc_jose(token, p256_public_key)
        assert result["id"] == vc["id"]
        assert result["type"] == vc["type"]
