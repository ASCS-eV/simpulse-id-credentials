"""Generate signed VC-JOSE-COSE JWT artifacts from example credentials.

Reads expanded (human-readable) examples from examples/*.json and
examples/gaiax/*.json, then produces wire-format signed JWTs plus
decoded companion files in examples/signed/.

Output per credential:
  - <name>.jwt                      — VC-JOSE-COSE compact JWS (wire format)
  - <name>.decoded.json             — Decoded JWT header + payload
  - <name>.evidence-vp.jwt          — Evidence VP JWT (if evidence present)
  - <name>.evidence-vp.decoded.json — Decoded evidence VP with inner VCs decoded

Source examples are NEVER modified.
"""

import base64
import copy
import json
import sys
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ec import (
    SECP256R1,
    EllipticCurvePrivateNumbers,
    EllipticCurvePublicNumbers,
)
from harbour.keys import p256_public_key_to_did_key
from harbour.signer import sign_vc_jose, sign_vp_jose

REPO_ROOT = Path(__file__).resolve().parent.parent
EXAMPLES_DIR = REPO_ROOT / "examples"
SIGNED_DIR = EXAMPLES_DIR / "signed"
FIXTURES_DIR = REPO_ROOT / "submodules" / "harbour-credentials" / "tests" / "fixtures"


