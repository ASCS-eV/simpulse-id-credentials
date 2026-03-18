#!/usr/bin/env python3
"""Generate downstream artifacts (JSON-LD context, SHACL shapes, OWL ontology)
from simpulseid LinkML schema using importmap for harbour resolution.

Credential types (is_a: HarbourCredential) are defined in a separate imported
schema (simpulseid-credentials.yaml). The SHACL generator uses exclude_imports
to emit shapes only for subject types and nested types; harbour's own SHACL
artifacts validate the credential envelope via RDFS inference.
"""

import json
from pathlib import Path

from linkml.generators.jsonldcontextgen import ContextGenerator
from linkml.generators.owlgen import OwlSchemaGenerator
from linkml.generators.shaclgen import ShaclGenerator as _BaseShaclGenerator

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA = REPO_ROOT / "linkml" / "simpulseid.yaml"
IMPORTMAP_FILE = REPO_ROOT / "linkml" / "importmap.json"
OUT_DIR = REPO_ROOT / "artifacts" / "simpulseid"


class SimpulseidShaclGenerator(_BaseShaclGenerator):
    """SHACL generator with importmap-aware initialisation.

    Bypasses ``ShaclGenerator.__post_init__``'s ``SchemaView`` construction
    which calls ``_initialize_using_schemaloader`` and doubles the schema
    path when ``base_dir`` is set, causing cross-directory imports to fail.
    See https://github.com/linkml/linkml/issues/2913
    """

    uses_schemaloader = False

    def __post_init__(self) -> None:
        from linkml.utils.generator import Generator

        Generator.__post_init__(self)
        self.generate_header()


def load_importmap() -> dict:
    if IMPORTMAP_FILE.exists():
        raw = json.loads(IMPORTMAP_FILE.read_text())
        resolved = {}
        for key, val in raw.items():
            p = Path(val)
            if not p.is_absolute():
                p = (IMPORTMAP_FILE.parent / p).resolve()
            resolved[key] = str(p)
        return resolved
    return {}


def main() -> None:
    import_map = load_importmap()
    base_dir = str(SCHEMA.parent)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Generating OWL ontology...")
    owl_gen = OwlSchemaGenerator(str(SCHEMA), importmap=import_map, base_dir=base_dir)
    (OUT_DIR / "simpulseid.owl.ttl").write_text(owl_gen.serialize(), encoding="utf-8")

    print("Generating SHACL shapes...")
    shacl_gen = SimpulseidShaclGenerator(
        str(SCHEMA),
        importmap=import_map,
        base_dir=base_dir,
        closed=True,
        exclude_imports=True,
    )
    (OUT_DIR / "simpulseid.shacl.ttl").write_text(
        shacl_gen.serialize(), encoding="utf-8"
    )

    print("Generating JSON-LD context...")
    ctx_gen = ContextGenerator(
        str(SCHEMA),
        importmap=import_map,
        base_dir=base_dir,
        mergeimports=False,
        xsd_anyuri_as_iri=True,
    )
    ctx_text = ctx_gen.serialize()

    # Ensure "type": "@type" is present in the generated context.
    # LinkML cannot emit this alias without declaring a ``type`` slot, which
    # would override the W3C VCDM v2 ``"type": "@type"`` with a typed
    # property definition (see harbour-core-credential.yaml §slots comment).
    ctx_data = json.loads(ctx_text)
    ctx_obj = ctx_data.get("@context", {})
    if isinstance(ctx_obj, dict) and "type" not in ctx_obj:
        ctx_obj["type"] = "@type"

    ctx_data["@context"] = ctx_obj
    ctx_text = json.dumps(ctx_data, indent=3, ensure_ascii=False)

    (OUT_DIR / "simpulseid.context.jsonld").write_text(ctx_text, encoding="utf-8")

    print(f"Done: {OUT_DIR}/")


if __name__ == "__main__":
    main()
