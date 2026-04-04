"""Shared fixtures for credentials repo tests."""

import base64
import json
from pathlib import Path

import pytest
from cryptography.hazmat.primitives.asymmetric.ec import (
    SECP256R1,
    EllipticCurvePrivateNumbers,
    EllipticCurvePublicNumbers,
)
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from harbour.keys import p256_public_key_to_did_key, public_key_to_did_key

EXAMPLES_DIR = Path(__file__).parent.parent / "examples"
HARBOUR_FIXTURES_DIR = (
    Path(__file__).parent.parent
    / "submodules"
    / "harbour-credentials"
    / "tests"
    / "fixtures"
)


def _b64url_decode(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


# ---------------------------------------------------------------------------
# Ed25519 fixtures (legacy)
# ---------------------------------------------------------------------------


def _load_ed25519_keypair():
    """Load the committed Ed25519 test keypair from harbour fixtures."""
    jwk_path = HARBOUR_FIXTURES_DIR / "keys" / "test-keypair.json"
    with open(jwk_path) as f:
        jwk = json.load(f)
    raw_private = _b64url_decode(jwk["d"])
    private_key = Ed25519PrivateKey.from_private_bytes(raw_private)
    return private_key, private_key.public_key()


@pytest.fixture(scope="session")
def ed25519_keypair():
    return _load_ed25519_keypair()


@pytest.fixture(scope="session")
def private_key(ed25519_keypair):
    return ed25519_keypair[0]


@pytest.fixture(scope="session")
def public_key(ed25519_keypair):
    return ed25519_keypair[1]


@pytest.fixture(scope="session")
def did_key_vm(public_key):
    did = public_key_to_did_key(public_key)
    fragment = did.split(":")[-1]
    return f"{did}#{fragment}"


# ---------------------------------------------------------------------------
# P-256 fixtures
# ---------------------------------------------------------------------------


def _load_p256_keypair():
    """Load the committed P-256 test keypair from harbour fixtures."""
    jwk_path = HARBOUR_FIXTURES_DIR / "keys" / "test-keypair-p256.json"
    with open(jwk_path) as f:
        jwk = json.load(f)
    x = int.from_bytes(_b64url_decode(jwk["x"]), "big")
    y = int.from_bytes(_b64url_decode(jwk["y"]), "big")
    d = int.from_bytes(_b64url_decode(jwk["d"]), "big")
    pub_numbers = EllipticCurvePublicNumbers(x, y, SECP256R1())
    priv_numbers = EllipticCurvePrivateNumbers(d, pub_numbers)
    private_key = priv_numbers.private_key()
    return private_key, private_key.public_key()


@pytest.fixture(scope="session")
def p256_keypair():
    return _load_p256_keypair()


@pytest.fixture(scope="session")
def p256_private_key(p256_keypair):
    return p256_keypair[0]


@pytest.fixture(scope="session")
def p256_public_key(p256_keypair):
    return p256_keypair[1]


@pytest.fixture(scope="session")
def p256_did_key_vm(p256_public_key):
    did = p256_public_key_to_did_key(p256_public_key)
    fragment = did.split(":")[-1]
    return f"{did}#{fragment}"


# ---------------------------------------------------------------------------
# Example credential discovery
# ---------------------------------------------------------------------------


def _discover_example_files():
    """Discover all JSON example files for parametrized tests."""
    if not EXAMPLES_DIR.exists():
        return []
    return sorted(EXAMPLES_DIR.glob("simpulseid-*.json"))


EXAMPLE_FILES = _discover_example_files()


@pytest.fixture(params=EXAMPLE_FILES, ids=[f.stem for f in EXAMPLE_FILES])
def example_vc(request):
    """Load an example VC from examples/ directory."""
    path = request.param
    with open(path) as f:
        return json.load(f)


def _discover_signed_files():
    """Discover signed VC JWT files (excludes evidence VP JWTs)."""
    signed_dir = EXAMPLES_DIR / "signed"
    if not signed_dir.exists():
        return []
    return sorted(f for f in signed_dir.glob("*.jwt") if ".evidence-vp." not in f.name)


SIGNED_FILES = _discover_signed_files()


@pytest.fixture(params=SIGNED_FILES, ids=[f.stem for f in SIGNED_FILES])
def signed_jwt(request):
    """Load a signed JWT from examples/signed/."""
    return request.param.read_text().strip()
