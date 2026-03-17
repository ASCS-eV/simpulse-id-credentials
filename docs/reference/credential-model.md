# Credential Data Model

This page documents how SimpulseID credential types extend the
[Harbour Credentials](https://ascs-ev.github.io/harbour-credentials/schema/credential-model/)
base model. For the base class hierarchy and Gaia-X composition pattern,
see the harbour-credentials documentation.

## Schema File Structure

```text
linkml/
├── importmap.json                # Maps import paths to submodule schemas
├── simpulseid.yaml               # Subject types, enums, business slots
└── simpulseid-credentials.yaml   # 5 credential types (is_a: HarbourCredential)
```

## Import Chain

```mermaid
graph LR
    W["w3c-vc.yaml<br/><i>W3C VC envelope</i>"]
    H["harbour-core-credential.yaml<br/><i>Abstract base</i>"]
    SC["simpulseid-credentials.yaml<br/><i>5 credential types</i>"]
    S["simpulseid.yaml<br/><i>Subject types + enums</i>"]

    W --> H
    H --> SC
    H --> S
    SC --> S

    style W fill:#e3f2fd,stroke:#1565c0
    style H fill:#f3e5f5,stroke:#6a1b9a
    style SC fill:#fff3e0,stroke:#e65100
    style S fill:#e8f5e9,stroke:#2e7d32
```

Import paths in `importmap.json` resolve `./harbour` to the
`harbour-core-credential.yaml` file inside `submodules/harbour-credentials/`.

---

## Credential Type Hierarchy

All five SimpulseID credential types inherit from `HarbourCredential`
(defined in harbour-credentials). They override `evidence` and
`credentialStatus` to be **optional**, since not all issuance flows
require them immediately.

```mermaid
classDiagram
    class HarbourCredential {
        <<abstract — harbour-credentials>>
        issuer : uri ⟨required⟩
        validFrom : datetime ⟨required⟩
        validUntil : datetime
        evidence : Evidence[] ⟨required⟩
        credentialStatus : CRSetEntry[] ⟨required⟩
    }

    class ParticipantCredential {
        evidence : optional
        credentialStatus : optional
    }
    class AdministratorCredential {
        evidence : optional
        credentialStatus : optional
    }
    class UserCredential {
        evidence : optional
        credentialStatus : optional
    }
    class AscsBaseMembershipCredential {
        evidence : optional
        credentialStatus : optional
    }
    class AscsEnvitedMembershipCredential {
        evidence : optional
        credentialStatus : optional
    }

    HarbourCredential <|-- ParticipantCredential
    HarbourCredential <|-- AdministratorCredential
    HarbourCredential <|-- UserCredential
    HarbourCredential <|-- AscsBaseMembershipCredential
    HarbourCredential <|-- AscsEnvitedMembershipCredential
```

### Constraint Overrides (slot_usage)

| Field | Harbour Base | SimpulseID Override |
|-------|-------------|---------------------|
| `issuer` | required | *(inherited)* |
| `validFrom` | required | *(inherited)* |
| `evidence` | **required** | **optional** |
| `credentialStatus` | **required** (CRSetEntry) | **optional** |

---

## Credential ↔ Subject Type Mapping

Each credential type attests to a specific subject type. Subject types
are standalone classes (not inherited from `HarbourCredential`) that
define the `credentialSubject` claim structure:

```mermaid
flowchart LR
    subgraph creds["Credential Types"]
        PC["ParticipantCredential"]
        AC["AdministratorCredential"]
        UC["UserCredential"]
        BMC["AscsBaseMembership<br/>Credential"]
        EMC["AscsEnvitedMembership<br/>Credential"]
    end

    subgraph subjects["Subject Types"]
        SP["SimpulseidParticipant<br/><i>Organisation</i>"]
        SA["SimpulseidAdministrator<br/><i>Person + elevated perms</i>"]
        SU["SimpulseidUser<br/><i>Person</i>"]
        BM["AscsBaseMembership"]
        EM["AscsEnvitedMembership"]
    end

    PC --> SP
    AC --> SA
    UC --> SU
    BMC --> BM
    EMC --> EM

    style creds fill:#fff3e0,stroke:#e65100
    style subjects fill:#e8f5e9,stroke:#2e7d32
```

### Subject Type Details

#### Organisation Subjects

| Field | Participant | Required |
|-------|------------|----------|
| `harbourCredential` | IRI to Harbour GX credential | **yes** |
| `legalForm` | `SimpulseIdLegalForm` enum | no |
| `duns` | DUNS number | no |
| `email` | Contact email | no |
| `url` | Website | no |
| `termsAndConditions` | T&C docs with integrity hash | no |
| `participant` | Nested Gaia-X compliance data | no |
| `name` | Organisation name | no |

#### Person Subjects

| Field | Administrator | User |
|-------|--------------|------|
| `harbourCredential` | **required** | **required** |
| `givenName` | **required** | optional |
| `familyName` | **required** | optional |
| `email` | **required** | optional |
| `memberOf` | optional | optional |
| `participant` | optional | optional |

#### Membership Subjects

| Field | Base Membership | ENVITED Membership |
|-------|----------------|-------------------|
| `member` | **required** (DID) | **required** (DID) |
| `programName` | optional | optional |
| `hostingOrganization` | optional | optional |
| `memberSince` | optional | optional |
| `baseMembershipCredential` | — | **required** (IRI) |

---

## Trust Chain

Credentials reference each other via IRI links to establish a chain
of trust from the ecosystem root to individual memberships:

```mermaid
flowchart TD
    HC["Harbour GX Credential<br/><i>LegalPersonCredential</i><br/>(signed by ecosystem operator)"]
    PC["SimpulseID<br/>ParticipantCredential<br/>(signed by SimpulseID issuer)"]
    BMC["AscsBaseMembership<br/>Credential"]
    EMC["AscsEnvitedMembership<br/>Credential"]

    HC -- "harbourCredential (IRI)" --> PC
    PC -. "issuer resolves via DID" .-> BMC
    BMC -- "baseMembershipCredential (IRI)" --> EMC

    style HC fill:#e3f2fd,stroke:#1565c0
    style PC fill:#fff3e0,stroke:#e65100
    style BMC fill:#e8f5e9,stroke:#2e7d32
    style EMC fill:#e8f5e9,stroke:#2e7d32
```

The `harbourCredential` field in each subject type is an IRI reference
(not an embedded credential), keeping payload sizes small and enabling
independent verification of each layer.

---

## Legal Form Enum

The `SimpulseIdLegalForm` enum covers organisation types across
jurisdictions:

| Region | Values |
|--------|--------|
| **US** | `LLC`, `Corporation`, `LimitedPartnership`, `NonprofitCorporation` |
| **DE** | `GmbH`, `AG`, `Einzelunternehmen`, `GbR`, `OHG`, `KG`, `UG` |
| **UK** | `SoleTrader`, `Partnership`, `LimitedCompany`, `LLP`, `CIC`, `CIO`, `CooperativeSociety`, `BenCom`, `Trust`, `UnincorporatedAssociation` |
| **Fallback** | `other` |
