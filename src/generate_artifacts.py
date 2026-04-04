#!/usr/bin/env python3
"""Generate downstream artifacts (JSON-LD context, SHACL shapes, OWL ontology)
from the simpulseid-core LinkML schema.

All three generators receive the schema file path, importmap, and base_dir
so that SchemaView resolves cross-directory imports (e.g. ``./harbour`` →
harbour-gx-credential in the submodule) via the standard importmap mechanism.

SHACL uses ``exclude_imports=True`` so only locally-defined classes get shapes
(subject types, program types, and credential types — all in simpulseid-core).
Imported harbour / gaia-x classes are excluded.

NOTE: The ``publisher`` slot is named ``programPublisher`` to avoid a
name collision with the gaia-x ``publisher`` slot (different ``from_schema``).
Both schemas are loaded by SchemaLoader during import resolution, and
``merge_dicts`` raises ValueError on same-name slots from different schemas.
Renaming eliminates the conflict; ``slot_uri: sdo:publisher`` ensures the
RDF property remains ``schema:publisher``.
"""

import json
from pathlib import Path

from linkml.generators.jsonldcontextgen import ContextGenerator
from linkml.generators.owlgen import OwlSchemaGenerator
from linkml.generators.shaclgen import ShaclGenerator

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA = REPO_ROOT / "linkml" / "simpulseid-core.yaml"
IMPORTMAP_FILE = REPO_ROOT / "linkml" / "importmap.json"
OUT_DIR = REPO_ROOT / "artifacts" / "simpulseid-core"


def load_importmap() -> dict:
    """Resolve importmap paths relative to the importmap file's directory."""
    if not IMPORTMAP_FILE.exists():
        return {}
    raw = json.loads(IMPORTMAP_FILE.read_text())
    resolved = {}
    for key, val in raw.items():
        p = Path(val)
        if not p.is_absolute():
            p = (IMPORTMAP_FILE.parent / p).resolve()
        resolved[key] = str(p)
    return resolved


def main() -> None:
    import_map = load_importmap()
    gen_args = dict(importmap=import_map, base_dir=str(SCHEMA.parent))

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # --- OWL ---
    print("Generating OWL ontology...")
    owl_gen = OwlSchemaGenerator(
        str(SCHEMA), deterministic=True, normalize_prefixes=True, **gen_args
    )
    (OUT_DIR / "simpulseid-core.owl.ttl").write_text(
        owl_gen.serialize(), encoding="utf-8"
    )

    # --- SHACL ---
    print("Generating SHACL shapes...")
    shacl_gen = ShaclGenerator(
        str(SCHEMA),
        closed=True,
        exclude_imports=True,
        deterministic=True,
        normalize_prefixes=True,
        **gen_args,
    )
    (OUT_DIR / "simpulseid-core.shacl.ttl").write_text(
        shacl_gen.serialize(), encoding="utf-8"
    )

    # --- JSON-LD context ---
    print("Generating JSON-LD context...")
    ctx_gen = ContextGenerator(
        str(SCHEMA),
        mergeimports=False,
        exclude_external_imports=True,
        xsd_anyuri_as_iri=True,
        normalize_prefixes=True,
        deterministic=True,
        **gen_args,
    )
    ctx_text = ctx_gen.serialize()

    # Inject "type": "@type" — LinkML cannot emit this alias without declaring
    # a ``type`` slot, which would shadow the W3C VCDM v2 keyword mapping.
    ctx_data = json.loads(ctx_text)
    ctx_obj = ctx_data.get("@context", {})
    if isinstance(ctx_obj, dict) and "type" not in ctx_obj:
        ctx_obj["type"] = "@type"
        ctx_data["@context"] = ctx_obj
    ctx_text = json.dumps(ctx_data, indent=3, ensure_ascii=False)

    (OUT_DIR / "simpulseid-core.context.jsonld").write_text(ctx_text, encoding="utf-8")

    print(f"Done: {OUT_DIR}/")


if __name__ == "__main__":
    main()
