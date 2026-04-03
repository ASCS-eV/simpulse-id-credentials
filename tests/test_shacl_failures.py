"""SHACL validation failure tests — verify shapes catch invalid data.

Mutation-based testing: start from a known-good credential or DID fixture,
apply a single mutation, and assert that SHACL reports the expected violation
on the correct property path. Follows the harbour-credentials
test_shacl_failures.py pattern.

Validation uses the ``ShaclValidator`` from ontology-management-base —
the same pipeline as production (RDFS inference enabled).

Run with::

    pytest tests/test_shacl_failures.py -v

Requires generated artifacts (``make generate``) and the OMB submodule.
"""

import copy
import json
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pytest
import rdflib
from rdflib import RDF, Namespace
from src.tools.utils.registry_resolver import RegistryResolver
from src.tools.validators.shacl.validator import ShaclValidator

# ---------------------------------------------------------------------------
# Repository paths
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).parent.parent.resolve()
OMB_ROOT = (
    REPO_ROOT
    / "submodules"
    / "harbour-credentials"
    / "submodules"
    / "ontology-management-base"
)
HARBOUR_ARTIFACTS = REPO_ROOT / "submodules" / "harbour-credentials" / "artifacts"
SIMPULSEID_ARTIFACTS = REPO_ROOT / "artifacts"
EXAMPLES_DIR = REPO_ROOT / "examples"
DID_DIR = EXAMPLES_DIR / "did-ethr"

# SHACL namespaces for result graph queries
SH = Namespace("http://www.w3.org/ns/shacl#")
CRED = Namespace("https://www.w3.org/2018/credentials#")
SIMPULSEID = Namespace("https://w3id.org/ascs-ev/simpulse-id/v1/")
HARBOUR = Namespace("https://w3id.org/reachhaven/harbour/core/v1/")
DIDCORE = Namespace("https://www.w3.org/ns/did#")
SCHEMA = Namespace("https://schema.org/")

_skip_no_artifacts = pytest.mark.skipif(
    not (
        SIMPULSEID_ARTIFACTS / "simpulseid-core" / "simpulseid-core.shacl.ttl"
    ).exists(),
    reason="Generated artifacts not found — run 'make generate'",
)


# ---------------------------------------------------------------------------
# Structured violation helper
# ---------------------------------------------------------------------------


@dataclass
class ShaclViolation:
    """Human-readable representation of a single SHACL validation result."""

    focus_node: str
    result_path: Optional[str]
    constraint: str
    severity: str
    message: str

    def __str__(self) -> str:
        path_str = f" path={self.result_path}" if self.result_path else ""
        return (
            f"[{self.severity}]{path_str} constraint={self.constraint} — {self.message}"
        )


def _extract_violations(results_graph: rdflib.Graph) -> list[ShaclViolation]:
    """Extract structured violations from a pyshacl results graph."""
    violations = []
    for result in results_graph.subjects(RDF.type, SH.ValidationResult):
        paths = list(results_graph.objects(result, SH.resultPath))
        severities = list(results_graph.objects(result, SH.resultSeverity))
        components = list(results_graph.objects(result, SH.sourceConstraintComponent))
        messages = list(results_graph.objects(result, SH.resultMessage))
        focus_nodes = list(results_graph.objects(result, SH.focusNode))

        violations.append(
            ShaclViolation(
                focus_node=str(focus_nodes[0]) if focus_nodes else "?",
                result_path=str(paths[0]) if paths else None,
                constraint=(str(components[0]).split("#")[-1] if components else "?"),
                severity=(str(severities[0]).split("#")[-1] if severities else "?"),
                message=str(messages[0]) if messages else "(no message)",
            )
        )
    return violations


def _format_violations(violations: list[ShaclViolation]) -> str:
    if not violations:
        return "(no violations)"
    return "\n".join(f"  • {v}" for v in violations)


# ---------------------------------------------------------------------------
# Validation helper
# ---------------------------------------------------------------------------


def _validate(
    data: dict,
    validator: ShaclValidator,
) -> tuple[bool, list[ShaclViolation], str]:
    """Validate a JSON dict via the OMB ShaclValidator.

    Writes to a temp file and runs the full pipeline (context inlining,
    schema discovery, RDFS inference, SHACL validation).
    """
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
    ) as f:
        json.dump(data, f, ensure_ascii=False)
        temp_path = Path(f.name)

    try:
        result = validator.validate([temp_path])
        violations = (
            _extract_violations(result.report_graph)
            if result.report_graph is not None
            else []
        )
        return result.conforms, violations, result.report_text
    finally:
        temp_path.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Mutation helpers
# ---------------------------------------------------------------------------


