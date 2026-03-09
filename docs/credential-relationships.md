# SimpulseID Credential Relationships

This document explains how the five SimpulseID credential types relate to each other,
the entities they describe, and the semantic meaning of `member` vs `memberOf`.

## Entity Graph

The ENVITED ecosystem has four kinds of entities and five credential types that
bind them together:

```mermaid
graph TD
    ASCS["ASCS e.V.<br/><i>Trust Anchor & Issuer</i><br/>did:ethr:0x14a34:0x50916c8e454722d2357916d4250500102288bb03"]
    BMW["BMW AG<br/><i>Participant</i><br/>did:ethr:0x14a34:0x9d273DCaC2f6367968d61caf69A7E3177fd81048"]
    ADMIN["Andreas Admin<br/><i>Administrator (NaturalPerson)</i><br/>did:ethr:0x14a34:0xb2F7...b39a"]
    USER["Max Mustermann<br/><i>User (NaturalPerson)</i><br/>did:ethr:0x14a34:0x0f4D...d4fC"]
    BASE["ASCS Base Membership<br/><i>ProgramMembership</i><br/>urn:uuid:22423d4a-..."]
    ENVITED["ENVITED Membership<br/><i>ProgramMembership</i><br/>urn:uuid:bac22d92-..."]

    ASCS -- "issues all credentials" --> BMW
    BMW -- "employs" --> ADMIN
    BMW -- "employs" --> USER
    BASE -- "member" --> BMW
    BASE -- "hostingOrganization" --> ASCS
    ENVITED -- "member" --> BMW
    ENVITED -- "hostingOrganization" --> ASCS
    ENVITED -. "baseMembershipCredential<br/>(prerequisite)" .-> BASE
    ADMIN -- "memberOf" --> BMW
    USER -- "memberOf" --> BMW
```

## Credential Types and What They Prove

| # | Credential | Subject | Proves |
|---|-----------|---------|--------|
| 1 | `ParticipantCredential` | BMW (Participant) | BMW is a verified legal person in the ecosystem |
| 2 | `AscsBaseMembershipCredential` | a ProgramMembership | BMW holds ASCS e.V. base membership |
| 3 | `AscsEnvitedMembershipCredential` | a ProgramMembership | BMW holds ENVITED research cluster membership |
| 4 | `AdministratorCredential` | Andreas (Administrator) | Andreas is an authorized admin for BMW |
| 5 | `UserCredential` | Max (User) | Max is an authorized user under BMW |

## Issuance Flow and Prerequisites

Credentials are issued in a specific order. Some require prior credentials as evidence:

```mermaid
flowchart LR
    PC["1. ParticipantCredential<br/><i>BMW is a legal person</i>"]
    BM["2. AscsBaseMembershipCredential<br/><i>BMW is an ASCS member</i>"]
    EM["3. AscsEnvitedMembershipCredential<br/><i>BMW is an ENVITED member</i>"]
    AC["4. AdministratorCredential<br/><i>Andreas manages BMW</i>"]
    UC["5. UserCredential<br/><i>Max acts for BMW</i>"]

    PC -->|"evidence: IssuanceEvidence<br/>(proves participant exists)"| BM
    BM -->|"baseMembershipCredential<br/>(prerequisite)"| EM
    PC -.->|"issuer.member = BMW"| AC
    PC -.->|"issuer.member = BMW"| UC
```

**Step by step (using BMW as the example):**

1. **ParticipantCredential** -- ASCS verifies BMW's legal identity (registration number,
   address, etc.) and issues a credential. The `credentialSubject` contains a nested
   `legalPerson` object typed `gx:LegalPerson` with Gaia-X compliant data.

2. **AscsBaseMembershipCredential** -- ASCS issues a base membership. The credential
   carries `evidence` containing the ParticipantCredential (proving BMW exists).
   The `credentialSubject` is a ProgramMembership with `member: BMW`.

3. **AscsEnvitedMembershipCredential** -- ASCS issues an ENVITED membership.
   The `baseMembershipCredential` field references the base membership (step 2)
   as a prerequisite. Without base ASCS membership, ENVITED membership cannot be issued.

4. **AdministratorCredential** -- ASCS issues credentials for BMW's admin (Andreas).
   The `issuer.member` field identifies BMW as the organization.

5. **UserCredential** -- BMW itself (acting as issuer) issues credentials to its users.
   The `issuer.member` still points to BMW (self-referential: BMW issues for its own users).

## `member` vs `memberOf` -- When to Use Which

These are two sides of the same relationship. The key is **which entity is the subject**:

```mermaid
graph LR
    subgraph "ProgramMembership (the relationship)"
        M["AscsBaseMembership"]
    end
    subgraph "The member"
        P["BMW (Participant)"]
    end
    subgraph "The host"
        H["ASCS e.V."]
    end

    M -- "member<br/>(schema:member)" --> P
    M -- "hostingOrganization<br/>(schema:hostingOrganization)" --> H
    P -- "memberOf<br/>(schema:memberOf)" --> M
```

### `member` (schema:member)

Used **on the membership object**, pointing **to the member**.

> "This membership **has** this member."

Appears in:
- **Membership credentialSubject** -- `"member": "did:ethr:0x14a34:0x9d27...1048"` identifies
  who holds the membership.
- **Issuer object** -- `"member": "did:ethr:0x14a34:0x9d27...1048"` identifies which
  participant this credential is issued for (SimpulseID convention using schema:member).

### `memberOf` (schema:memberOf)

Used **on the person/organization**, pointing **to what they belong to**.

> "This person **belongs to** this organization."

Appears in:
- **Administrator credentialSubject** -- `"memberOf": ["did:ethr:0x14a34:0x9d27...1048"]`
  means "Andreas belongs to BMW".
- **User credentialSubject** -- `"memberOf": ["did:ethr:0x14a34:0x9d27...1048"]`
  means "Max belongs to BMW".

### Why membership subjects have their own URN-UUIDs

A ProgramMembership is a **relationship object**, not a first-class entity with its own
DID. Each membership gets a unique `urn:uuid:` identifier that is distinct from both
the participant's DID and the credential envelope's `id`.

This avoids graph merge conflicts: if two membership credentials used the participant's
DID as `credentialSubject.id`, loading them into one RDF graph would merge all properties
onto a single node -- producing nonsensical data (BMW would have two `programName`
values, two contradictory types, etc.).

Similarly, evidence VC snippets (inline references to prior credentials) omit
`credentialSubject` to prevent merging with the full credential's subject when both
are in the same graph.

## Credential Subject Identity Summary

| Credential | credentialSubject.id | Why |
|-----------|---------------------|-----|
| ParticipantCredential | BMW's DID | The subject IS BMW |
| AdministratorCredential | Andreas's DID | The subject IS Andreas |
| UserCredential | Max's DID | The subject IS Max |
| AscsBaseMembershipCredential | own urn:uuid | The subject is a membership relationship, not an entity |
| AscsEnvitedMembershipCredential | own urn:uuid | The subject is a membership relationship, not an entity |
