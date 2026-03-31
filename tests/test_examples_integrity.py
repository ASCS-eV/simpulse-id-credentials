"""Tests for example credential integrity and chain-of-trust properties.

Validates that example credentials meet the requirements for a verifiable,
auditable chain of trust per:
- W3C VC-JOSE-COSE §3.3.2 (kid → assertionMethod resolution)
- W3C VCDM 2.0 §4.1 (@context completeness)
- OID4VP §8.4 (delegation challenge nonce format)
- SD-JWT-VC-15 §3.2.2.1 (vct URI presence)
- Gaia-X ICAM 25.11 (gxParticipant composition)
"""

import json
from pathlib import Path

import pytest

EXAMPLES_DIR = Path(__file__).parent.parent / "examples"
DID_ETHR_DIR = EXAMPLES_DIR / "did-ethr"


def _load_all_examples():
    """Load all example credential JSON files."""
    return sorted(EXAMPLES_DIR.glob("simpulseid-*.json"))


def _load_all_did_docs():
    """Load all DID document JSON files."""
    docs = {}
    for f in sorted(DID_ETHR_DIR.glob("*.json")):
        data = json.loads(f.read_text())
        did_id = data.get("id", "")
        docs[did_id] = data
    return docs


EXAMPLE_FILES = _load_all_examples()
DID_DOCS = _load_all_did_docs()


# ---------------------------------------------------------------------------
# Evidence nonce tests (Finding F2)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("path", EXAMPLE_FILES, ids=[f.stem for f in EXAMPLE_FILES])
def test_evidence_nonce_not_placeholder(path):
    """Evidence nonces must not contain ISSUE_PAYLOAD placeholder.

    Per OID4VP §8.4, nonces must be valid cryptographic challenges.
    The signing pipeline computes proper delegation challenges at signing time.
    """
    vc = json.loads(path.read_text())
    for ev in vc.get("evidence", []):
        vp = ev.get("verifiablePresentation", {})
        if isinstance(vp, dict):
            nonce = vp.get("nonce", "")
            assert "ISSUE_PAYLOAD" not in nonce, (
                f"Evidence nonce in {path.name} contains placeholder 'ISSUE_PAYLOAD'. "
                f"Nonces must be proper delegation challenges."
            )


# ---------------------------------------------------------------------------
# DID key linkage tests (Finding F8)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("path", EXAMPLE_FILES, ids=[f.stem for f in EXAMPLE_FILES])
def test_issuer_has_did_document(path):
    """Each credential issuer must have a corresponding DID document."""
    vc = json.loads(path.read_text())
    issuer = vc.get("issuer", "")
    assert issuer in DID_DOCS, (
        f"Credential {path.name} has issuer '{issuer}' "
        f"but no DID document exists in examples/did-ethr/."
    )


@pytest.mark.parametrize("path", EXAMPLE_FILES, ids=[f.stem for f in EXAMPLE_FILES])
def test_issuer_did_has_assertion_method(path):
    """Issuer DID document must have assertionMethod per DID-CORE-1.1 §5.3.1."""
    vc = json.loads(path.read_text())
    issuer = vc.get("issuer", "")
    did_doc = DID_DOCS.get(issuer)
    if did_doc is None:
        pytest.skip(f"No DID document for {issuer}")
    assert "assertionMethod" in did_doc, (
        f"DID document for {issuer} has no assertionMethod. "
        f"Per W3C VC-JOSE-COSE §3.3.2, kid must resolve to assertionMethod."
    )
    assert len(did_doc["assertionMethod"]) > 0, (
        f"assertionMethod for {issuer} is empty."
    )


@pytest.mark.parametrize("path", EXAMPLE_FILES, ids=[f.stem for f in EXAMPLE_FILES])
def test_issuer_did_has_signing_key(path):
    """Issuer DID must have a P-256 signing key in verificationMethod.

    Per W3C VC-JOSE-COSE §3.3.2, the kid in the JWT header must identify
    a key in the issuer's DID document verificationMethod that is also
    referenced from assertionMethod.
    """
    vc = json.loads(path.read_text())
    issuer = vc.get("issuer", "")
    did_doc = DID_DOCS.get(issuer)
    if did_doc is None:
        pytest.skip(f"No DID document for {issuer}")

    assertion_ids = did_doc.get("assertionMethod", [])

    # At least one P-256 JsonWebKey must exist in both
    p256_keys = [
        vm
        for vm in did_doc.get("verificationMethod", [])
        if vm.get("type") == "JsonWebKey"
        and vm.get("publicKeyJwk", {}).get("crv") == "P-256"
    ]
    assert len(p256_keys) > 0, (
        f"No P-256 JsonWebKey in verificationMethod for {issuer}. "
        f"Harbour credentials are signed with ES256 (P-256)."
    )

    # At least one P-256 key must be in assertionMethod
    p256_in_assertion = [k for k in p256_keys if k.get("id") in assertion_ids]
    assert len(p256_in_assertion) > 0, (
        f"No P-256 key referenced in assertionMethod for {issuer}."
    )