def _load(name: str) -> dict:
    """Load an example by filename from examples/ or examples/did-ethr/."""
    for directory in [EXAMPLES_DIR, DID_DIR]:
        path = directory / name
        if path.exists():
            return json.loads(path.read_text())
    raise FileNotFoundError(f"Example not found: {name}")


def _remove_field(data: dict, *keys: str) -> dict:
    """Return a deep copy with a nested field removed."""
    data = copy.deepcopy(data)
    target = data
    for key in keys[:-1]:
        target = target[key]
    del target[keys[-1]]
    return data


def _set_field(data: dict, value, *keys: str) -> dict:
    """Return a deep copy with a nested field set to a new value."""
    data = copy.deepcopy(data)
    target = data
    for key in keys[:-1]:
        target = target[key]
    target[keys[-1]] = value
    return data


def _add_field(data: dict, value, *keys: str) -> dict:
    """Return a deep copy with a nested field added."""
    data = copy.deepcopy(data)
    target = data
    for key in keys[:-1]:
        target = target[key]
    target[keys[-1]] = value
    return data


# ---------------------------------------------------------------------------
# Session-scoped fixture
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def shacl_validator():
    """OMB ShaclValidator with harbour + simpulseid artifacts."""
    resolver = RegistryResolver(root_dir=OMB_ROOT)
    resolver.register_artifact_directory(HARBOUR_ARTIFACTS)
    resolver.register_artifact_directory(SIMPULSEID_ARTIFACTS)
    return ShaclValidator(
        root_dir=OMB_ROOT,
        inference_mode="rdfs",
        verbose=False,
        resolver=resolver,
    )


# ═══════════════════════════════════════════════════════════════════════════
# Positive baselines
# ═══════════════════════════════════════════════════════════════════════════


_CREDENTIAL_FILES = sorted(EXAMPLES_DIR.glob("simpulseid-*.json"))
_DID_FILES = sorted(DID_DIR.glob("*.json"))


@_skip_no_artifacts
class TestPositiveBaseline:
    """Sanity check — valid examples must pass before we test mutations."""

    @pytest.mark.parametrize(
        "path", _CREDENTIAL_FILES, ids=[f.stem for f in _CREDENTIAL_FILES]
    )
    def test_valid_credential(self, path, shacl_validator):
        cred = json.loads(path.read_text())
        conforms, violations, text = _validate(cred, shacl_validator)
        assert conforms, (
            f"{path.name} should conform:\n{_format_violations(violations)}"
        )

    @pytest.mark.parametrize("path", _DID_FILES, ids=[f.stem for f in _DID_FILES])
    def test_valid_did(self, path, shacl_validator):
        doc = json.loads(path.read_text())
        conforms, violations, text = _validate(doc, shacl_validator)
        assert conforms, (
            f"{path.name} should conform:\n{_format_violations(violations)}"
        )


# ═══════════════════════════════════════════════════════════════════════════
# C1: Missing mandatory fields  (MinCountConstraintComponent)
# ═══════════════════════════════════════════════════════════════════════════

# (example_file, field_path_to_remove, expected_shacl_path_str, test_id)
_MISSING_FIELD_CASES = [
    # --- ParticipantCredential envelope ---
    (
        "simpulseid-participant-credential.json",
        ("issuer",),
        str(CRED.issuer),
        "Participant-missing-issuer",
    ),
    (
        "simpulseid-participant-credential.json",
        ("validFrom",),
        str(CRED.validFrom),
        "Participant-missing-validFrom",
    ),
    (
        "simpulseid-participant-credential.json",
        ("credentialStatus",),
        str(CRED.credentialStatus),
        "Participant-missing-credentialStatus",
    ),
    # --- Participant subject ---
    # NOTE: Participant-missing-harbourCredential is tested separately as xfail
    # (see TestParticipantShapeGap below).
    # --- AdministratorCredential ---
    (
        "simpulseid-administrator-credential.json",
        ("credentialSubject", "harbourCredential"),
        str(SIMPULSEID.harbourCredential),
        "Administrator-missing-harbourCredential",
    ),
    # --- UserCredential ---
    (
        "simpulseid-user-credential.json",
        ("credentialSubject", "harbourCredential"),
        str(SIMPULSEID.harbourCredential),
        "User-missing-harbourCredential",
    ),
    # --- AscsBaseMembershipCredential ---
    (
        "simpulseid-ascs-base-membership-credential.json",
        ("credentialSubject", "member"),
        str(SCHEMA.member),
        "BaseMembership-missing-member",
    ),
    # --- AscsEnvitedMembershipCredential ---
    (
        "simpulseid-ascs-envited-membership-credential.json",
        ("credentialSubject", "member"),
        str(SCHEMA.member),
        "EnvitedMembership-missing-member",
    ),
    (
        "simpulseid-ascs-envited-membership-credential.json",
        ("credentialSubject", "baseMembershipCredential"),
        str(SIMPULSEID.baseMembershipCredential),
        "EnvitedMembership-missing-baseMembershipCredential",
    ),
]


