"""Tests for the evidence proof chain in SimpulseID credentials.

Verifies that:
1. Expanded evidence VPs can be signed and produce valid JWTs
2. Outer credentials with JWT evidence can be signed and verified
3. The full chain (outer VC -> evidence VP -> inner VC) is decodable
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


class TestEvidenceVPSigning:
    """Test signing of evidence VPs extracted from example credentials."""

    def test_sign_credential_evidence_vp(
        self, p256_private_key, p256_public_key, p256_did_key_vm
    ):
        """Sign a CredentialEvidence VP and verify it."""
        vc = _load_example("simpulseid-participant-credential.json")
        vp = _get_evidence_vp(vc)
        assert vp is not None, "Expected expanded evidence VP"

        # Sign inner VCs first
        inner_vcs = vp.get("verifiableCredential", [])
        inner_jwts = []
        for inner_vc in inner_vcs:
            jwt = sign_vc_jose(inner_vc, p256_private_key, kid=p256_did_key_vm)
            inner_jwts.append(jwt)

        # Build VP with JWT inner VCs
        signed_vp = {
            "@context": vp["@context"],
            "type": vp["type"],
            "verifiableCredential": inner_jwts,
        }
        if "holder" in vp:
            signed_vp["holder"] = vp["holder"]

        nonce = vp.get("nonce")
        vp_jwt = sign_vp_jose(
            signed_vp, p256_private_key, kid=p256_did_key_vm, nonce=nonce
        )

        # Verify VP
        result = verify_vp_jose(vp_jwt, p256_public_key, expected_nonce=nonce)
        assert result["type"] == ["VerifiablePresentation"]
        assert len(result["verifiableCredential"]) == 1

    def test_sign_membership_evidence_vp(
        self, p256_private_key, p256_public_key, p256_did_key_vm
    ):
        """Sign a membership CredentialEvidence VP and verify it."""
        vc = _load_example("simpulseid-ascs-base-membership-credential.json")
        vp = _get_evidence_vp(vc)
        assert vp is not None, "Expected expanded evidence VP"

        inner_vcs = vp.get("verifiableCredential", [])
        inner_jwts = []
        for inner_vc in inner_vcs:
            jwt = sign_vc_jose(inner_vc, p256_private_key, kid=p256_did_key_vm)
            inner_jwts.append(jwt)

        signed_vp = {
            "@context": vp["@context"],
            "type": vp["type"],
            "verifiableCredential": inner_jwts,
        }

        vp_jwt = sign_vp_jose(signed_vp, p256_private_key, kid=p256_did_key_vm)

        result = verify_vp_jose(vp_jwt, p256_public_key)
        assert result["type"] == ["VerifiablePresentation"]


# ---------------------------------------------------------------------------
# Full proof chain
# ---------------------------------------------------------------------------


class TestFullProofChain:
    """Test the full signing chain: inner VC -> evidence VP -> outer VC."""

    @pytest.fixture()
    def signed_participant(self, p256_private_key, p256_public_key, p256_did_key_vm):
        """Sign the participant credential with full evidence chain."""
        import copy

        vc = _load_example("simpulseid-participant-credential.json")
        vc_copy = copy.deepcopy(vc)

        evidence_vp_jwt = None
        for ev in vc_copy.get("evidence", []):
            vp = ev.get("verifiablePresentation")
            if isinstance(vp, dict):
                # Sign inner VCs
                inner_jwts = []
                for inner_vc in vp.get("verifiableCredential", []):
                    inner_jwts.append(
                        sign_vc_jose(inner_vc, p256_private_key, kid=p256_did_key_vm)
                    )
                signed_vp = {
                    "@context": vp["@context"],
                    "type": vp["type"],
                    "verifiableCredential": inner_jwts,
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
        assert result["type"] == ["VerifiablePresentation"]

    def test_inner_emailpass_vc_verifies(self, signed_participant, p256_public_key):
        """The inner EmailPass VC JWT inside the evidence VP should verify."""
        _, evidence_vp_jwt = signed_participant
        vp_result = verify_vp_jose(evidence_vp_jwt, p256_public_key)
        inner_jwt = vp_result["verifiableCredential"][0]
        assert isinstance(inner_jwt, str)
        inner_result = verify_vc_jose(inner_jwt, p256_public_key)
        assert "EmailPass" in inner_result["type"]
        assert inner_result["credentialSubject"]["email"] == "admin1@asc-s.de"

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

        # Decode inner EmailPass VC
        inner_jwt = vp["payload"]["verifiableCredential"][0]
        inner = _decode_jwt(inner_jwt)
        assert inner["header"]["typ"] == "vc+jwt"
        assert "EmailPass" in inner["payload"]["type"]

    def test_issuer_is_string_did(self, signed_participant, p256_public_key):
        """The issuer should be a string DID (not an object)."""
        vc_jwt, _ = signed_participant
        result = verify_vc_jose(vc_jwt, p256_public_key)
        assert isinstance(result["issuer"], str)
        assert result["issuer"].startswith("did:")


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
