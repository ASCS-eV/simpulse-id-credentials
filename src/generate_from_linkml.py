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
        --out-shacl   generated/ontologies/SimpulseIdShacl.ttl \
        --out-owl     generated/ontologies/SimpulseIdOntology.ttl

The script writes ALL artefacts into the /generated/* folder so that
hand-written files in /contexts and /ontologies remain untouched for diffing.
"""

import argparse
import os
from pathlib import Path
from typing import Dict

from linkml.generators.jsonldcontextgen import ContextGenerator
from linkml.generators.owlgen import OwlSchemaGenerator
from linkml.generators.shaclgen import ShaclGenerator as _BaseShaclGenerator
from linkml_runtime.utils.schemaview import SchemaView


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
    Build an import map for Gaia-X LinkML modules so that imports like
    'address', 'legal-person', 'vm-image', etc. resolve to the actual files under
    service-characteristics/linkml.

    We map:

        'address'      -> '/abs/path/service-characteristics/linkml/address'
        'vm-image'     -> '/abs/path/service-characteristics/linkml/vm-image'
        'legal-person' -> '/abs/path/service-characteristics/linkml/legal-person'
        ...

    SchemaLoader / SchemaView will then append '.yaml' and treat the value
    as an absolute file path, bypassing incorrect 'linkml/*.yaml' resolution.
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
        stem = yaml_file.stem  # e.g. 'address', 'country-names', 'vm-image'
        import_map[stem] = str(yaml_file.with_suffix("").resolve())

    debug(f"Built import_map with {len(import_map)} entries from {gaiax_linkml_dir}")
    # Show a few sample entries
    sample_keys = sorted(import_map.keys())[:10]
    debug(f"Import map keys (first {len(sample_keys)}): {sample_keys}")
    return import_map


# ---------------------------------------------------------------------------
# Fixed ShaclGenerator that correctly propagates importmap into SchemaView
# ---------------------------------------------------------------------------

class FixedShaclGenerator(_BaseShaclGenerator):
    """
    Wrapper around the stock ShaclGenerator.

    The original ShaclGenerator.__post_init__ builds its own SchemaView without
    using the importmap. That causes imports like 'vm-image', 'legal-person',
    etc. to be resolved again relative to linkml/, which is why you saw
    errors like 'linkml/vm-image.yaml'.

    Here we:

    1) Run the base Generator.__post_init__ to get a fully resolved SchemaDefinition
       via SchemaLoader (which *does* use importmap).
    2) Build a SchemaView from that resolved schema, explicitly passing the same
       importmap (and base_dir) so any further import resolution inside SchemaView
       uses the Gaia-X paths, not linkml/.
    """

    def __post_init__(self) -> None:
        from linkml.utils.generator import Generator as BaseGenerator

        debug("[FixedShaclGenerator] __post_init__ starting")
        debug(f"[FixedShaclGenerator] raw schema parameter type: {type(self.schema)}")

        # Run only the generic Generator logic (SchemaLoader etc.), NOT the
        # original ShaclGenerator.__post_init__ which would create its own SchemaView.
        debug("[FixedShaclGenerator] Running BaseGenerator.__post_init__ (SchemaLoader + imports)")
        BaseGenerator.__post_init__(self)

        debug(
            "[FixedShaclGenerator] After BaseGenerator.__post_init__: "
            f"schema.name={getattr(self.schema, 'name', None)!r}, "
            f"schema.id={getattr(self.schema, 'id', None)!r}, "
            f"base_dir={self.base_dir!r}, "
            f"importmap entries={len(self.importmap) if getattr(self, 'importmap', None) else 0}"
        )

        # Now create a SchemaView that knows about the same importmap.
        debug("[FixedShaclGenerator] Building SchemaView from resolved schema with importmap + base_dir")
        sv = SchemaView(self.schema, importmap=self.importmap or {}, base_dir=self.base_dir)

        debug(
            "[FixedShaclGenerator] SchemaView created: "
            f"root schema={sv.schema.name!r}, "
            f"importmap entries={len(sv.importmap)}"
        )
        if sv.importmap:
            some_keys = sorted(sv.importmap.keys())[:10]
            debug(f"[FixedShaclGenerator] SchemaView.importmap keys (first {len(some_keys)}): {some_keys}")

        # Attach to self so ShaclGenerator.as_graph() can use it.
        self.schemaview = sv

        # Generate SHACL header as usual
        self.generate_header()
        debug("[FixedShaclGenerator] __post_init__ completed")


# ---------------------------------------------------------------------------
# Main script
# ---------------------------------------------------------------------------

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

    model_path = Path(args.model).resolve()
    if not model_path.exists():
        raise SystemExit(f"LinkML model not found: {model_path}")

    repo_root = find_repo_root(model_path.parent)
    debug(f"repo_root: {repo_root}  (exists={repo_root.exists()}, type={'dir' if repo_root.is_dir() else 'missing'})")

    # Build import map for Gaia-X schemas under service-characteristics/linkml
    import_map = build_import_map(repo_root)

    # Keep LINKML_MODEL_PATH for other tools, although our import_map is the critical part.
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

    cwd = Path.cwd()
    debug(f"Current working directory: {cwd}")
    debug(f"Model path (resolved): {model_path}")

    out_context = Path(args.out_context).resolve()
    out_shacl = Path(args.out_shacl).resolve()
    out_owl = Path(args.out_owl).resolve()

    debug(
        f"out_context: {out_context}  (exists={out_context.exists()}, "
        f"type={'file' if out_context.is_file() else 'missing'})"
    )
    debug(
        f"out_shacl:   {out_shacl}  (exists={out_shacl.exists()}, "
        f"type={'file' if out_shacl.is_file() else 'missing'})"
    )
    debug(
        f"out_owl:     {out_owl}  (exists={out_owl.exists()}, "
        f"type={'file' if out_owl.is_file() else 'missing'})"
    )

    # Ensure /generated/* directory structure exists
    ensure_parent_dir(out_context)
    ensure_parent_dir(out_shacl)
    ensure_parent_dir(out_owl)

    print(f"Using LinkML model: {model_path}")

    # Base dir for loaders and SchemaView – the directory of simpulseid-model.yaml
    base_dir = str(model_path.parent)
    debug(f"Using base_dir for generators: {base_dir}")

    # Change working directory only for internal relative path logic
    old_cwd = Path.cwd()
    os.chdir(model_path.parent)
    try:
        # 1) JSON-LD context
        print(f"Generating JSON-LD context -> {out_context}")
        debug("Initializing ContextGenerator with importmap and base_dir")
        ctx_gen = ContextGenerator(
            str(model_path),
            importmap=import_map,
            base_dir=base_dir,
        )
        context_str = ctx_gen.serialize()
        out_context.write_text(context_str, encoding="utf-8")
        debug("JSON-LD context generation completed successfully.")

        # 2) SHACL shapes
        print(f"Generating SHACL shapes -> {out_shacl}")
        debug("Initializing FixedShaclGenerator with importmap and base_dir")
        shacl_gen = FixedShaclGenerator(
            str(model_path),
            importmap=import_map,
            base_dir=base_dir,
        )
        shacl_str = shacl_gen.serialize()
        out_shacl.write_text(shacl_str, encoding="utf-8")
        debug("SHACL shapes generation completed successfully.")

        # 3) OWL ontology
        print(f"Generating OWL ontology -> {out_owl}")
        debug("Initializing OwlSchemaGenerator with importmap and base_dir")
        owl_gen = OwlSchemaGenerator(
            str(model_path),
            importmap=import_map,
            base_dir=base_dir,
        )
        owl_str = owl_gen.serialize()
        out_owl.write_text(owl_str, encoding="utf-8")
        debug("OWL ontology generation completed successfully.")
    finally:
        os.chdir(old_cwd)

    print("Done. Generated artefacts in /generated/* for comparison with hand-written files.")


if __name__ == "__main__":
    main()
