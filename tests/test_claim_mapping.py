"""Tests for claim mappings: W3C VCDM JSON-LD <-> SD-JWT-VC flat claims."""

import json
from pathlib import Path

from src.claim_mapping import (
    MAPPINGS,
    get_mapping_for_vc,
    sd_jwt_claims_to_vc,
    vc_to_sd_jwt_claims,
)

EXAMPLES_DIR = Path(__file__).parent.parent / "examples"


def _load_example(name: str) -> dict:
    with open(EXAMPLES_DIR / name) as f:
        return json.load(f)


class TestParticipantMapping:
    def test_vc_to_claims(self):
        vc = _load_example("simpulseid-participant-credential.json")
        mapping = MAPPINGS["simpulseid:ParticipantCredential"]
        claims, disclosable = vc_to_sd_jwt_claims(vc, mapping)

        assert claims["iss"] == "did:web:did.ascs.digital:participants:ascs"
        assert claims["sub"] == "did:web:did.ascs.digital:participants:bmw"
        assert claims["legalName"] == "Bayerische Motoren Werke Aktiengesellschaft"
        assert claims["legalForm"] == "AG"
        assert claims["email"] == "imprint@bmw.com"
        assert "legalAddress" in claims
        assert "email" in disclosable
        assert "legalAddress" in disclosable

    def test_roundtrip(self):
        vc = _load_example("simpulseid-participant-credential.json")
        mapping = MAPPINGS["simpulseid:ParticipantCredential"]
        claims, _ = vc_to_sd_jwt_claims(vc, mapping)
        reconstructed = sd_jwt_claims_to_vc(
            claims, mapping, "simpulseid:ParticipantCredential"
        )
        assert (
            reconstructed["credentialSubject"]["legalName"]
            == vc["credentialSubject"]["legalName"]
        )
        assert (
            reconstructed["credentialSubject"]["legalForm"]
            == vc["credentialSubject"]["legalForm"]
        )


class TestAdministratorMapping:
    def test_vc_to_claims(self):
        vc = _load_example("simpulseid-administrator-credential.json")
        mapping = MAPPINGS["simpulseid:AdministratorCredential"]
        claims, disclosable = vc_to_sd_jwt_claims(vc, mapping)

        assert claims["givenName"] == "Andreas"
        assert claims["familyName"] == "Admin"
        assert claims["email"] == "andreas.admin@bmw.com"
        assert "givenName" in disclosable
        assert "email" in disclosable

    def test_roundtrip(self):
        vc = _load_example("simpulseid-administrator-credential.json")
        mapping = MAPPINGS["simpulseid:AdministratorCredential"]
        claims, _ = vc_to_sd_jwt_claims(vc, mapping)
        reconstructed = sd_jwt_claims_to_vc(
            claims, mapping, "simpulseid:AdministratorCredential"
        )
        assert (
            reconstructed["credentialSubject"]["givenName"]
            == vc["credentialSubject"]["givenName"]
        )


class TestUserMapping:
    def test_vc_to_claims(self):
        vc = _load_example("simpulseid-user-credential.json")
        mapping = MAPPINGS["simpulseid:UserCredential"]
        claims, disclosable = vc_to_sd_jwt_claims(vc, mapping)

        assert "memberOf" in claims

    def test_roundtrip(self):
        vc = _load_example("simpulseid-user-credential.json")
        mapping = MAPPINGS["simpulseid:UserCredential"]
        claims, _ = vc_to_sd_jwt_claims(vc, mapping)
        reconstructed = sd_jwt_claims_to_vc(
            claims, mapping, "simpulseid:UserCredential"
        )
        assert "UserCredential" in str(reconstructed["type"])


class TestBaseMembershipMapping:
    def test_vc_to_claims(self):
        vc = _load_example("simpulseid-ascs-base-membership-credential.json")
        mapping = MAPPINGS["simpulseid:AscsBaseMembershipCredential"]
        claims, disclosable = vc_to_sd_jwt_claims(vc, mapping)

        assert claims["programName"] == "ASCS e.V. Base Membership"
        assert claims["memberSince"] == "2023-01-01"
        assert "memberSince" in disclosable


class TestEnvitedMembershipMapping:
    def test_vc_to_claims(self):
        vc = _load_example("simpulseid-ascs-envited-membership-credential.json")
        mapping = MAPPINGS["simpulseid:AscsEnvitedMembershipCredential"]
        claims, disclosable = vc_to_sd_jwt_claims(vc, mapping)

        assert "baseMembershipCredential" in claims


class TestMappingDiscovery:
    def test_get_mapping_for_participant(self):
        vc = _load_example("simpulseid-participant-credential.json")
        mapping = get_mapping_for_vc(vc)
        assert mapping is not None
        assert mapping["vct"].endswith("ParticipantCredential")

    def test_get_mapping_for_unknown(self):
        vc = {"type": ["VerifiableCredential", "UnknownType"]}
        mapping = get_mapping_for_vc(vc)
        assert mapping is None
