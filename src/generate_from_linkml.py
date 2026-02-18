#!/usr/bin/env python3
"""
Generate downstream artefacts (JSON-LD context, SHACL shapes, OWL ontology)
from one or more LinkML schemas.
"""

import argparse
import os
from pathlib import Path
from typing import Dict, List
from urllib.parse import urlparse

from linkml.generators.jsonldcontextgen import ContextGenerator
from linkml.generators.owlgen import OwlSchemaGenerator
from linkml.generators.shaclgen import ShaclGenerator as _BaseShaclGenerator
from linkml_runtime.utils.schemaview import SchemaView


def _remove_shape_props(g, shape_uri, predicates):
    """Remove specific predicates from a SHACL shape node. Returns count removed."""
    removed = 0
    for pred in predicates:
        for s, p, o in list(g.triples((shape_uri, pred, None))):
            g.remove((s, p, o))
            removed += 1
    return removed


def postprocess_shacl(
    shacl_path: Path, model_path: Path, import_map: Dict[str, str]
) -> None:
    """Post-process generated SHACL to fix known LinkML generator issues.

    Fixes applied:
    1. Abstract classes: remove sh:targetClass (prevents matching nested instances)
    2. All shapes: remove sh:closed and sh:ignoredProperties (incompatible with
       RDFS inference — inferred parent types cause nodes to match multiple closed
       shapes with conflicting property sets)
    3. Identifier slots: remove sh:minCount from property shapes
       (identifier: true maps to @id in JSON-LD, never emits a property triple)
    4. designates_type slots: remove property shapes for rdf:type
       (designates_type maps to @type; values are IRIs, not xsd:anyURI literals)
    5. linkml:Any: remove sh:class constraints and the Any node shape
       (range: Any means unconstrained, not "must be typed linkml:Any")
    """
    from rdflib import Graph, Namespace, URIRef
    from rdflib.namespace import RDF

    SH = Namespace("http://www.w3.org/ns/shacl#")
    LINKML = Namespace("https://w3id.org/linkml/")

    base_dir = str(model_path.parent)
    sv = SchemaView(str(model_path), importmap=import_map, base_dir=base_dir)

    g = Graph()
    g.parse(shacl_path, format="turtle")
    removed = 0

    # --- 1. Abstract classes: remove sh:targetClass ---
    for cls_name, cls_def in sv.all_classes().items():
        if cls_def.abstract:
            uri = sv.get_uri(cls_def, expand=True)
            if uri:
                shape = URIRef(str(uri))
                removed += _remove_shape_props(g, shape, [SH.targetClass])

    # --- 2. All shapes: remove sh:closed and sh:ignoredProperties ---
    for shape in g.subjects(SH.closed, None):
        removed += _remove_shape_props(g, shape, [SH.closed, SH.ignoredProperties])

    # --- 3. Identifier slots: remove sh:minCount (maps to @id, not a triple) ---
    for slot_name, slot_def in sv.all_slots().items():
        if slot_def.identifier:
            uri = sv.get_uri(slot_def, expand=True)
            if uri:
                id_uri = URIRef(str(uri))
                for bnode in g.subjects(SH.path, id_uri):
                    for s, p, o in list(g.triples((bnode, SH.minCount, None))):
                        g.remove((s, p, o))
                        removed += 1

    # --- 4. designates_type: remove rdf:type property shapes ---
    # The type slot (designates_type: true) generates sh:datatype xsd:anyURI
    # and sh:nodeKind sh:Literal for rdf:type, but rdf:type values are IRIs.
    # Remove the entire property shape for rdf:type from all node shapes.
    rdf_type = RDF.type
    for bnode in list(g.subjects(SH.path, rdf_type)):
        # Remove all triples on this blank node (the property shape)
        for s, p, o in list(g.triples((bnode, None, None))):
            g.remove((s, p, o))
            removed += 1
        # Remove references to this blank node from parent shapes
        for s, p, o in list(g.triples((None, SH.property, bnode))):
            g.remove((s, p, o))
            removed += 1

    # --- 5. linkml:Any: remove class constraints and node shape ---
    any_uri = LINKML.Any
    for s, p, o in list(g.triples((None, SH["class"], any_uri))):
        g.remove((s, p, o))
        removed += 1
    # Remove the linkml:Any node shape entirely
    for s, p, o in list(g.triples((any_uri, None, None))):
        g.remove((s, p, o))
        removed += 1

    # --- 6. Enum sh:in: remove all enum constraints ---
    # LinkML-generated sh:in constraints are incompatible with JSON-LD data in
    # several ways: meaning URIs vs string literals, sh:or wrapping, and datatype
    # mismatches. Structural validation (cardinality, class, datatype) is sufficient.
    from rdflib.collection import Collection

    for s, p, list_node in list(g.triples((None, SH["in"], None))):
        try:
            coll = Collection(g, list_node)
            coll.clear()
        except Exception:
            pass
        g.remove((s, p, list_node))
        removed += 1

    if removed:
        shacl_path.write_text(g.serialize(format="turtle"), encoding="utf-8")
        print(f"  Post-processed SHACL: {removed} triples removed")


