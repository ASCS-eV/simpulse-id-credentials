# LinkML Schemas

This repository defines credential types and subject types using [LinkML](https://linkml.io/), a modeling language for linked data. The schemas are the single source of truth from which OWL ontologies, SHACL shapes, and JSON-LD contexts are generated.

## Schema Files

| File | Purpose |
|------|---------|
| `linkml/simpulseid.yaml` | Main schema — subject types, slots, enums, and imports |
| `linkml/simpulseid-credentials.yaml` | Credential type definitions (separated for SHACL generation) |
| `linkml/importmap.json` | Import resolution for harbour submodule schemas |

### Why Two Schema Files?

Credential types (e.g., `ParticipantCredential`) and subject types (e.g., `SimpulseidParticipant`) are intentionally separated. The SHACL generator uses `exclude_imports=True` to emit shapes **only** for subject types and nested types defined in `simpulseid.yaml`. Harbour's own SHACL artifacts handle credential envelope validation via RDFS inference.

## Class Hierarchy

### Credential Types (in `simpulseid-credentials.yaml`)

All credential types extend `HarbourCredential`:

```text
HarbourCredential (harbour base)
├── ParticipantCredential
├── AdministratorCredential
├── UserCredential
├── AscsBaseMembershipCredential
└── AscsEnvitedMembershipCredential
```

### Subject Types (in `simpulseid.yaml`)

```text
SimpulseidParticipant    → simpulseid:Participant
SimpulseidAdministrator  → simpulseid:Administrator
SimpulseidUser           → simpulseid:User
AscsBaseMembership       → simpulseid:AscsBaseMembership
AscsEnvitedMembership    → simpulseid:AscsEnvitedMembership
```

## Slots

### SimpulseID Business Slots

| Slot | URI | Range | Description |
|------|-----|-------|-------------|
| `harbourCredential` | `simpulseid:harbourCredential` | URI | Reference to Harbour baseline credential |
| `duns` | `simpulseid:duns` | string | DUNS number |
| `legalForm` | `simpulseid:legalForm` | `SimpulseIdLegalForm` | Legal form enum |
| `baseMembershipCredential` | `simpulseid:baseMembershipCredential` | URI | Reference to base membership VC |
| `termsAndConditions` | `simpulseid:termsAndConditions` | Any (`gx:TermsAndConditions`) | T&C with integrity hash (Gaia-X type) |
| `gxParticipant` | `harbour:gxParticipant` | Any | Gaia-X participant data |

### Schema.org Mappings

| Slot | URI | Range |
|------|-----|-------|
| `givenName` | `sdo:givenName` | string |
| `familyName` | `sdo:familyName` | string |
| `member` | `sdo:member` | URI |
| `memberOf` | `sdo:memberOf` | URI (multivalued) |
| `programName` | `sdo:programName` | string |
| `hostingOrganization` | `sdo:hostingOrganization` | URI |
| `memberSince` | `sdo:memberSince` | date |

!!! note "Schema.org Prefix Handling"
    The LinkML schemas in this repository bind `https://schema.org/` under the `sdo:` prefix. This avoids a prefix-name collision with LinkML's built-in `schema:` prefix, which still resolves to `http://schema.org/` in the upstream meta-model.

## Enums

### SimpulseIdLegalForm

Legal form values for organizations:

`AG`, `GmbH`, `LLC`, `Corporation`, `LimitedPartnership`, `NonprofitCorporation`, `Einzelunternehmen`, `GbR`, `OHG`, `KG`, `UG`, `SoleTrader`, `UnincorporatedAssociation`, `Partnership`, `Trust`, `LimitedCompany`, `LLP`, `CIC`, `CIO`, `CooperativeSociety`, `BenCom`, `other`

## Import Map

The `importmap.json` file resolves harbour schema imports:

```json
{
  "harbour": "./harbour-core-credential.yaml"
}
```

This allows `imports: [./harbour]` in the schema to resolve to the harbour submodule's LinkML definitions without hardcoding paths.

## Generating Artifacts

After modifying schemas, regenerate all artifacts:

```bash
make generate
```

This runs `src/generate_artifacts.py`, which produces:

| Output | Generator | Location |
|--------|-----------|----------|
| OWL ontology | `OwlSchemaGenerator` | `artifacts/simpulseid/simpulseid.owl.ttl` |
| SHACL shapes | `DomainShaclGenerator` | `artifacts/simpulseid/simpulseid.shacl.ttl` |
| JSON-LD context | `ContextGenerator` | `artifacts/simpulseid/simpulseid.context.jsonld` |

### LinkML Workarounds

The generator includes two workarounds for LinkML issues:

1. **[linkml#2913](https://github.com/linkml/linkml/issues/2913)**: `ShaclGenerator.__post_init__` ignores `importmap`, so a custom `DomainShaclGenerator` bypasses it
2. **[linkml#2914](https://github.com/linkml/linkml/issues/2914)**: `sh:class linkml:Any` constraints are stripped because `linkml:Any` is never asserted as `rdf:type` on instance data

## See Also

- [JSON-LD Contexts](jsonld.md) — Generated context reference
- [Validation](../integration/validation.md) — Validating against generated SHACL shapes
- [LinkML documentation](https://linkml.io/linkml/)
