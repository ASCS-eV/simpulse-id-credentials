# Generated artefacts

This folder contains downstream artefacts generated from LinkML schemas:

- JSON-LD context (`*_context.jsonld`)
- SHACL shapes (`*_shacl.ttl`)
- OWL ontology (`*_ontology.ttl`)

Each schema is generated into its own subfolder:

- `generated/simpulseid/`
- `generated/harbour/`
- `generated/gx/`

## 1) Generate

From repository root:

```bash
python3 src/generate_from_linkml.py \
  --model linkml/simpulseid.yaml \
  --model linkml/harbour.yaml \
  --model service-characteristics/linkml/gaia-x.yaml \
  --out-root generated
```

## 2) Validate examples against generated SHACL + schema (recommended)

Examples are validated using the `ontology-management-base` validator.
Point `--root` to `generated/` so it can resolve:

- generated contexts
- generated SHACL files
- generated ontologies

Example:

```bash
python3 ontology-management-base/src/check_jsonld_against_shacl_schema.py \
  examples/simpulseid-administrator-credential.json \
  --root generated/
```

## Notes on `id` / `@id`

In JSON-LD, the node identifier is the keyword `@id`. Many JSON-LD contexts (including VC contexts) map a compact term like `id` to `@id`, but the underlying mechanism is JSON-LD itself.

For LinkML, the robust modelling pattern is to define a shared slot once (e.g., in a small `core.yaml`) with:

- `slot_uri: "@id"` for the `id` slot
- `slot_uri: "@type"` for the `type` slot

and import that shared definition into all schemas that need it. This prevents “conflicting URIs for item: id” during import merges.
