"""Generate signed VC-JOSE-COSE JWT artifacts from example credentials.

Reads expanded (human-readable) examples from examples/*.json, then produces
wire-format signed JWTs plus decoded companion files in examples/signed/.

Output per credential:
  - <name>.jwt                      — VC-JOSE-COSE compact JWS (wire format)
  - <name>.decoded.json             — Decoded JWT header + payload
  - <name>.evidence-vp.jwt          — Evidence VP JWT (if evidence present)
  - <name>.evidence-vp.decoded.json — Decoded evidence VP

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
from harbour.delegation import TransactionData, create_delegation_challenge
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


def sign_evidence_vp(vp: dict, private_key, kid: str, vc_payload: dict) -> str:
    """Sign an evidence VP as a VC-JOSE-COSE JWT.

    Takes the expanded VP object (empty VP with holder + nonce, no inner VCs)
    and signs it. Uses the harbour delegation module to create a proper
    challenge nonce per EVES-009 / OID4VP §8.4.

    The challenge format is: <nonce> HARBOUR_DELEGATE <sha256-hash>
    where the hash covers the credential payload being consented to.
    """
    clean_vp = {
        "@context": vp.get("@context", ["https://www.w3.org/ns/credentials/v2"]),
        "type": vp.get("type", ["VerifiablePresentation"]),
    }

    if "holder" in vp:
        clean_vp["holder"] = vp["holder"]

    # Build transaction data for the credential issuance consent
    credential_id = vc_payload.get("id", "default")
    tx = TransactionData.create(
        action="credential.issue",
        txn={"credentialId": credential_id},
        credential_ids=[credential_id],
        description=f"Consent to issuance of {credential_id}",
    )
    nonce = create_delegation_challenge(tx)

    return sign_vp_jose(clean_vp, private_key, kid=kid, nonce=nonce)


def decode_evidence_vp(vp_jwt: str) -> dict:
    """Decode an evidence VP JWT."""
    return _decode_jwt(vp_jwt)


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
                # Expanded VP — sign it with a proper delegation challenge nonce
                evidence_vp_jwt = sign_evidence_vp(
                    vp_obj, private_key, kid, vc_payload=vc
                )
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

    # Map issuer DIDs to their verification method kid in the DID document.
    # In the project-specific did:ethr examples, the primary P-256 controller
    # key is exposed as #controller and is listed in assertionMethod.
    ISSUER_KID_MAP = {
        "did:ethr:0x14a34:0x50916c8e454722d2357916d4250500102288bb03": (
            "did:ethr:0x14a34:0x50916c8e454722d2357916d4250500102288bb03#controller"
        ),
        "did:ethr:0x14a34:0x9d273DCaC2f6367968d61caf69A7E3177fd81048": (
            "did:ethr:0x14a34:0x9d273DCaC2f6367968d61caf69A7E3177fd81048#controller"
        ),
    }

    # Find all example credentials
    examples = discover_examples()
    if not examples:
        print("No example credentials found in examples/", file=sys.stderr)
        sys.exit(1)

    print(f"Signing {len(examples)} example credentials with test P-256 key...")
    print("  Issuer -> kid mapping:")
    for issuer, kid in ISSUER_KID_MAP.items():
        print(f"    {issuer} → {kid}")

    for path, prefix in examples:
        # Determine kid from credential issuer
        vc = json.loads(path.read_text())
        issuer = vc.get("issuer", "")
        kid = ISSUER_KID_MAP.get(issuer)
        if kid is None:
            print(
                f"  WARNING: No kid mapping for issuer {issuer}, skipping {path.name}",
                file=sys.stderr,
            )
            continue

        jwt_path = process_example(path, prefix, private_key, kid)
        print(f"  {path.relative_to(REPO_ROOT)} -> {jwt_path.relative_to(REPO_ROOT)}")

    # List all generated files
    signed_files = sorted(SIGNED_DIR.iterdir())
    print(f"\nGenerated {len(signed_files)} files in examples/signed/:")
    for f in signed_files:
        print(f"  {f.name}")

    print("Done.")


if __name__ == "__main__":
    main()
