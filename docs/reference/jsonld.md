# JSON-LD Contexts

JSON-LD contexts map short property names in credential JSON to full IRIs, enabling semantic interoperability. The SimpulseID context is generated from LinkML schemas and composed with upstream contexts.

## Context Composition

Every SimpulseID credential uses a stack of four contexts:

```json
{
  "@context": [
    "https://www.w3.org/ns/credentials/v2",
    "https://w3id.org/gaia-x/development#",
    "https://w3id.org/reachhaven/harbour/credentials/v1/",
    "https://w3id.org/ascs-ev/simpulse-id/credentials/v1/"
  ]
}
```

| Context | Purpose |
|---------|---------|
| W3C VCDM v2 | Base credential vocabulary (`issuer`, `validFrom`, `credentialSubject`, etc.) |
| Gaia-X | Gaia-X 25.11 compliance terms (`gx:LegalPerson`, `gx:registrationNumber`, etc.) |
| Harbour | Credential envelope terms (`HarbourCredential`, `CRSetEntry`, `evidence`, etc.) |
| SimpulseID | Domain-specific terms (`Participant`, `legalForm`, `duns`, etc.) |

Contexts are processed in order — later contexts can override earlier ones. The SimpulseID context is always last, so its `@vocab` acts as the default namespace for any terms not defined by upstream contexts.

## Generated Context

The SimpulseID context is generated from `linkml/simpulseid.yaml` and written to `artifacts/simpulseid/simpulseid.context.jsonld`.

### Default Namespace

```json
"@vocab": "https://w3id.org/ascs-ev/simpulse-id/credentials/v1/"
```

Any bare term not explicitly mapped (e.g., `duns`, `hash`) resolves to the SimpulseID namespace.

### Prefix Definitions

| Prefix | IRI | Usage |
|--------|-----|-------|
| `simpulseid` | `https://w3id.org/ascs-ev/simpulse-id/credentials/v1/` | Domain types and slots |
| `harbour` | `https://w3id.org/reachhaven/harbour/credentials/v1/` | Harbour base types |
| `schema` | `http://schema.org/` | Schema.org (HTTP) for most slots |
| `sdo` | `https://schema.org/` | Schema.org (HTTPS) for `name` only |
| `cred` | `https://www.w3.org/2018/credentials#` | W3C credentials vocabulary |
| `xsd` | `http://www.w3.org/2001/XMLSchema#` | XML Schema datatypes |

!!! note "Dual Schema.org Prefixes"
    The W3C VC v2 context maps `name` to `https://schema.org/name` (HTTPS, `@protected`). Most other schema.org terms use `http://schema.org/`. The `sdo:` prefix (HTTPS) is used exclusively for `name` so SHACL validation `sh:path` matches the actual RDF predicate.

### Term Mappings

#### String Properties

| JSON Term | Maps To |
|-----------|---------|
| `name` | `sdo:name` (HTTPS schema.org) |
| `givenName` | `schema:givenName` |
| `familyName` | `schema:familyName` |
| `email` | `schema:email` |
| `programName` | `schema:programName` |
| `duns` | `simpulseid:duns` (via `@vocab`) |
| `hash` | `simpulseid:hash` (via `@vocab`) |

#### URI Properties

These are typed as `xsd:anyURI`:

| JSON Term | Maps To |
|-----------|---------|
| `harbourCredential` | `simpulseid:harbourCredential` |
| `baseMembershipCredential` | `simpulseid:baseMembershipCredential` |
| `member` | `schema:member` |
| `memberOf` | `schema:memberOf` |
| `hostingOrganization` | `schema:hostingOrganization` |
| `url` | `schema:url` |

#### Date Properties

| JSON Term | Maps To | Datatype |
|-----------|---------|----------|
| `memberSince` | `schema:memberSince` | `xsd:date` |
| `validFrom` | `cred:validFrom` | `xsd:dateTime` |
| `validUntil` | `cred:validUntil` | `xsd:dateTime` |

#### Type Alias

```json
"type": "@type"
```

This alias is added by the generator as a post-processing step because LinkML cannot emit it without declaring a `type` slot that would conflict with the W3C VCDM v2 context's `@protected` definition.

## Regenerating

The context is regenerated with:

```bash
make generate
```

The generator (`src/generate_artifacts.py`) uses `linkml.generators.jsonldcontextgen.ContextGenerator` and applies a post-processing step to add the `"type": "@type"` alias.

## See Also

- [LinkML Schemas](linkml.md) — Source schema definitions
- [JSON-LD 1.1 specification](https://www.w3.org/TR/json-ld11/)
- [W3C VC Data Model v2.0](https://www.w3.org/TR/vc-data-model-2.0/)