def postprocess_owl(owl_path: Path) -> None:
    """Add rdfs:subClassOf for classes with external class_uri mappings.

    LinkML maps classes to external IRIs via class_uri (e.g., Evidence → cred:Evidence).
    The OWL generator creates the local class (harbour:Evidence) with skos:exactMatch
    to the external IRI, but RDFS inference needs rdfs:subClassOf to propagate type
    assertions through the class hierarchy.
    """
    from rdflib import Graph, Namespace
    from rdflib.namespace import OWL, RDF, RDFS

    SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")

    g = Graph()
    g.parse(owl_path, format="turtle")

    added = 0
    for local_uri, _, external_uri in list(g.triples((None, SKOS.exactMatch, None))):
        if local_uri == external_uri:
            continue
        if (local_uri, RDF.type, OWL.Class) not in g:
            continue
        if (local_uri, RDFS.subClassOf, external_uri) not in g:
            g.add((local_uri, RDFS.subClassOf, external_uri))
            added += 1

    if added:
        owl_path.write_text(g.serialize(format="turtle"), encoding="utf-8")
        print(
            f"  Post-processed OWL: added {added} rdfs:subClassOf for external class_uri"
        )


def debug(msg: str) -> None:
    print(f"[DEBUG] {msg}")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def find_repo_root(start: Path) -> Path:
    current = start
    while current != current.parent:
        if (current / "submodules" / "ontology-management-base").is_dir() or (
            current / ".git"
        ).is_dir():
            return current
        current = current.parent
    return start.parent


def build_import_map(repo_root: Path) -> Dict[str, str]:
    candidates = [
        repo_root / "submodules" / "service-characteristics" / "linkml",
        repo_root / "service-characteristics" / "linkml",
    ]
    gaiax_linkml_dir = next((d for d in candidates if d.is_dir()), None)

    import_map: Dict[str, str] = {}

    if not gaiax_linkml_dir:
        debug(f"Gaia-X linkml dir not found in candidates: {candidates}")
        return import_map

    for yaml_file in gaiax_linkml_dir.glob("*.yaml"):
        abs_path = str(yaml_file.with_suffix("").resolve())
        import_map[yaml_file.stem] = abs_path
        # Relative path from repo_root/linkml/ (used by simpulseid.yaml)
        legacy_path = f"../submodules/service-characteristics/linkml/{yaml_file.stem}"
        import_map[legacy_path] = abs_path
        import_map[f"{legacy_path}.yaml"] = abs_path
        # Relative path from harbour-credentials/linkml/ (used by harbour.yaml)
        harbour_rel = f"../../service-characteristics/linkml/{yaml_file.stem}"
        import_map[harbour_rel] = abs_path
        import_map[f"{harbour_rel}.yaml"] = abs_path

    debug(f"Built import_map with {len(import_map)} entries from {gaiax_linkml_dir}")

    # Add harbour-credentials linkml dir to import map
    harbour_linkml_dir = repo_root / "submodules" / "harbour-credentials" / "linkml"
    if harbour_linkml_dir.is_dir():
        for yaml_file in harbour_linkml_dir.glob("*.yaml"):
            abs_path = str(yaml_file.with_suffix("").resolve())
            import_map[yaml_file.stem] = abs_path
            # Also map ./name (relative import used within harbour-credentials)
            import_map[f"./{yaml_file.stem}"] = abs_path

    return import_map


def iri_to_model_name(iri: str) -> str:
    path = urlparse(iri).path
    parts = [p for p in path.split("/") if p]
    return parts[0].lower() if parts else "unknown"


class FixedShaclGenerator(_BaseShaclGenerator):
    """Ensure SchemaView is built with the same importmap/base_dir as the loader."""

    def __post_init__(self) -> None:
        from linkml.utils.generator import Generator as BaseGenerator

        BaseGenerator.__post_init__(self)
        self.schemaview = SchemaView(
            self.schema, importmap=self.importmap or {}, base_dir=self.base_dir
        )
        self.generate_header()


def set_linkml_model_path(repo_root: Path) -> None:
    gaiax_linkml_dirs = [
        repo_root / "submodules" / "service-characteristics" / "linkml",
        repo_root / "service-characteristics" / "linkml",
    ]
    local_linkml_dir = repo_root / "linkml"
    harbour_linkml_dir = repo_root / "submodules" / "harbour-credentials" / "linkml"

    search_paths: List[str] = []

    for d in gaiax_linkml_dirs:
        if d.is_dir():
            search_paths.append(str(d))

    if harbour_linkml_dir.is_dir():
        search_paths.append(str(harbour_linkml_dir))

    if local_linkml_dir.is_dir():
        search_paths.append(str(local_linkml_dir))

    existing_env = os.environ.get("LINKML_MODEL_PATH")
    if existing_env:
        search_paths.append(existing_env)

    if search_paths:
        os.environ["LINKML_MODEL_PATH"] = os.pathsep.join(search_paths)
        debug(f"LINKML_MODEL_PATH set to: {os.environ['LINKML_MODEL_PATH']}")


