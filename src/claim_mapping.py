"""Claim mappings from W3C VCDM JSON-LD to SD-JWT-VC flat claims.

Defines how each SimpulseID credential type maps between nested JSON-LD
(credentialSubject) and flat SD-JWT-VC claims, plus which claims are
selectively disclosable.
"""

VCT_BASE = "https://w3id.org/ascs-ev/simpulse-id/credentials/v1"

PARTICIPANT_MAPPING = {
    "vct": f"{VCT_BASE}/ParticipantCredential",
    "claims": {
        "credentialSubject.legalName": "legalName",
        "credentialSubject.legalForm": "legalForm",
        "credentialSubject.duns": "duns",
        "credentialSubject.email": "email",
        "credentialSubject.url": "url",
        "credentialSubject.legalAddress": "legalAddress",
        "credentialSubject.headquartersAddress": "headquartersAddress",
        "credentialSubject.registrationNumber": "registrationNumber",
        "credentialSubject.termsAndConditions": "termsAndConditions",
    },
    "always_disclosed": ["iss", "vct", "iat", "exp", "legalName", "legalForm"],
    "selectively_disclosed": [
        "legalAddress",
        "headquartersAddress",
        "registrationNumber",
        "email",
        "url",
        "duns",
    ],
}

ADMINISTRATOR_MAPPING = {
    "vct": f"{VCT_BASE}/AdministratorCredential",
    "claims": {
        "credentialSubject.givenName": "givenName",
        "credentialSubject.familyName": "familyName",
        "credentialSubject.email": "email",
        "credentialSubject.memberOf": "memberOf",
        "credentialSubject.address": "address",
        "credentialSubject.termsAndConditions": "termsAndConditions",
    },
    "always_disclosed": ["iss", "vct", "iat", "exp", "memberOf"],
    "selectively_disclosed": [
        "givenName",
        "familyName",
        "email",
        "address",
    ],
}

USER_MAPPING = {
    "vct": f"{VCT_BASE}/UserCredential",
    "claims": {
        "credentialSubject.givenName": "givenName",
        "credentialSubject.familyName": "familyName",
        "credentialSubject.email": "email",
        "credentialSubject.memberOf": "memberOf",
        "credentialSubject.termsAndConditions": "termsAndConditions",
    },
    "always_disclosed": ["iss", "vct", "iat", "exp", "memberOf"],
    "selectively_disclosed": [
        "givenName",
        "familyName",
        "email",
    ],
}

BASE_MEMBERSHIP_MAPPING = {
    "vct": f"{VCT_BASE}/AscsBaseMembershipCredential",
    "claims": {
        "credentialSubject.memberOf": "memberOf",
        "credentialSubject.programName": "programName",
        "credentialSubject.hostingOrganization": "hostingOrganization",
        "credentialSubject.memberSince": "memberSince",
        "credentialSubject.termsAndConditions": "termsAndConditions",
    },
    "always_disclosed": [
        "iss",
        "vct",
        "iat",
        "exp",
        "memberOf",
        "programName",
    ],
    "selectively_disclosed": ["memberSince", "hostingOrganization"],
}

ENVITED_MEMBERSHIP_MAPPING = {
    "vct": f"{VCT_BASE}/AscsEnvitedMembershipCredential",
    "claims": {
        "credentialSubject.memberOf": "memberOf",
        "credentialSubject.programName": "programName",
        "credentialSubject.hostingOrganization": "hostingOrganization",
        "credentialSubject.memberSince": "memberSince",
        "credentialSubject.baseMembershipCredential": "baseMembershipCredential",
        "credentialSubject.termsAndConditions": "termsAndConditions",
    },
    "always_disclosed": [
        "iss",
        "vct",
        "iat",
        "exp",
        "memberOf",
        "programName",
        "baseMembershipCredential",
    ],
    "selectively_disclosed": ["memberSince", "hostingOrganization"],
}

