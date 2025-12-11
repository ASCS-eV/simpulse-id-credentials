#!/usr/bin/env python3
"""
Generate downstream artefacts (JSON-LD context, SHACL shapes, OWL ontology)
from the SimpulseID LinkML schema.

Usage examples:

    python src/generate_from_linkml.py \
        --model linkml/simpulseid-model.yaml

    # With explicit output paths:
    python src/generate_from_linkml.py \
        --model linkml/simpulseid-model.yaml \
        --out-context generated/contexts/SimpulseIdCredentials.context.jsonld \
        --out-shacl generated/ontologies/SimpulseIdShacl.ttl \
        --out-owl generated/ontologies/SimpulseIdOntology.ttl

The script writes ALL artefacts into the /generated/* folder so that
hand-written files in /contexts and /ontologies remain untouched for diffing.
"""

import argparse
import os
from pathlib import Path
from typing import Dict

# NOTE: JSONLDContextGenerator was renamed to ContextGenerator in recent LinkML versions
from linkml.generators.jsonldcontextgen import ContextGenerator
from linkml.generators.shaclgen import ShaclGenerator
from linkml.generators.owlgen import OwlSchemaGenerator


def debug(msg: str) -> None:
    print(f"[DEBUG] {msg}")


def ensure_parent_dir(path: Path) -> None:
    if path.parent and not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)


def find_repo_root(start: Path) -> Path:
    """
    Heuristic to find the repo root starting from the model path.

    We walk upwards until we find either:
    - a .git directory, or
    - a 'service-characteristics' directory.

    If nothing is found, we return the starting directory's parent.
    """
    current = start
    while current != current.parent:
        if (current / ".git").is_dir() or (current / "service-characteristics").is_dir():
            return current
        current = current.parent
    # Fallback: parent of start
    return start.parent