def get_model_name(model_path: Path, import_map: Dict[str, str], base_dir: str) -> str:
    sv = SchemaView(str(model_path), importmap=import_map, base_dir=base_dir)
    # Prefer explicit 'name' from YAML
    if sv.schema.name:
        return sv.schema.name

    # Fallback to parsing the ID
    sid = getattr(sv.schema, "id", None)
    if sid:
        return iri_to_model_name(sid)

    # Final fallback to filename
    return model_path.stem.lower()


def generate_one(model_path: Path, out_root: Path, import_map: Dict[str, str]) -> None:
    base_dir = str(model_path.parent)

    model_name = get_model_name(model_path, import_map, base_dir)

    out_dir = out_root / model_name
    ensure_dir(out_dir)

    out_context = out_dir / f"{model_name}.context.jsonld"
    out_shacl = out_dir / f"{model_name}.shacl.ttl"
    out_owl = out_dir / f"{model_name}.owl.ttl"

    debug(f"Model: {model_path}")
    debug(f"model_name={model_name!r}")
    debug(f"Outputs: {out_dir}")

    old_cwd = Path.cwd()
    os.chdir(model_path.parent)
    try:
        print(f"Using LinkML model: {model_path}")

        print(f"Generating JSON-LD context -> {out_context}")
        # The ContextGenerator handles @id/@type automatically due to identifier: true and designates_type: true
        ctx_gen = ContextGenerator(
            str(model_path), importmap=import_map, base_dir=base_dir
        )
        out_context.write_text(ctx_gen.serialize(), encoding="utf-8")

        print(f"Generating SHACL shapes -> {out_shacl}")
        shacl_gen = FixedShaclGenerator(
            str(model_path), importmap=import_map, base_dir=base_dir
        )
        out_shacl.write_text(shacl_gen.serialize(), encoding="utf-8")
        postprocess_shacl(out_shacl, model_path, import_map)

        print(f"Generating OWL ontology -> {out_owl}")
        owl_gen = OwlSchemaGenerator(
            str(model_path), importmap=import_map, base_dir=base_dir
        )
        out_owl.write_text(owl_gen.serialize(), encoding="utf-8")
        postprocess_owl(out_owl)

        print(f"Done: {model_name}")
    finally:
        os.chdir(old_cwd)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate JSON-LD context, SHACL shapes and OWL ontology from one or more LinkML models."
    )
    parser.add_argument(
        "--model",
        action="append",
        required=False,
        help="Path to a LinkML YAML schema. If not provided, defaults to all *.yaml files in the 'linkml' directory (non-recursive).",
    )
    parser.add_argument(
        "--out-root",
        default=None,
        help="Root output folder. When set, all models output here. "
        "When omitted, auto-discover routes each model to its own artifacts/ dir.",
    )

    args = parser.parse_args()

    explicit_out_root = args.out_root is not None

    if args.model:
        models = [Path(m).resolve() for m in args.model]
    else:
        repo_root = find_repo_root(Path.cwd())
        linkml_dir = repo_root / "linkml"

        if not linkml_dir.is_dir():
            linkml_dir = Path("linkml").resolve()

        if not linkml_dir.is_dir():
            raise SystemExit(
                f"Error: No --model provided and 'linkml' directory not found at {repo_root / 'linkml'}"
            )

        print(f"No --model specified. Auto-detecting *.yaml in {linkml_dir}...")
        models = sorted(list(linkml_dir.glob("*.yaml")))

        # Also discover models from submodule linkml dirs
        harbour_linkml = repo_root / "submodules" / "harbour-credentials" / "linkml"
        if harbour_linkml.is_dir():
            models.extend(sorted(harbour_linkml.glob("*.yaml")))

        if not models:
            raise SystemExit(f"Error: No .yaml files found in {linkml_dir}")

    for mp in models:
        if not mp.exists():
            raise SystemExit(f"LinkML model not found: {mp}")

    repo_root = find_repo_root(models[0].parent)
    debug(f"repo_root: {repo_root}")

    import_map = build_import_map(repo_root)
    set_linkml_model_path(repo_root)

    harbour_linkml_dir = (
        repo_root / "submodules" / "harbour-credentials" / "linkml"
    ).resolve()

    for mp in models:
        if explicit_out_root:
            out_root = Path(args.out_root).resolve()
        elif mp.resolve().parent == harbour_linkml_dir:
            out_root = (
                repo_root / "submodules" / "harbour-credentials" / "artifacts"
            ).resolve()
        else:
            out_root = (repo_root / "artifacts").resolve()

        ensure_dir(out_root)
        generate_one(mp, out_root, import_map)


if __name__ == "__main__":
    main()
