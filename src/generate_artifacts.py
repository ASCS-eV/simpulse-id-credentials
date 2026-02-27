#!/usr/bin/env python3
"""Generate downstream artifacts (JSON-LD context, SHACL shapes, OWL ontology)
from simpulseid LinkML schema using importmap for harbour resolution.

The SHACL generator is customised to fix known LinkML issues:
- importmap not passed to SchemaView in gen-shacl __post_init__
- sh:closed=true incompatible with multi-context JSON-LD credentials
- range: Any generating unusable sh:class linkml:Any constraints
- identifier slots generating sh:path on @id (not a real RDF property)
- imported shapes duplicating harbour's own artifacts
"""

import json
from pathlib import Path
from typing import Callable

from linkml.generators.jsonldcontextgen import ContextGenerator
from linkml.generators.owlgen import OwlSchemaGenerator
from linkml.generators.shaclgen import ShaclGenerator as _BaseShaclGenerator
from linkml_runtime.utils.schemaview import SchemaView
from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDF, SH

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA = REPO_ROOT / "linkml" / "simpulseid.yaml"
IMPORTMAP_FILE = REPO_ROOT / "linkml" / "importmap.json"
OUT_DIR = REPO_ROOT / "artifacts" / "simpulseid"

SIMPULSEID = Namespace("https://w3id.org/ascs-ev/simpulse-id/credentials/v1/")
LINKML = Namespace("https://w3id.org/linkml/")


class FixedShaclGenerator(_BaseShaclGenerator):
    """SHACL generator with fixes for domain-layer credential schemas.

    Fixes applied:
    1. Importmap passed to SchemaView (upstream gen-shacl bug).
    2. closed=False: open shapes for multi-context JSON-LD data.
    3. range: Any skips sh:class (nodeKind only, matching harbour pattern).
    4. Post-processing removes:
       - linkml:Any shape (dead; no class constraints reference it)
       - harbour:id properties (JSON-LD @id is not an RDF property)
       - Non-simpulseid shapes (harbour's own artifacts handle those)
    """

    def __post_init__(self) -> None:
        from linkml.utils.generator import Generator as BaseGenerator

        BaseGenerator.__post_init__(self)
        self.schemaview = SchemaView(
            self.schema, importmap=self.importmap or {}, base_dir=self.base_dir
        )
        self.generate_header()

    def _add_class(self, func: Callable, r: str) -> None:
        """Skip sh:class for Any range — emit nodeKind only."""
        if r == "Any":
            return
        super()._add_class(func, r)

    def as_graph(self) -> Graph:
        g = super().as_graph()
        return _cleanup_domain_shacl(g)


def _cleanup_domain_shacl(g: Graph) -> Graph:
    """Remove imported shapes and dead artefacts from domain SHACL graph.

    Domain schemas (like simpulseid) import harbour as a base. The SHACL
    generator re-emits shapes for all imported classes, but harbour's own
    artifacts already provide those. We keep only simpulseid:* shapes and
    clean up linkml:Any / harbour:id artefacts.
    """
    harbour_id = URIRef("https://w3id.org/reachhaven/harbour/credentials/v1/id")

    # Collect shapes to remove: anything not targeting simpulseid:* classes
    shapes_to_remove = set()
    for shape, _, target in g.triples((None, SH.targetClass, None)):
        if not str(target).startswith(str(SIMPULSEID)):
            shapes_to_remove.add(shape)

    # Also remove the linkml:Any shape
    linkml_any = LINKML.Any
    if (linkml_any, RDF.type, SH.NodeShape) in g:
        shapes_to_remove.add(linkml_any)

    # Remove all triples belonging to non-simpulseid shapes
    for shape in shapes_to_remove:
        # Remove property blank nodes
        for _, _, prop_node in g.triples((shape, SH.property, None)):
            for t in list(g.triples((prop_node, None, None))):
                g.remove(t)
        # Remove ignoredProperties list nodes
        for _, _, ignored in g.triples((shape, SH.ignoredProperties, None)):
            _remove_rdf_list(g, ignored)
        # Remove all direct triples on the shape
        for t in list(g.triples((shape, None, None))):
            g.remove(t)

    # Remove harbour:id property shapes from remaining simpulseid shapes
    # (id maps to @id in JSON-LD, not a real RDF property)
    for shape, _, prop_node in list(g.triples((None, SH.property, None))):
        if (prop_node, SH.path, harbour_id) in g:
            for t in list(g.triples((prop_node, None, None))):
                g.remove(t)
            g.remove((shape, SH.property, prop_node))

    # Deduplicate property shapes: inheritance causes the SHACL generator to
    # emit the same sh:path twice per shape (once from the local class, once
    # from the parent).  Keep the override (no sh:minCount) over the inherited
    # version; if tied, keep the lower sh:order.
    _deduplicate_properties(g)

    return g


def _deduplicate_properties(g: Graph) -> None:
    """Remove duplicate sh:property entries with the same sh:path on each shape."""
    for shape in set(s for s, _, _ in g.triples((None, SH.property, None))):
        # Group property blank nodes by their sh:path
        by_path: dict[URIRef, list] = {}
        for _, _, prop_node in g.triples((shape, SH.property, None)):
            path = g.value(prop_node, SH.path)
            if path is not None:
                by_path.setdefault(path, []).append(prop_node)

        for path, nodes in by_path.items():
            if len(nodes) <= 1:
                continue

            # Prefer the property without sh:minCount (the relaxed override)
            def sort_key(n):
                has_min = g.value(n, SH.minCount) is not None
                order = int(g.value(n, SH.order) or 999)
                return (has_min, order)

            nodes.sort(key=sort_key)
            for dup in nodes[1:]:
                for t in list(g.triples((dup, None, None))):
                    g.remove(t)
                g.remove((shape, SH.property, dup))


def _remove_rdf_list(g: Graph, node: URIRef) -> None:
    """Recursively remove an RDF list from the graph."""
    while node and node != RDF.nil:
        next_node = g.value(node, RDF.rest)
        for t in list(g.triples((node, None, None))):
            g.remove(t)
        node = next_node


def load_importmap() -> dict:
    if IMPORTMAP_FILE.exists():
        return json.loads(IMPORTMAP_FILE.read_text())
    return {}


def main() -> None:
    import_map = load_importmap()
    base_dir = str(SCHEMA.parent)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    owl_path = OUT_DIR / "simpulseid.owl.ttl"
    shacl_path = OUT_DIR / "simpulseid.shacl.ttl"
    context_path = OUT_DIR / "simpulseid.context.jsonld"

    print("Generating OWL ontology...")
    owl_gen = OwlSchemaGenerator(str(SCHEMA), importmap=import_map, base_dir=base_dir)
    owl_path.write_text(owl_gen.serialize(), encoding="utf-8")

    print("Generating SHACL shapes...")
    shacl_gen = FixedShaclGenerator(
        str(SCHEMA), importmap=import_map, base_dir=base_dir, closed=False
    )
    shacl_path.write_text(shacl_gen.serialize(), encoding="utf-8")

    print("Generating JSON-LD context...")
    ctx_gen = ContextGenerator(str(SCHEMA), importmap=import_map, base_dir=base_dir)
    context_path.write_text(ctx_gen.serialize(), encoding="utf-8")

    print(f"Done: {OUT_DIR}/")


if __name__ == "__main__":
    main()