# Registry: VC type string → mapping dict
MAPPINGS = {
    "simpulseid:ParticipantCredential": PARTICIPANT_MAPPING,
    "simpulseid:AdministratorCredential": ADMINISTRATOR_MAPPING,
    "simpulseid:UserCredential": USER_MAPPING,
    "simpulseid:AscsBaseMembershipCredential": BASE_MEMBERSHIP_MAPPING,
    "simpulseid:AscsEnvitedMembershipCredential": ENVITED_MEMBERSHIP_MAPPING,
}


def vc_to_sd_jwt_claims(vc: dict, mapping: dict) -> tuple[dict, list[str]]:
    """Convert a W3C VCDM JSON-LD VC to flat SD-JWT-VC claims.

    Args:
        vc: The Verifiable Credential JSON-LD dict.
        mapping: One of the *_MAPPING dicts above.

    Returns:
        Tuple of (flat_claims_dict, disclosable_claim_names).
    """
    claims = {}

    # Map issuer
    issuer = vc.get("issuer")
    if isinstance(issuer, dict):
        claims["iss"] = issuer.get("id", "")
    elif isinstance(issuer, str):
        claims["iss"] = issuer

    # Map subject ID
    subject = vc.get("credentialSubject", {})
    claims["sub"] = subject.get("id", "")

    # Map validity
    if "validFrom" in vc:
        claims["iat"] = vc["validFrom"]
    if "validUntil" in vc:
        claims["exp"] = vc["validUntil"]

    # Map credential-specific claims
    for vc_path, flat_name in mapping["claims"].items():
        value = _get_nested(vc, vc_path)
        if value is not None:
            claims[flat_name] = value

    disclosable = [
        name for name in mapping.get("selectively_disclosed", []) if name in claims
    ]

    return claims, disclosable


def sd_jwt_claims_to_vc(claims: dict, mapping: dict, vc_type: str) -> dict:
    """Convert flat SD-JWT-VC claims back to W3C VCDM JSON-LD structure.

    Args:
        claims: Flat claims dict.
        mapping: One of the *_MAPPING dicts above.
        vc_type: The VC type (e.g., "simpulseid:ParticipantCredential").

    Returns:
        W3C VCDM JSON-LD dict.
    """
    vc: dict = {
        "@context": [
            "https://www.w3.org/ns/credentials/v2",
            "https://w3id.org/ascs-ev/simpulse-id/credentials/v1/",
            "https://w3id.org/reachhaven/harbour/credentials/v1/",
            "https://w3id.org/gaia-x/development/",
        ],
        "type": ["VerifiableCredential", vc_type],
    }

    if "iss" in claims:
        vc["issuer"] = {"id": claims["iss"]}
    if "iat" in claims:
        vc["validFrom"] = claims["iat"]
    if "exp" in claims:
        vc["validUntil"] = claims["exp"]

    subject: dict = {}
    if "sub" in claims:
        subject["id"] = claims["sub"]

    # Reverse map
    reverse_map = {v: k for k, v in mapping["claims"].items()}
    for flat_name, value in claims.items():
        if flat_name in reverse_map:
            vc_path = reverse_map[flat_name]
            _set_nested(vc, vc_path, value)

    if subject or vc.get("credentialSubject"):
        existing = vc.get("credentialSubject", {})
        vc["credentialSubject"] = {**subject, **existing}

    return vc


def get_mapping_for_vc(vc: dict) -> dict | None:
    """Find the matching mapping for a VC based on its type."""
    vc_types = vc.get("type", [])
    for vc_type, mapping in MAPPINGS.items():
        if vc_type in vc_types:
            return mapping
    return None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_nested(obj: dict, path: str):
    """Get a nested value by dot-separated path."""
    parts = path.split(".")
    current = obj
    for part in parts:
        if isinstance(current, dict):
            current = current.get(part)
        else:
            return None
    return current


def _set_nested(obj: dict, path: str, value):
    """Set a nested value by dot-separated path."""
    parts = path.split(".")
    current = obj
    for part in parts[:-1]:
        if part not in current:
            current[part] = {}
        current = current[part]
    current[parts[-1]] = value