def build_import_map(repo_root: Path) -> Dict[str, str]:
    """
    Build an import map for SchemaLoader so that imports like 'address',
    'country-names', 'legal-person', etc. used inside Gaia-X's gaia-x.yaml
    resolve to the actual files under service-characteristics/linkml.

    We map:

        'address' -> '/abs/path/service-characteristics/linkml/address'
        'country-names' -> '/abs/path/service-characteristics/linkml/country-names'
        ...

    SchemaLoader will then append '.yaml' and treat the value as an absolute
    file path, bypassing the incorrect 'linkml/address.yaml' resolution.
    """
    gaiax_linkml_dir = repo_root / "service-characteristics" / "linkml"
    import_map: Dict[str, str] = {}

    if not gaiax_linkml_dir.is_dir():
        debug(
            f"Gaia-X linkml dir not found at {gaiax_linkml_dir} "
            f"(exists={gaiax_linkml_dir.exists()}, type={'dir' if gaiax_linkml_dir.is_dir() else 'missing'})"
        )
        return import_map

    for yaml_file in gaiax_linkml_dir.glob("*.yaml"):
        stem = yaml_file.stem  # e.g. 'address', 'country-names'
        # Absolute path *without* .yaml; SchemaLoader will add '.yaml'
        import_map[stem] = str(yaml_file.with_suffix("").resolve())

    debug(f"Built import_map with {len(import_map)} entries from {gaiax_linkml_dir}")
    # Print a few sample entries for debugging
    for i, (k, v) in enumerate(sorted(import_map.items())):
        if i >= 10:
            break
        debug(f"  import_map[{k!r}] = {v!r}")

    return import_map


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate JSON-LD context, SHACL shapes and OWL ontology from a LinkML model."
    )
    parser.add_argument(
        "--model",
        required=True,
        help="Path to the LinkML YAML schema (e.g. linkml/simpulseid-model.yaml).",
    )
    parser.add_argument(
        "--out-context",
        default="generated/contexts/SimpulseIdCredentials.context.jsonld",
        help="Output path for the generated JSON-LD context.",
    )
    parser.add_argument(
        "--out-shacl",
        default="generated/ontologies/SimpulseIdShacl.ttl",
        help="Output path for the generated SHACL shapes.",
    )
    parser.add_argument(
        "--out-owl",
        default="generated/ontologies/SimpulseIdOntology.ttl",
        help="Output path for the generated OWL ontology.",
    )

    args = parser.parse_args()

    cwd = Path.cwd()
    model_path = Path(args.model).resolve()

    debug(f"Current working directory: {cwd}")
    debug(f"Model path (resolved): {model_path}")

    if not model_path.exists():
        raise SystemExit(f"LinkML model not found: {model_path}")

    repo_root = find_repo_root(model_path.parent)
    debug(
        f"repo_root: {repo_root}  (exists={repo_root.exists()}, "
        f"type={'dir' if repo_root.is_dir() else 'missing'})"
    )

    # Build import map for Gaia-X schemas under service-characteristics/linkml
    import_map = build_import_map(repo_root)
    debug(f"Import map keys (first 10): {sorted(list(import_map.keys()))[:10]}")

    # We keep LINKML_MODEL_PATH for other tools if you are using them,
    # but the *critical* part for this script is import_map above.
    gaiax_linkml_dir = repo_root / "service-characteristics" / "linkml"
    local_linkml_dir = repo_root / "linkml"
    search_paths = []

    if gaiax_linkml_dir.is_dir():
        search_paths.append(str(gaiax_linkml_dir))
    if local_linkml_dir.is_dir():
        search_paths.append(str(local_linkml_dir))

    existing_env = os.environ.get("LINKML_MODEL_PATH")
    if existing_env:
        search_paths.append(existing_env)

    if search_paths:
        new_value = os.pathsep.join(search_paths)
        os.environ["LINKML_MODEL_PATH"] = new_value
        debug(f"LINKML_MODEL_PATH set to: {new_value}")
    else:
        debug(
            "Warning: could not find 'service-characteristics/linkml' or 'linkml' "
            "directories relative to the model; imports may fail."
        )

    out_context = Path(args.out_context).resolve()
    out_shacl = Path(args.out_shacl).resolve()
    out_owl = Path(args.out_owl).resolve()

    debug(
        f"out_context: {out_context}  (exists={out_context.exists()}, "
        f"type={'file' if out_context.is_file() else 'missing'})"
    )
    debug(
        f"out_shacl: {out_shacl}  (exists={out_shacl.exists()}, "
        f"type={'file' if out_shacl.is_file() else 'missing'})"
    )
    debug(
        f"out_owl: {out_owl}  (exists={out_owl.exists()}, "
        f"type={'file' if out_owl.is_file() else 'missing'})"
    )

    # Ensure /generated/* directory structure exists
    ensure_parent_dir(out_context)
    ensure_parent_dir(out_shacl)
    ensure_parent_dir(out_owl)

    print(f"Using LinkML model: {model_path}")

    # For relative imports in simpulseid-model.yaml itself, having base_dir=model_path.parent
    # is the most intuitive setup.
    base_dir = str(model_path.parent)
    debug(f"Using base_dir for generators: {base_dir}")

    # Change working directory only for the generators' internal filesystem logic
    old_cwd = Path.cwd()
    os.chdir(model_path.parent)
    try:
        # 1) JSON-LD context
        print(f"Generating JSON-LD context -> {out_context}")
        debug("Initializing ContextGenerator with importmap and base_dir")
        try:
            ctx_gen = ContextGenerator(
                str(model_path),
                importmap=import_map,
                base_dir=base_dir,
            )
        except Exception as e:
            debug("ContextGenerator initialization failed. "
                  "This usually indicates a schema modelling problem "
                  "(e.g. duplicate identifiers, conflicting slot names, "
                  "or unresolved imports).")
            raise

        context_str = ctx_gen.serialize()
        out_context.write_text(context_str, encoding="utf-8")

        # 2) SHACL shapes
        print(f"Generating SHACL shapes -> {out_shacl}")
        debug("Initializing ShaclGenerator with importmap and base_dir")
        try:
            shacl_gen = ShaclGenerator(
                str(model_path),
                importmap=import_map,
                base_dir=base_dir,
            )
        except Exception as e:
            debug("ShaclGenerator initialization failed. "
                  "This is likely due to the same schema issues reported "
                  "by the JSON-LD context generation step.")
            raise

        shacl_str = shacl_gen.serialize()
        out_shacl.write_text(shacl_str, encoding="utf-8")

        # 3) OWL ontology
        print(f"Generating OWL ontology -> {out_owl}")
        debug("Initializing OwlSchemaGenerator with importmap and base_dir")
        try:
            owl_gen = OwlSchemaGenerator(
                str(model_path),
                importmap=import_map,
                base_dir=base_dir,
            )
        except Exception as e:
            debug("OwlSchemaGenerator initialization failed. "
                  "Again, likely a modelling issue in the LinkML schema.")
            raise

        owl_str = owl_gen.serialize()
        out_owl.write_text(owl_str, encoding="utf-8")
    finally:
        os.chdir(old_cwd)

    print("Done. Generated artefacts in /generated/* for comparison with hand-written files.")


if __name__ == "__main__":
    main()
