#!/usr/bin/env python3
"""
Generate downstream artefacts (JSON-LD context, SHACL shapes, OWL ontology)
from one or more LinkML schemas.

Examples:
  python3 src/generate_from_linkml.py --model linkml/simpulseid.yaml
  python3 src/generate_from_linkml.py --model linkml/simpulseid.yaml --model linkml/harbour.yaml
"""

import argparse
import os
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urlparse

from linkml.generators.jsonldcontextgen import ContextGenerator
from linkml.generators.owlgen import OwlSchemaGenerator
from linkml.generators.shaclgen import ShaclGenerator as _BaseShaclGenerator
from linkml_runtime.utils.schemaview import SchemaView
import json

def patch_jsonld_keywords(context_json: str) -> str:
    """
    LinkML cannot use '@id'/'@type' as slot_uri (loader rejects it).
    We therefore patch the generated context to alias:
      - id -> @id
      - type -> @type
    """
    doc = json.loads(context_json)
    ctx = doc.get("@context")
    if isinstance(ctx, dict):
        ctx["id"] = "@id"
        ctx["type"] = "@type"
    return json.dumps(doc, indent=2, ensure_ascii=False) + "\n"


def debug(msg: str) -> None:
    print(f"[DEBUG] {msg}")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def find_repo_root(start: Path) -> Path:
    current = start
    while current != current.parent:
        if (current / ".git").is_dir() or (current / "service-characteristics").is_dir():
            return current
        current = current.parent
    return start.parent


def build_import_map(repo_root: Path) -> Dict[str, str]:
    gaiax_linkml_dir = repo_root / "service-characteristics" / "linkml"
    import_map: Dict[str, str] = {}

    if not gaiax_linkml_dir.is_dir():
        debug(f"Gaia-X linkml dir not found at {gaiax_linkml_dir}")
        return import_map

    for yaml_file in gaiax_linkml_dir.glob("*.yaml"):
        import_map[yaml_file.stem] = str(yaml_file.with_suffix("").resolve())

    debug(f"Built import_map with {len(import_map)} entries from {gaiax_linkml_dir}")
    return import_map


def iri_to_model_name(iri: str) -> str:
    path = urlparse(iri).path
    parts = [p for p in path.split("/") if p]
    return (parts[0].lower() if parts else "unknown")


class FixedShaclGenerator(_BaseShaclGenerator):
    """Ensure SchemaView is built with the same importmap/base_dir as the loader."""

    def __post_init__(self) -> None:
        from linkml.utils.generator import Generator as BaseGenerator

        BaseGenerator.__post_init__(self)
        self.schemaview = SchemaView(self.schema, importmap=self.importmap or {}, base_dir=self.base_dir)
        self.generate_header()


def set_linkml_model_path(repo_root: Path) -> None:
    gaiax_linkml_dir = repo_root / "service-characteristics" / "linkml"
    local_linkml_dir = repo_root / "linkml"

    search_paths: List[str] = []
    if gaiax_linkml_dir.is_dir():
        search_paths.append(str(gaiax_linkml_dir))
    if local_linkml_dir.is_dir():
        search_paths.append(str(local_linkml_dir))

    existing_env = os.environ.get("LINKML_MODEL_PATH")
    if existing_env:
        search_paths.append(existing_env)

    if search_paths:
        os.environ["LINKML_MODEL_PATH"] = os.pathsep.join(search_paths)
        debug(f"LINKML_MODEL_PATH set to: {os.environ['LINKML_MODEL_PATH']}")


def schema_id_for(model_path: Path, import_map: Dict[str, str], base_dir: str) -> Optional[str]:
    sv = SchemaView(str(model_path), importmap=import_map, base_dir=base_dir)
    return getattr(sv.schema, "id", None)


def generate_one(model_path: Path, out_root: Path, import_map: Dict[str, str]) -> None:
    base_dir = str(model_path.parent)

    sid = schema_id_for(model_path, import_map, base_dir)
    model_name = iri_to_model_name(sid) if sid else model_path.stem.lower()

    out_dir = out_root / model_name
    ensure_dir(out_dir)

    out_context = out_dir / f"{model_name}_context.jsonld"
    out_shacl = out_dir / f"{model_name}_shacl.ttl"
    out_owl = out_dir / f"{model_name}_ontology.ttl"

    debug(f"Model: {model_path}")
    debug(f"schema_id={sid!r} -> model_name={model_name!r}")
    debug(f"Outputs: {out_dir}")

    old_cwd = Path.cwd()
    os.chdir(model_path.parent)
    try:
        print(f"Using LinkML model: {model_path}")

        print(f"Generating JSON-LD context -> {out_context}")
        ctx_gen = ContextGenerator(str(model_path), importmap=import_map, base_dir=base_dir)
        out_context.write_text(patch_jsonld_keywords(ctx_gen.serialize()), encoding="utf-8")

        print(f"Generating SHACL shapes -> {out_shacl}")
        shacl_gen = FixedShaclGenerator(str(model_path), importmap=import_map, base_dir=base_dir)
        out_shacl.write_text(shacl_gen.serialize(), encoding="utf-8")

        print(f"Generating OWL ontology -> {out_owl}")
        owl_gen = OwlSchemaGenerator(str(model_path), importmap=import_map, base_dir=base_dir)
        out_owl.write_text(owl_gen.serialize(), encoding="utf-8")

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
        required=True,
        help="Path to a LinkML YAML schema. Repeat --model for multiple schemas.",
    )
    parser.add_argument(
        "--out-root",
        default="generated",
        help="Root output folder (default: generated). Each schema is generated into generated/<model_name>/",
    )

    args = parser.parse_args()

    models = [Path(m).resolve() for m in args.model]
    for mp in models:
        if not mp.exists():
            raise SystemExit(f"LinkML model not found: {mp}")

    repo_root = find_repo_root(models[0].parent)
    debug(f"repo_root: {repo_root} (exists={repo_root.exists()}, type={'dir' if repo_root.is_dir() else 'missing'})")

    import_map = build_import_map(repo_root)
    set_linkml_model_path(repo_root)

    out_root = Path(args.out_root).resolve()
    ensure_dir(out_root)

    for mp in models:
        generate_one(mp, out_root, import_map)


if __name__ == "__main__":
    main()
