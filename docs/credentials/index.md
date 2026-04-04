# Credential Types

SimpulseID defines five W3C Verifiable Credential types for identity and membership management in the [ENVITED-X Data Space](https://staging.envited-x.net). All credentials are issued by [ASCS e.V.](https://ascs.digital) as the trust anchor, deployed at [identity.ascs.digital](https://identity.ascs.digital).

Each credential type extends `HarbourCredential` from the [harbour-credentials](https://github.com/reachhaven/harbour-credentials) base schema. Credential subjects carry a mandatory `harbourCredential` IRI linking to a Harbour Gaia-X compliance credential, which provides the baseline of trust (Gaia-X `LegalPerson` or `NaturalPerson` attestation).

The credential types and their lifecycle are specified in [EVES-008](https://github.com/ASCS-eV/EVES/blob/main/EVES/EVES-008/eves-008.md). Evidence VPs follow [EVES-009](https://github.com/ASCS-eV/EVES/blob/main/EVES/EVES-009/eves-009.md).

## Available Types

| Credential Type | Description | Subject ID | Schema |
|-----------------|-------------|------------|--------|
| [ParticipantCredential](participant.md) | Organization identity (gx:LegalPerson) | `did:ethr` | `simpulseid:ParticipantCredential` |
| [AdministratorCredential](administrator.md) | Elevated-permission natural person | `did:ethr` | `simpulseid:AdministratorCredential` |
| [UserCredential](user.md) | Standard natural person | `did:ethr` | `simpulseid:UserCredential` |
| [Base Membership](membership.md) | ASCS e.V. base membership | `urn:uuid:` | `simpulseid:AscsBaseMembershipCredential` |
| [ENVITED Membership](membership.md) | ENVITED research cluster membership | `urn:uuid:` | `simpulseid:AscsEnvitedMembershipCredential` |

## Issuance Order (per EVES-008 §2)

Credentials MUST be issued in the following order:

1. **ParticipantCredential** --- ASCS verifies the organization's legal identity
2. **AscsBaseMembershipCredential** --- requires ParticipantCredential as prerequisite
3. **AscsEnvitedMembershipCredential** (optional) --- requires BaseMembership as prerequisite
4. **AdministratorCredential** / **UserCredential** --- issued to natural persons under a participant

## Schema Structure

All credentials follow the W3C Verifiable Credentials Data Model v2.0 with three mandatory `@context` entries:

```json
{
  "@context": [
    "https://www.w3.org/ns/credentials/v2",
    "https://w3id.org/reachhaven/harbour/core/v1/",
    "https://w3id.org/ascs-ev/simpulse-id/v1/"
  ],
  "type": ["VerifiableCredential", "<credential-type>"],
  "issuer": "<issuer-did>",
  "validFrom": "<iso-datetime>",
  "credentialSubject": {
    "id": "<subject-did-or-urn>",
    "type": "<subject-type>",
    "harbourCredential": "<harbour-gx-credential-urn>"
  },
  "credentialStatus": [{"type": "harbour:CRSetEntry", "statusPurpose": "revocation"}],
  "evidence": [{"type": ["harbour:CredentialEvidence"], "verifiablePresentation": "..."}]
}
```

## LinkML Definitions

Credential types are defined in a single LinkML schema:

- `linkml/simpulseid-core.yaml` --- All subject types, credential types, program metadata, and enums
- `linkml/importmap.json` --- Import resolution for harbour-credentials and Gaia-X schemas

After modifying schemas, regenerate artifacts:

```bash
make generate
```
