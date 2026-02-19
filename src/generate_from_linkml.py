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

        print(f"Generating OWL ontology -> {out_owl}")
        owl_gen = OwlSchemaGenerator(
            str(model_path), importmap=import_map, base_dir=base_dir
        )
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
