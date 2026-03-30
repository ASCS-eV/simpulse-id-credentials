#!/usr/bin/env python3
"""Generate downstream artifacts (JSON-LD context, SHACL shapes, OWL ontology)
from the simpulseid-core LinkML schema.

All three generators receive the schema file path, importmap, and base_dir
so that SchemaView resolves cross-directory imports (e.g. ``./harbour`` →
harbour-gx-credential in the submodule) via the standard importmap mechanism.

For SHACL, ``exclude_imports=True`` would strip *all* imports — including the
simpulseid-credentials schema that defines our credential types.  Instead we
generate shapes for every class, then filter the output to retain only shapes
whose ``sh:targetClass`` is in the simpulseid namespace.
"""

import json
from pathlib import Path

from linkml.generators.jsonldcontextgen import ContextGenerator
from linkml.generators.owlgen import OwlSchemaGenerator
from linkml.generators.shaclgen import ShaclGenerator
from rdflib import BNode, Graph, Namespace

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA = REPO_ROOT / "linkml" / "simpulseid-core.yaml"
IMPORTMAP_FILE = REPO_ROOT / "linkml" / "importmap.json"
OUT_DIR = REPO_ROOT / "artifacts" / "simpulseid-core"

SIMPULSEID_NS = Namespace("https://w3id.org/ascs-ev/simpulse-id/v1/")
SH = Namespace("http://www.w3.org/ns/shacl#")


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


def filter_shacl_to_namespace(shacl_text: str, namespace: Namespace) -> str:
    """Keep only SHACL node shapes whose sh:targetClass is in *namespace*."""
    g = Graph()
    g.parse(data=shacl_text, format="turtle")

    target_shapes = {
        shape
        for shape, _, target in g.triples((None, SH.targetClass, None))
        if str(target).startswith(str(namespace))
    }

    filtered = Graph()
    for pfx, ns in g.namespaces():
        filtered.bind(pfx, ns)

    def collect_reachable(node: object, visited: set | None = None) -> None:
        if visited is None:
            visited = set()
        if node in visited:
            return
        visited.add(node)
        for p, o in g.predicate_objects(node):
            filtered.add((node, p, o))
            if isinstance(o, BNode):
                collect_reachable(o, visited)

    for shape in target_shapes:
        collect_reachable(shape)

    return filtered.serialize(format="turtle")


def _context_gen_without_harbour(gen_args: dict) -> str:
    """Generate context JSON working around the publisher slot conflict.

    Both gaia-x and simpulseid define ``publisher`` with different
    ``from_schema`` URIs.  SchemaLoader.resolve() raises ValueError
    on such conflicts.  We temporarily patch merge_dicts to skip
    conflicting imported slots (target's definition wins), which is
    correct since ``mergeimports=False`` excludes imported terms anyway.
    """
    import linkml.utils.mergeutils as mu

    _orig_merge_dicts = mu.merge_dicts

    def _lenient_merge_dicts(
        target, source, imported_from, imported_from_uri, merge_imports
    ):
        """Like merge_dicts but skip conflicting slots from imports."""
        if not merge_imports:
            # Remove cross-schema conflicting slots from a shallow copy
            # so the original dicts are not mutated.
            safe = {
                k: v
                for k, v in source.items()
                if k not in target
                or not hasattr(target[k], "from_schema")
                or not hasattr(v, "from_schema")
                or target[k].from_schema == v.from_schema
            }
            return _orig_merge_dicts(
                target, safe, imported_from, imported_from_uri, merge_imports
            )
        return _orig_merge_dicts(
            target, source, imported_from, imported_from_uri, merge_imports
        )

    mu.merge_dicts = _lenient_merge_dicts
    try:
        ctx_gen = ContextGenerator(
            str(SCHEMA),
            mergeimports=False,
            exclude_external_imports=True,
            xsd_anyuri_as_iri=True,
            normalize_prefixes=True,
            deterministic=True,
            **gen_args,
        )
        return ctx_gen.serialize()
    finally:
        mu.merge_dicts = _orig_merge_dicts


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
        deterministic=True,
        normalize_prefixes=True,
        **gen_args,
    )
    raw_shacl = shacl_gen.serialize()
    filtered_shacl = filter_shacl_to_namespace(raw_shacl, SIMPULSEID_NS)
    (OUT_DIR / "simpulseid-core.shacl.ttl").write_text(filtered_shacl, encoding="utf-8")

    # --- JSON-LD context ---
    print("Generating JSON-LD context...")
    # Work around a SchemaLoader slot-merging conflict: both gaia-x and
    # simpulseid define a ``publisher`` slot with different ``from_schema``
    # values and ranges (string vs ProgramPublisher).  SchemaLoader.resolve()
    # raises ValueError on such conflicts.  Since ``mergeimports=False``
    # excludes imported terms from the context anyway, we strip the
    # harbour import before passing the schema to ContextGenerator.
    ctx_text = _context_gen_without_harbour(gen_args)

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