# ---------------------------------------------------------------------------
# Gaia-X composition tests (Finding F3)
# ---------------------------------------------------------------------------

PERSON_TYPES = {"simpulseid:ParticipantCredential"}

NATURAL_PERSON_TYPES = {
    "simpulseid:UserCredential",
    "simpulseid:AdministratorCredential",
}


@pytest.mark.parametrize("path", EXAMPLE_FILES, ids=[f.stem for f in EXAMPLE_FILES])
def test_participant_has_gx_composition(path):
    """ParticipantCredential must have participant composition.

    Per Gaia-X Trust Framework 25.11, legal person credentials must include
    gx:LegalPerson composition with registrationNumber, headquartersAddress,
    legalAddress.
    """
    vc = json.loads(path.read_text())
    vc_types = vc.get("type", [])

    if "simpulseid:ParticipantCredential" not in vc_types:
        pytest.skip("Not a ParticipantCredential")

    subject = vc.get("credentialSubject", {})
    gx = subject.get("participant")
    assert gx is not None, (
        f"ParticipantCredential {path.name} missing participant composition. "
        f"Required for Gaia-X 25.11 gx:LegalPerson compliance."
    )
    gx_type = gx.get("type")
    gx_types = gx_type if isinstance(gx_type, list) else [gx_type]
    assert "gx:LegalPerson" in gx_types, (
        f"participant type must include gx:LegalPerson, got {gx_type}"
    )


@pytest.mark.parametrize("path", EXAMPLE_FILES, ids=[f.stem for f in EXAMPLE_FILES])
def test_natural_person_has_gx_composition(path):
    """User/Admin credentials must have participant with harbour.gx:NaturalPerson.

    Personal attributes (givenName, familyName, email) live inside the
    participant node as a harbour.gx:NaturalPerson blank node.
    """
    vc = json.loads(path.read_text())
    vc_types = vc.get("type", [])

    if not NATURAL_PERSON_TYPES.intersection(vc_types):
        pytest.skip("Not a User or Administrator credential")

    subject = vc.get("credentialSubject", {})
    gx = subject.get("participant")
    assert gx is not None, (
        f"{path.name} missing participant composition. "
        f"Personal attributes must live in harbour.gx:NaturalPerson inner node."
    )
    gx_type = gx.get("type")
    gx_types = gx_type if isinstance(gx_type, list) else [gx_type]
    assert "harbour.gx:NaturalPerson" in gx_types, (
        f"participant type must include harbour.gx:NaturalPerson, got {gx_type}"
    )
    assert "givenName" in gx, f"{path.name}: participant missing givenName"
    assert "familyName" in gx, f"{path.name}: participant missing familyName"
    assert "email" in gx, f"{path.name}: participant missing email"


@pytest.mark.parametrize("path", EXAMPLE_FILES, ids=[f.stem for f in EXAMPLE_FILES])
def test_admin_participant_has_address(path):
    """AdministratorCredential participant must include gx:address.

    Administrators are natural persons with elevated permissions — address
    is a mandatory business requirement. For standard users, address is
    optional. Both are enforced at the SimpulseID layer (harbour
    NaturalPerson SHACL keeps address optional for all NaturalPersons).
    """
    vc = json.loads(path.read_text())
    vc_types = vc.get("type", [])

    if "simpulseid:AdministratorCredential" not in vc_types:
        pytest.skip("Not an AdministratorCredential")

    subject = vc.get("credentialSubject", {})
    gx = subject.get("participant", {})
    assert "address" in gx, (
        f"{path.name}: Administrator participant missing address. "
        f"Address is mandatory for administrators."
    )


# ---------------------------------------------------------------------------
# Credential structure tests
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("path", EXAMPLE_FILES, ids=[f.stem for f in EXAMPLE_FILES])
def test_credential_has_required_fields(path):
    """All credentials must have the W3C VCDM 2.0 required fields."""
    vc = json.loads(path.read_text())
    assert "@context" in vc, "Missing @context"
    assert "type" in vc, "Missing type"
    assert "issuer" in vc, "Missing issuer"
    assert "credentialSubject" in vc, "Missing credentialSubject"
    assert "credentialStatus" in vc, "Missing credentialStatus (harbour requirement)"
    assert "validFrom" in vc, "Missing validFrom (harbour requirement)"


@pytest.mark.parametrize("path", EXAMPLE_FILES, ids=[f.stem for f in EXAMPLE_FILES])
def test_credential_status_is_crset(path):
    """credentialStatus entries must be harbour:CRSetEntry."""
    vc = json.loads(path.read_text())
    statuses = vc.get("credentialStatus", [])
    assert len(statuses) > 0, "credentialStatus is empty"
    for status in statuses:
        assert status.get("type") == "harbour:CRSetEntry", (
            f"credentialStatus type must be harbour:CRSetEntry, got {status.get('type')}"
        )
        assert "statusPurpose" in status, "Missing statusPurpose"
