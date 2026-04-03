"""Tests for example credential integrity and chain-of-trust properties.

Validates that example credentials meet the requirements for a verifiable,
auditable chain of trust per:
- W3C VC-JOSE-COSE §3.3.2 (kid → assertionMethod resolution)
- W3C DID-CORE §5.3, §5.4 (DID document structure)
- W3C VCDM 2.0 §4.1 (@context completeness)
- OID4VP §8.4 (delegation challenge nonce format)
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
    """Load all DID document JSON files, keyed by DID id."""
    docs = {}
    for f in sorted(DID_ETHR_DIR.glob("*.json")):
        data = json.loads(f.read_text())
        did_id = data.get("id", "")
        docs[did_id] = data
    return docs


def _load_all_did_files():
    """Return DID fixture paths grouped by role."""
    return sorted(DID_ETHR_DIR.glob("*.json"))


def _load_credential_ids():
    """Return the set of credential ids from all example files."""
    ids = set()
    for f in EXAMPLES_DIR.glob("simpulseid-*.json"):
        data = json.loads(f.read_text())
        cred_id = data.get("id")
        if cred_id:
            ids.add(cred_id)
    return ids


EXAMPLE_FILES = _load_all_examples()
DID_DOCS = _load_all_did_docs()
DID_FILES = _load_all_did_files()
CREDENTIAL_IDS = _load_credential_ids()

SIGNER_DID_FILES = sorted(
    list(DID_ETHR_DIR.glob("simpulseid-participant-*-did.json"))
    + list(DID_ETHR_DIR.glob("simpulseid-user-*-did.json"))
)
RESOURCE_DID_FILES = sorted(
    list(DID_ETHR_DIR.glob("simpulseid-program-*-did.json"))
    + list(DID_ETHR_DIR.glob("simpulseid-service-*-did.json"))
)
PROGRAM_DID_FILES = sorted(DID_ETHR_DIR.glob("simpulseid-program-*-did.json"))


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


# ---------------------------------------------------------------------------
# Cross-document IRI resolution tests
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("path", EXAMPLE_FILES, ids=[f.stem for f in EXAMPLE_FILES])
def test_subject_did_has_document(path):
    """Credential subjects with did: identifiers must have DID documents."""
    vc = json.loads(path.read_text())
    subject_id = vc.get("credentialSubject", {}).get("id", "")
    if not subject_id.startswith("did:"):
        pytest.skip("Subject uses urn:uuid: (membership relationship)")
    assert subject_id in DID_DOCS, (
        f"Subject DID {subject_id} in {path.name} has no DID document "
        f"in examples/did-ethr/."
    )


@pytest.mark.parametrize("path", EXAMPLE_FILES, ids=[f.stem for f in EXAMPLE_FILES])
def test_member_of_references_resolve(path):
    """memberOf IRI references must point to known ecosystem entities."""
    vc = json.loads(path.read_text())
    member_of = vc.get("credentialSubject", {}).get("memberOf", [])
    if not member_of:
        pytest.skip("No memberOf in this credential")
    for ref in member_of:
        assert ref in DID_DOCS, (
            f"memberOf reference {ref} in {path.name} has no DID document."
        )


@pytest.mark.parametrize("path", EXAMPLE_FILES, ids=[f.stem for f in EXAMPLE_FILES])
def test_hosting_organization_resolves(path):
    """hostingOrganization must point to a known participant DID."""
    vc = json.loads(path.read_text())
    host = vc.get("credentialSubject", {}).get("hostingOrganization")
    if host is None:
        pytest.skip("No hostingOrganization in this credential")
    assert isinstance(host, str), (
        f"hostingOrganization in {path.name} must be a plain URI string, "
        f"got {type(host).__name__}"
    )
    assert host in DID_DOCS, (
        f"hostingOrganization {host} in {path.name} has no DID document."
    )


@pytest.mark.parametrize("path", EXAMPLE_FILES, ids=[f.stem for f in EXAMPLE_FILES])
def test_member_reference_resolves(path):
    """member (schema:member) must point to a known participant DID."""
    vc = json.loads(path.read_text())
    member = vc.get("credentialSubject", {}).get("member")
    if member is None:
        pytest.skip("No member in this credential")
    assert member in DID_DOCS, f"member {member} in {path.name} has no DID document."


@pytest.mark.parametrize("path", EXAMPLE_FILES, ids=[f.stem for f in EXAMPLE_FILES])
def test_base_membership_credential_resolves(path):
    """baseMembershipCredential must reference a known credential id."""
    vc = json.loads(path.read_text())
    base_ref = vc.get("credentialSubject", {}).get("baseMembershipCredential")
    if base_ref is None:
        pytest.skip("No baseMembershipCredential in this credential")
    assert base_ref in CREDENTIAL_IDS, (
        f"baseMembershipCredential {base_ref} in {path.name} does not match "
        f"any credential id. Known ids: {CREDENTIAL_IDS}"
    )


REVOCATION_REGISTRY_DID = "did:ethr:0x14a34:0x4612FbF84Ef87dfBc363c6077235A475502346d1"


@pytest.mark.parametrize("path", EXAMPLE_FILES, ids=[f.stem for f in EXAMPLE_FILES])
def test_credential_status_registry_resolves(path):
    """credentialStatus id prefix must match the revocation registry DID."""
    vc = json.loads(path.read_text())
    for status in vc.get("credentialStatus", []):
        status_id = status.get("id", "")
        assert status_id.startswith(REVOCATION_REGISTRY_DID), (
            f"credentialStatus id '{status_id}' in {path.name} does not start "
            f"with revocation registry DID {REVOCATION_REGISTRY_DID}"
        )
    assert REVOCATION_REGISTRY_DID in DID_DOCS, (
        f"Revocation registry DID {REVOCATION_REGISTRY_DID} has no DID document."
    )


# ---------------------------------------------------------------------------
# DID document structural invariant tests
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "path", SIGNER_DID_FILES, ids=[f.stem for f in SIGNER_DID_FILES]
)
def test_signer_did_has_verification_method(path):
    """Signer DIDs (participants, users) must expose local P-256 keys.

    Per DID-CORE §5.3.1, signer DIDs must have verificationMethod with
    at least one JsonWebKey, referenced from both authentication and
    assertionMethod. They must NOT have a controller (self-sovereign).
    """
    doc = json.loads(path.read_text())

    assert "controller" not in doc, (
        f"Signer DID {path.name} must not have a controller (self-sovereign)."
    )

    vms = doc.get("verificationMethod", [])
    assert len(vms) > 0, f"Signer DID {path.name} has no verificationMethod."

    p256_keys = [
        vm
        for vm in vms
        if vm.get("type") == "JsonWebKey"
        and vm.get("publicKeyJwk", {}).get("crv") == "P-256"
    ]
    assert len(p256_keys) > 0, f"Signer DID {path.name} has no P-256 JsonWebKey."

    auth = doc.get("authentication", [])
    assertion = doc.get("assertionMethod", [])
    assert len(auth) > 0, f"Signer DID {path.name} has no authentication."
    assert len(assertion) > 0, f"Signer DID {path.name} has no assertionMethod."

    key_ids = {vm["id"] for vm in p256_keys}
    assert key_ids & set(auth), (
        f"No P-256 key referenced in authentication for {path.name}."
    )
    assert key_ids & set(assertion), (
        f"No P-256 key referenced in assertionMethod for {path.name}."
    )


@pytest.mark.parametrize(
    "path", RESOURCE_DID_FILES, ids=[f.stem for f in RESOURCE_DID_FILES]
)
def test_resource_did_has_controller(path):
    """Resource DIDs (programs, services) must be externally controlled.

    Per DID-CORE §5.1.2, resource DIDs use the controller property to
    delegate authority. They must NOT have local verificationMethod.
    The controller must reference a known participant DID.
    """
    doc = json.loads(path.read_text())

    controller = doc.get("controller")
    assert controller is not None, f"Resource DID {path.name} must have a controller."
    assert controller in DID_DOCS, (
        f"Controller {controller} in {path.name} has no DID document."
    )

    assert "verificationMethod" not in doc, (
        f"Resource DID {path.name} must not have local verificationMethod "
        f"(externally controlled)."
    )


@pytest.mark.parametrize(
    "path", PROGRAM_DID_FILES, ids=[f.stem for f in PROGRAM_DID_FILES]
)
def test_program_did_has_metadata_service(path):
    """Program DIDs must expose a ProgramMetadataService endpoint.

    The service must have a serviceEndpoint with an @id (IRI node)
    pointing to the program metadata URL.
    """
    doc = json.loads(path.read_text())

    services = doc.get("service", [])
    pms = [s for s in services if s.get("type") == "ProgramMetadataService"]
    assert len(pms) == 1, (
        f"Program DID {path.name} must have exactly one ProgramMetadataService, "
        f"found {len(pms)}."
    )

    endpoint = pms[0].get("serviceEndpoint")
    assert endpoint is not None, (
        f"ProgramMetadataService in {path.name} has no serviceEndpoint."
    )


# ---------------------------------------------------------------------------
# DID document IRI type pollution regression guard (issue #28)
# ---------------------------------------------------------------------------


def _walk_objects(data, path=""):
    """Yield (json_path, obj) for every dict in the JSON tree."""
    if isinstance(data, dict):
        yield path, data
        for k, v in data.items():
            yield from _walk_objects(v, f"{path}.{k}")
    elif isinstance(data, list):
        for i, v in enumerate(data):
            yield from _walk_objects(v, f"{path}[{i}]")


@pytest.mark.parametrize("path", DID_FILES, ids=[f.stem for f in DID_FILES])
def test_did_no_iri_type_pollution(path):
    """DID documents must not assert @type on external DID IRIs.

    An expanded JSON-LD object with both @id (pointing to another entity's
    DID) and @type creates rdf:type triples on that external IRI. When
    loaded into the same graph as the target entity's DID document, the
    closed SHACL shapes on the external type reject the DID properties.

    This is the exact bug fixed in issue #28.
    """
    doc = json.loads(path.read_text())
    doc_id = doc.get("id", "")

    for json_path, obj in _walk_objects(doc):
        obj_id = obj.get("@id", "")
        obj_type = obj.get("@type")
        if not obj_id.startswith("did:"):
            continue
        if obj_id == doc_id:
            continue
        assert obj_type is None, (
            f"{path.name} at {json_path}: object with @id={obj_id} also has "
            f"@type={obj_type}. This pollutes the external DID's rdf:type in "
            f"the merged graph. Use a plain URI string instead."
        )