@_skip_no_artifacts
class TestMissingMandatoryFields:
    """Removing a required field must trigger MinCountConstraintComponent."""

    @pytest.mark.parametrize(
        "example_file, field_path, expected_path, test_id",
        _MISSING_FIELD_CASES,
        ids=[c[3] for c in _MISSING_FIELD_CASES],
    )
    def test_missing_field_detected(
        self, example_file, field_path, expected_path, test_id, shacl_validator
    ):
        cred = _load(example_file)
        mutated = _remove_field(cred, *field_path)

        conforms, violations, text = _validate(mutated, shacl_validator)

        assert not conforms, (
            f"[{test_id}] Should FAIL without '{'.'.join(field_path)}' "
            f"but SHACL said it conforms."
        )

        min_count_on_path = [
            v
            for v in violations
            if v.constraint == "MinCountConstraintComponent"
            and v.result_path == expected_path
        ]
        assert min_count_on_path, (
            f"[{test_id}] Expected MinCountConstraintComponent on "
            f"<{expected_path}> but got:\n"
            f"{_format_violations(violations)}\n\nFull report:\n{text}"
        )


# ═══════════════════════════════════════════════════════════════════════════
# C2: Closed shape violations  (ClosedConstraintComponent)
# ═══════════════════════════════════════════════════════════════════════════

# (example_file, field_path_to_add, field_value, test_id)
_CLOSED_SHAPE_CASES = [
    # Unexpected top-level credential property
    (
        "simpulseid-participant-credential.json",
        ("unknownField",),
        "surprise!",
        "ParticipantCredential-unexpected-property",
    ),
    # NOTE: Participant-subject-unexpected-property is tested separately as xfail
    # (see TestParticipantShapeGap below).
    # Unexpected property on Administrator subject
    (
        "simpulseid-administrator-credential.json",
        ("credentialSubject", "extraData"),
        {"foo": "bar"},
        "Administrator-subject-unexpected-property",
    ),
    # Unexpected property on BaseMembership subject
    (
        "simpulseid-ascs-base-membership-credential.json",
        ("credentialSubject", "bogus"),
        "oops",
        "BaseMembership-subject-unexpected-property",
    ),
]


@_skip_no_artifacts
class TestClosedShapeViolations:
    """Adding an unexpected property to a closed shape must be caught."""

    @pytest.mark.parametrize(
        "example_file, field_path, field_value, test_id",
        _CLOSED_SHAPE_CASES,
        ids=[c[3] for c in _CLOSED_SHAPE_CASES],
    )
    def test_unexpected_property_detected(
        self, example_file, field_path, field_value, test_id, shacl_validator
    ):
        cred = _load(example_file)
        mutated = _add_field(cred, field_value, *field_path)

        conforms, violations, text = _validate(mutated, shacl_validator)

        assert not conforms, (
            f"[{test_id}] Should FAIL with unexpected property but conforms.\n"
            f"Check that the shape has sh:closed true."
        )

        closed = [v for v in violations if v.constraint == "ClosedConstraintComponent"]
        assert closed, (
            f"[{test_id}] Expected ClosedConstraintComponent but got:\n"
            f"{_format_violations(violations)}\n\nFull report:\n{text}"
        )


# ═══════════════════════════════════════════════════════════════════════════
# C3: DID fixture mutations
# ═══════════════════════════════════════════════════════════════════════════


