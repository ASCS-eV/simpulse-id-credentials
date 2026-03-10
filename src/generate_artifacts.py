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

from linkml.generators.jsonldcontextgen import ContextGenerator as _BaseContextGenerator
from linkml.generators.owlgen import OwlSchemaGenerator
from linkml.generators.shaclgen import ShaclGenerator as _BaseShaclGenerator
from linkml_runtime.linkml_model.meta import SlotDefinition
from rdflib import Namespace

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA = REPO_ROOT / "linkml" / "simpulseid.yaml"
IMPORTMAP_FILE = REPO_ROOT / "linkml" / "importmap.json"
OUT_DIR = REPO_ROOT / "artifacts" / "simpulseid"

SH = Namespace("http://www.w3.org/ns/shacl#")
LINKML = Namespace("https://w3id.org/linkml/")


class DomainContextGenerator(_BaseContextGenerator):
    """Context generator that excludes imported vocabulary terms.

    W3C VC v2 envelope terms (issuer, validFrom, validUntil, evidence,
    credentialStatus) are imported transitively via harbour schemas.
    This generator skips them so the simpulseid JSON-LD context does not
    redefine ``@protected`` terms already provided by the W3C VC v2 context
    (``https://www.w3.org/ns/credentials/v2``).

    Mirrors ``HarbourContextGenerator`` in harbour-credentials.
    """

    def visit_slot(self, aliased_slot_name: str, slot: SlotDefinition) -> None:
        if getattr(slot, "imported_from", None) and not str(
            slot.imported_from
        ).startswith("linkml"):
            return
        super().visit_slot(aliased_slot_name, slot)


class DomainShaclGenerator(_BaseShaclGenerator):
    """SHACL generator that bypasses ShaclGenerator.__post_init__'s broken
    SchemaView construction (which ignores importmap).

    Workaround for https://github.com/linkml/linkml/issues/2913 —
    ``ShaclGenerator.__post_init__`` creates ``SchemaView(self.schema)``
    without forwarding ``importmap`` / ``base_dir``, so cross-directory
    imports fail.  Still unfixed as of LinkML 1.10.0.

    Also removes ``sh:class linkml:Any`` constraints from the generated graph.
    LinkML emits these for ``range: Any`` slots, but ``linkml:Any`` is a
    meta-schema type that is never asserted as ``rdf:type`` on instance data,
    so the constraint always fails SHACL validation.  Removing it preserves
    ``sh:nodeKind sh:BlankNodeOrIRI`` which is the correct structural check.
    See https://github.com/linkml/linkml/issues/2914
    """

    uses_schemaloader = False

    def __post_init__(self) -> None:
        from linkml.utils.generator import Generator

        Generator.__post_init__(self)
        self.generate_header()

    def as_graph(self):
        g = super().as_graph()
        for s, p, o in list(g.triples((None, SH["class"], LINKML.Any))):
            g.remove((s, p, o))
        return g


def load_importmap() -> dict:
    if IMPORTMAP_FILE.exists():
        return json.loads(IMPORTMAP_FILE.read_text())
    return {}


def main() -> None:
    import_map = load_importmap()
    base_dir = str(SCHEMA.parent)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Generating OWL ontology...")
    owl_gen = OwlSchemaGenerator(str(SCHEMA), importmap=import_map, base_dir=base_dir)
    (OUT_DIR / "simpulseid.owl.ttl").write_text(owl_gen.serialize(), encoding="utf-8")

    print("Generating SHACL shapes...")
    shacl_gen = DomainShaclGenerator(
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
    ctx_gen = DomainContextGenerator(
        str(SCHEMA), importmap=import_map, base_dir=base_dir, mergeimports=False
    )
    ctx_text = ctx_gen.serialize()

    # Ensure "type": "@type" is present in the generated context.
    # LinkML cannot emit this alias without declaring a ``type`` slot, which
    # would override the W3C VCDM v2 ``"type": "@type"`` with a typed
    # property definition (see harbour-core-credential.yaml §slots comment).
    # The alias is required so that JSON-LD ``"type"`` maps to ``rdf:type``
    # instead of falling through to ``@vocab``.
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
