# Generated artefacts

This folder contains downstream artefacts generated from LinkML schemas:

- JSON-LD context (`*.context.jsonld`)
- SHACL shapes (`*.shacl.ttl`)
- OWL ontology (`*.owl.ttl`)

Each schema is generated into its own flat subfolder, matching the ontology-management-base pattern:

- `artifacts/simpulseid/` (this repo)
- `submodules/harbour-credentials/artifacts/harbour-core-credential/` (harbour-credentials repo)
- `submodules/harbour-credentials/artifacts/harbour-gx-credential/` (harbour-credentials repo)

## 1) Generate

From repository root:

```bash
# Auto-discover mode routes each model to the correct artifacts/ dir
python3 src/generate_from_linkml.py

# Or specify models and a single output root explicitly
python3 src/generate_from_linkml.py \
  --model linkml/simpulseid.yaml \
  --out-root artifacts
```

## 2) Validate examples against generated SHACL + schema (recommended)

Examples are validated using the `submodules/harbour-credentials/submodules/ontology-management-base` validator.
It discovers artifacts automatically from `artifacts/` directories:

```bash
python3 submodules/harbour-credentials/submodules/ontology-management-base/src/check_jsonld_against_shacl_schema.py \
  examples/simpulseid-administrator-credential.json
```

## Notes on `id` / `@id`

In JSON-LD, the node identifier is the keyword `@id`. Many JSON-LD contexts (including VC contexts) map a compact term like `id` to `@id`, but the underlying mechanism is JSON-LD itself.

For LinkML, the robust modelling pattern is to define a shared slot once (e.g., in a small `core.yaml`) with:

- `slot_uri: "@id"` for the `id` slot
- `slot_uri: "@type"` for the `type` slot

and import that shared definition into all schemas that need it. This prevents "conflicting URIs for item: id" during import merges.