@_skip_no_artifacts
class TestDIDMutations:
    """Mutation tests for DID document SHACL shapes."""

    def test_program_did_missing_service_endpoint(self, shacl_validator):
        """ProgramMetadataService requires serviceEndpoint (minCount 1)."""
        doc = _load("simpulseid-program-administrator-did.json")
        del doc["service"][0]["serviceEndpoint"]

        conforms, violations, text = _validate(doc, shacl_validator)

        assert not conforms, "Should FAIL without serviceEndpoint but conforms."
        min_count = [
            v
            for v in violations
            if v.constraint == "MinCountConstraintComponent"
            and v.result_path == str(DIDCORE.serviceEndpoint)
        ]
        assert min_count, (
            f"Expected MinCount on didcore:serviceEndpoint but got:\n"
            f"{_format_violations(violations)}\n\nFull report:\n{text}"
        )

    def test_program_did_unexpected_service_property(self, shacl_validator):
        """ProgramMetadataService is closed — unexpected properties caught."""
        doc = _load("simpulseid-program-administrator-did.json")
        doc["service"][0]["bogusProperty"] = "unexpected"

        conforms, violations, text = _validate(doc, shacl_validator)

        assert not conforms, (
            "Should FAIL with unexpected service property but conforms."
        )
        closed = [v for v in violations if v.constraint == "ClosedConstraintComponent"]
        assert closed, (
            f"Expected ClosedConstraintComponent but got:\n"
            f"{_format_violations(violations)}\n\nFull report:\n{text}"
        )

    def test_participant_did_organization_unexpected_property(self, shacl_validator):
        """Organization endpoint is closed — unexpected properties caught."""
        doc = _load("simpulseid-participant-ascs-did.json")
        doc["service"][0]["serviceEndpoint"]["unknownProp"] = "oops"

        conforms, violations, text = _validate(doc, shacl_validator)

        assert not conforms, (
            "Should FAIL with unexpected Organization property but conforms."
        )
        closed = [v for v in violations if v.constraint == "ClosedConstraintComponent"]
        assert closed, (
            f"Expected ClosedConstraintComponent but got:\n"
            f"{_format_violations(violations)}\n\nFull report:\n{text}"
        )

    def test_participant_did_missing_trust_anchor_endpoint(self, shacl_validator):
        """TrustAnchorService requires serviceEndpoint (minCount 1)."""
        doc = _load("simpulseid-participant-ascs-did.json")
        del doc["service"][0]["serviceEndpoint"]

        conforms, violations, text = _validate(doc, shacl_validator)

        assert not conforms, (
            "Should FAIL without TrustAnchor serviceEndpoint but conforms."
        )
        min_count = [
            v
            for v in violations
            if v.constraint == "MinCountConstraintComponent"
            and v.result_path == str(DIDCORE.serviceEndpoint)
        ]
        assert min_count, (
            f"Expected MinCount on didcore:serviceEndpoint but got:\n"
            f"{_format_violations(violations)}\n\nFull report:\n{text}"
        )


# ═══════════════════════════════════════════════════════════════════════════
# C5: Participant subject shape (previously broken — see issue #28)
# ═══════════════════════════════════════════════════════════════════════════
#
# The Participant shape requires class_uri: simpulseid:SimpulseidParticipant
# (not simpulseid:Participant) to avoid a JSON-LD context collision with
# gx:Participant from the Gaia-X imports.


_PARTICIPANT_MISSING_CASES = [
    (
        "simpulseid-participant-credential.json",
        ("credentialSubject", "harbourCredential"),
        str(SIMPULSEID.harbourCredential),
        "Participant-missing-harbourCredential",
    ),
]


@_skip_no_artifacts
class TestParticipantSubjectShape:
    """Participant subject shape constraints."""

    @pytest.mark.parametrize(
        "example_file, field_path, expected_path, test_id",
        _PARTICIPANT_MISSING_CASES,
        ids=[c[3] for c in _PARTICIPANT_MISSING_CASES],
    )
    def test_participant_missing_field(
        self, example_file, field_path, expected_path, test_id, shacl_validator
    ):
        """Removing a required Participant field triggers MinCount."""
        cred = _load(example_file)
        mutated = _remove_field(cred, *field_path)

        conforms, violations, text = _validate(mutated, shacl_validator)

        assert not conforms, (
            f"[{test_id}] Should FAIL without '{'.'.join(field_path)}' "
            f"but SHACL said it conforms."
        )
        min_count = [
            v
            for v in violations
            if v.constraint == "MinCountConstraintComponent"
            and v.result_path == expected_path
        ]
        assert min_count, (
            f"[{test_id}] Expected MinCountConstraintComponent on "
            f"<{expected_path}> but got:\n"
            f"{_format_violations(violations)}\n\nFull report:\n{text}"
        )

    def test_participant_subject_unexpected_property(self, shacl_validator):
        """Adding a bogus field to Participant subject triggers Closed."""
        cred = _load("simpulseid-participant-credential.json")
        mutated = _add_field(cred, "unexpected", "credentialSubject", "bogusField")

        conforms, violations, text = _validate(mutated, shacl_validator)

        assert not conforms, (
            "Should FAIL with unexpected property but conforms.\n"
            "Check that the shape has sh:closed true."
        )
        closed = [v for v in violations if v.constraint == "ClosedConstraintComponent"]
        assert closed, (
            f"Expected ClosedConstraintComponent but got:\n"
            f"{_format_violations(violations)}\n\nFull report:\n{text}"
        )