def _b64url_decode(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def _decode_jwt(token: str) -> dict:
    """Decode a JWT into header and payload (no verification)."""
    parts = token.split(".")
    header = json.loads(_b64url_decode(parts[0]))
    payload = json.loads(_b64url_decode(parts[1]))
    return {"header": header, "payload": payload}


def load_test_p256_keypair():
    """Load the committed P-256 test keypair."""
    jwk_path = FIXTURES_DIR / "keys" / "test-keypair-p256.json"
    jwk = json.loads(jwk_path.read_text())
    x = int.from_bytes(_b64url_decode(jwk["x"]), "big")
    y = int.from_bytes(_b64url_decode(jwk["y"]), "big")
    d = int.from_bytes(_b64url_decode(jwk["d"]), "big")
    pub_numbers = EllipticCurvePublicNumbers(x, y, SECP256R1())
    priv_numbers = EllipticCurvePrivateNumbers(d, pub_numbers)
    private_key = priv_numbers.private_key()
    return private_key, private_key.public_key()


def sign_evidence_vp(vp: dict, private_key, kid: str) -> str:
    """Sign an evidence VP and its inner VCs as VC-JOSE-COSE JWTs.

    Takes the expanded VP object, signs each inner VC, replaces them with
    JWT strings, then signs the VP envelope.
    """
    clean_vp = {
        "@context": vp.get("@context", ["https://www.w3.org/ns/credentials/v2"]),
        "type": vp.get("type", ["VerifiablePresentation"]),
    }

    if "holder" in vp:
        clean_vp["holder"] = vp["holder"]

    # Sign inner VCs
    inner_vcs = vp.get("verifiableCredential", [])
    inner_jwts = []
    for vc in inner_vcs:
        if isinstance(vc, dict):
            inner_jwt = sign_vc_jose(vc, private_key, kid=kid)
            inner_jwts.append(inner_jwt)
        else:
            # Already a JWT string
            inner_jwts.append(vc)
    if inner_jwts:
        clean_vp["verifiableCredential"] = inner_jwts

    nonce = vp.get("nonce")
    return sign_vp_jose(clean_vp, private_key, kid=kid, nonce=nonce)


def decode_evidence_vp(vp_jwt: str) -> dict:
    """Decode an evidence VP JWT with nested inner VC JWTs decoded inline."""
    decoded = _decode_jwt(vp_jwt)
    inner_vcs = decoded["payload"].get("verifiableCredential", [])
    decoded_inners = []
    for inner in inner_vcs:
        if isinstance(inner, str) and "." in inner:
            inner_decoded = _decode_jwt(inner)
            decoded_inners.append(
                {
                    "_jwt": inner,
                    "_decoded": inner_decoded,
                }
            )
        else:
            decoded_inners.append(inner)
    if decoded_inners:
        decoded["payload"]["verifiableCredential"] = decoded_inners
    return decoded


def discover_examples() -> list[tuple[Path, str]]:
    """Discover example credentials from examples/.

    Returns list of (path, prefix) tuples. Prefix is used for output naming.
    """
    return [(f, f.stem) for f in sorted(EXAMPLES_DIR.glob("simpulseid-*.json"))]


def process_example(example_path: Path, output_prefix: str, private_key, kid: str):
    """Process a single example credential.

    Reads the expanded example, signs evidence and outer VC, writes all
    artifacts to examples/signed/. Never modifies the source file.
    """
    vc = json.loads(example_path.read_text())

    evidence_vp_jwt = None

    # Sign evidence VPs if present (work on a copy for outer signing)
    vc_for_signing = copy.deepcopy(vc)
    if "evidence" in vc_for_signing:
        for ev in vc_for_signing["evidence"]:
            vp_obj = ev.get("verifiablePresentation")
            if isinstance(vp_obj, dict):
                # Expanded VP — sign it
                evidence_vp_jwt = sign_evidence_vp(vp_obj, private_key, kid)
                # Replace with JWT string for outer VC signing
                ev["verifiablePresentation"] = evidence_vp_jwt

    # Sign the outer credential
    vc_jwt = sign_vc_jose(vc_for_signing, private_key, kid=kid)

    # Write outputs
    SIGNED_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Outer VC JWT
    jwt_path = SIGNED_DIR / f"{output_prefix}.jwt"
    jwt_path.write_text(vc_jwt + "\n")

    # 2. Decoded outer JWT
    decoded = _decode_jwt(vc_jwt)
    decoded_path = SIGNED_DIR / f"{output_prefix}.decoded.json"
    decoded_obj = {
        "_description": f"Decoded VC-JOSE-COSE JWT for {output_prefix}",
        **decoded,
    }
    decoded_path.write_text(
        json.dumps(decoded_obj, indent=2, ensure_ascii=False) + "\n"
    )

    # 3. Evidence VP JWT (if applicable)
    if evidence_vp_jwt:
        ev_jwt_path = SIGNED_DIR / f"{output_prefix}.evidence-vp.jwt"
        ev_jwt_path.write_text(evidence_vp_jwt + "\n")

        # 4. Decoded evidence VP
        ev_decoded = decode_evidence_vp(evidence_vp_jwt)
        ev_decoded_path = SIGNED_DIR / f"{output_prefix}.evidence-vp.decoded.json"
        ev_decoded_obj = {
            "_description": f"Decoded evidence VP JWT for {output_prefix}",
            **ev_decoded,
        }
        ev_decoded_path.write_text(
            json.dumps(ev_decoded_obj, indent=2, ensure_ascii=False) + "\n"
        )

    return jwt_path


def main():
    private_key, public_key = load_test_p256_keypair()
    kid = p256_public_key_to_did_key(public_key)
    kid_vm = f"{kid}#{kid.split(':')[-1]}"

    # Find all example credentials
    examples = discover_examples()
    if not examples:
        print("No example credentials found in examples/", file=sys.stderr)
        sys.exit(1)

    print(f"Signing {len(examples)} example credentials with test P-256 key...")
    print(f"  kid: {kid_vm}")

    for path, prefix in examples:
        jwt_path = process_example(path, prefix, private_key, kid_vm)
        print(f"  {path.relative_to(REPO_ROOT)} -> {jwt_path.relative_to(REPO_ROOT)}")

    # List all generated files
    signed_files = sorted(SIGNED_DIR.iterdir())
    print(f"\nGenerated {len(signed_files)} files in examples/signed/:")
    for f in signed_files:
        print(f"  {f.name}")

    print("Done.")


if __name__ == "__main__":
    main()
