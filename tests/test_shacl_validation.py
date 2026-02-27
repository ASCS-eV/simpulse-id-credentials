"""SHACL validation tests for SimpulseID credentials.

Uses the ontology-management-base validation suite with harbour + simpulseid
artifacts registered, matching the Makefile validate target pattern.
"""

from pathlib import Path

import pytest

from src.tools.utils.registry_resolver import RegistryResolver
from src.tools.validators.shacl.validator import ShaclValidator

REPO_ROOT = Path(__file__).parent.parent.resolve()
OMB_ROOT = REPO_ROOT / "submodules" / "ontology-management-base"
HARBOUR_ARTIFACTS = REPO_ROOT / "submodules" / "harbour-credentials" / "artifacts"
SIMPULSEID_ARTIFACTS = REPO_ROOT / "artifacts"
EXAMPLES_DIR = REPO_ROOT / "examples"
INVALID_DIR = REPO_ROOT / "tests" / "data" / "invalid"


def _discover_files(directory: Path, pattern: str = "*.json") -> list[Path]:
    if not directory.exists():
        return []
    return sorted(directory.glob(pattern))


VALID_FILES = _discover_files(EXAMPLES_DIR, "simpulseid-*.json")
INVALID_FILES = _discover_files(INVALID_DIR)


@pytest.fixture(scope="module")
def shacl_validator():
    """Create a ShaclValidator with harbour + simpulseid artifacts registered."""
    resolver = RegistryResolver(root_dir=OMB_ROOT)
    resolver.register_artifact_directory(HARBOUR_ARTIFACTS)
    resolver.register_artifact_directory(SIMPULSEID_ARTIFACTS)
    return ShaclValidator(root_dir=OMB_ROOT, verbose=False, resolver=resolver)


@pytest.mark.parametrize(
    "jsonld_file",
    VALID_FILES,
    ids=[f.stem for f in VALID_FILES],
)
def test_valid_example_passes(shacl_validator, jsonld_file):
    """Valid example credentials should pass SHACL validation."""
    result = shacl_validator.validate([jsonld_file])
    assert result.conforms, (
        f"{jsonld_file.name} should conform but got violations:\n"
        f"{result.report_text}"
    )


@pytest.mark.parametrize(
    "jsonld_file",
    INVALID_FILES,
    ids=[f.stem for f in INVALID_FILES],
)
def test_invalid_example_fails(shacl_validator, jsonld_file):
    """Invalid credentials (missing required fields) should fail SHACL validation."""
    result = shacl_validator.validate([jsonld_file])
    assert (
        not result.conforms
    ), f"{jsonld_file.name} should have SHACL violations but passed"
