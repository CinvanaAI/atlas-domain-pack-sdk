"""
Standalone domain pack validation command.
Validates a domain pack on disk without loading it into the database.
Produces a plain-language report with pass/fail per file.

Usage:
    python -m atlas_domain_pack_sdk.validate_pack examples/research_notes
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from .errors import (
    DomainPackLoadError,
    RegistryValidationError,
    DuplicateDefinitionError,
)
from .validators import (
    validate_manifest,
    validate_node_type_definition,
    validate_edge_type_definition,
    validate_procedure_definition,
    validate_lens_definition,
    validate_checkpoint_definition,
    validate_packet_template,
)


def validate_pack_dir(pack_dir: Path) -> dict:
    """
    Validate a domain pack directory.
    Returns a result dict:
    {
        "pack_name": str,
        "passed": bool,
        "files": {
            "pack_manifest.json": {"valid": int, "errors": [str]},
            ...
        },
        "warnings": [str],
        "errors": [str],
    }
    """
    results = {
        "pack_name": pack_dir.name,
        "passed": True,
        "files": {},
        "warnings": [],
        "errors": [],
    }

    def file_result(filename: str) -> dict:
        if filename not in results["files"]:
            results["files"][filename] = {"valid": 0, "errors": []}
        return results["files"][filename]

    def add_error(filename: str, msg: str):
        file_result(filename)["errors"].append(msg)
        results["errors"].append(f"{filename}: {msg}")
        results["passed"] = False

    def load_json_file(path: Path, filename: str):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            add_error(filename, f"File not found")
            return None
        except json.JSONDecodeError as e:
            add_error(filename, f"Invalid JSON: {e}")
            return None

    # --- pack_manifest.json (required) ---
    manifest_path = pack_dir / "pack_manifest.json"
    manifest = load_json_file(manifest_path, "pack_manifest.json")
    pack_name = pack_dir.name
    if manifest is not None:
        try:
            validate_manifest(manifest, pack_name, "pack_manifest.json")
            pack_name = manifest.get("pack_name", pack_dir.name)
            results["pack_name"] = pack_name
            file_result("pack_manifest.json")["valid"] = 1
        except (RegistryValidationError, DomainPackLoadError) as e:
            add_error("pack_manifest.json", str(e))

    # --- node_types.json (required) ---
    node_types_path = pack_dir / "node_types.json"
    node_types_data = load_json_file(node_types_path, "node_types.json")
    seen_node_types = set()
    if node_types_data is not None:
        if not isinstance(node_types_data, list):
            add_error("node_types.json", "Must be a JSON array")
        else:
            valid_count = 0
            for defn in node_types_data:
                name = defn.get("type_name", "<unnamed>")
                if name in seen_node_types:
                    add_error("node_types.json", f"Duplicate type_name: '{name}'")
                    continue
                seen_node_types.add(name)
                try:
                    validate_node_type_definition(defn, pack_name, "node_types.json")
                    valid_count += 1
                except RegistryValidationError as e:
                    add_error("node_types.json", str(e))
            file_result("node_types.json")["valid"] = valid_count

    # --- edge_types.json (required) ---
    edge_types_path = pack_dir / "edge_types.json"
    edge_types_data = load_json_file(edge_types_path, "edge_types.json")
    seen_edge_types = set()
    if edge_types_data is not None:
        if not isinstance(edge_types_data, list):
            add_error("edge_types.json", "Must be a JSON array")
        else:
            valid_count = 0
            for defn in edge_types_data:
                name = defn.get("type_name", "<unnamed>")
                if name in seen_edge_types:
                    add_error("edge_types.json", f"Duplicate type_name: '{name}'")
                    continue
                seen_edge_types.add(name)
                try:
                    validate_edge_type_definition(defn, pack_name, "edge_types.json")
                    valid_count += 1
                except RegistryValidationError as e:
                    add_error("edge_types.json", str(e))
            file_result("edge_types.json")["valid"] = valid_count

    # --- procedures.json (optional) ---
    procs_path = pack_dir / "procedures.json"
    if procs_path.exists():
        procs_data = load_json_file(procs_path, "procedures.json")
        if procs_data is not None:
            if not isinstance(procs_data, list):
                add_error("procedures.json", "Must be a JSON array")
            else:
                valid_count = 0
                for defn in procs_data:
                    try:
                        validate_procedure_definition(defn, pack_name, "procedures.json")
                        valid_count += 1
                    except RegistryValidationError as e:
                        add_error("procedures.json", str(e))
                file_result("procedures.json")["valid"] = valid_count

    # --- lenses.json (optional) ---
    lenses_path = pack_dir / "lenses.json"
    if lenses_path.exists():
        lenses_data = load_json_file(lenses_path, "lenses.json")
        if lenses_data is not None:
            if not isinstance(lenses_data, list):
                add_error("lenses.json", "Must be a JSON array")
            else:
                valid_count = 0
                for defn in lenses_data:
                    try:
                        validate_lens_definition(defn, pack_name, "lenses.json")
                        # Cross-check: verify procedure refs exist in this pack
                        for proc_ref in defn.get("compatible_procedure_ids", []):
                            if procs_path.exists():
                                procs_names = {d.get("name") for d in (procs_data or [])}
                                if proc_ref not in procs_names:
                                    results["warnings"].append(
                                        f"lenses.json > {defn.get('name')}: "
                                        f"references unknown procedure '{proc_ref}' — "
                                        f"did you mean one of {sorted(procs_names)}?"
                                    )
                        valid_count += 1
                    except RegistryValidationError as e:
                        add_error("lenses.json", str(e))
                file_result("lenses.json")["valid"] = valid_count

    # --- checkpoints.json (optional) ---
    cps_path = pack_dir / "checkpoints.json"
    if cps_path.exists():
        cps_data = load_json_file(cps_path, "checkpoints.json")
        if cps_data is not None:
            if not isinstance(cps_data, list):
                add_error("checkpoints.json", "Must be a JSON array")
            else:
                valid_count = 0
                for defn in cps_data:
                    try:
                        validate_checkpoint_definition(defn, pack_name, "checkpoints.json")
                        valid_count += 1
                    except RegistryValidationError as e:
                        add_error("checkpoints.json", str(e))
                file_result("checkpoints.json")["valid"] = valid_count

    # --- packet_templates.json (optional) ---
    templates_path = pack_dir / "packet_templates.json"
    if templates_path.exists():
        templates_data = load_json_file(templates_path, "packet_templates.json")
        if templates_data is not None:
            if not isinstance(templates_data, list):
                add_error("packet_templates.json", "Must be a JSON array")
            else:
                valid_count = 0
                cp_names = {d.get("name") for d in (cps_data if cps_path.exists() and isinstance(cps_data, list) else []) if isinstance(d, dict)}
                for defn in templates_data:
                    try:
                        validate_packet_template(defn, pack_name, "packet_templates.json")
                        # Cross-check checkpoint refs
                        for cp_ref in defn.get("required_checkpoints", []):
                            if cp_ref not in cp_names:
                                import difflib
                                close = difflib.get_close_matches(cp_ref, cp_names, n=1, cutoff=0.6)
                                hint = f" Did you mean: {close[0]}?" if close else ""
                                add_error(
                                    "packet_templates.json",
                                    f"{defn.get('template_name')}: references unknown checkpoint '{cp_ref}'.{hint}",
                                )
                        valid_count += 1
                    except RegistryValidationError as e:
                        add_error("packet_templates.json", str(e))
                file_result("packet_templates.json")["valid"] = valid_count

    # --- seed_data.json (optional) ---
    seed_path = pack_dir / "seed_data.json"
    if seed_path.exists():
        seed_data = load_json_file(seed_path, "seed_data.json")
        if seed_data is not None:
            seed_nodes = seed_data.get("nodes", [])
            seed_edges = seed_data.get("edges", [])
            valid_count = 0
            for node in seed_nodes:
                if not node.get("name"):
                    add_error("seed_data.json", f"Seed node missing 'name' field: {node}")
                elif not node.get("type"):
                    add_error("seed_data.json", f"Seed node '{node['name']}' missing 'type' field")
                elif node["type"] not in seen_node_types:
                    results["warnings"].append(
                        f"seed_data.json: node '{node['name']}' has type '{node['type']}' "
                        f"not defined in node_types.json"
                    )
                    valid_count += 1
                else:
                    valid_count += 1
            for edge in seed_edges:
                if not edge.get("source") or not edge.get("target") or not edge.get("type"):
                    add_error("seed_data.json", f"Seed edge missing source/target/type: {edge}")
                elif edge["type"] not in seen_edge_types:
                    results["warnings"].append(
                        f"seed_data.json: edge type '{edge['type']}' not defined in edge_types.json"
                    )
            file_result("seed_data.json")["valid"] = valid_count

    return results


def print_validation_report(results: dict) -> None:
    """Print a human-readable validation report."""
    pack_name = results["pack_name"]
    passed = results["passed"]

    print(f"Pack: {pack_name}")
    print(f"Status: {'PASS' if passed else 'FAIL'}")
    print()

    for filename, file_res in sorted(results["files"].items()):
        errors = file_res["errors"]
        valid = file_res["valid"]
        if errors:
            print(f"{filename}: {valid} valid, {len(errors)} error(s)")
            for e in errors:
                print(f"  [ERROR] {e}")
        else:
            print(f"{filename}: {valid} valid")

    if results["warnings"]:
        print(f"\nWarnings: {len(results['warnings'])}")
        for w in results["warnings"]:
            print(f"  [WARN] {w}")
    else:
        print(f"\nWarnings: 0")

    if not passed:
        print(f"\nErrors: {len(results['errors'])}")
        for e in results["errors"]:
            print(f"  [ERROR] {e}")


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Validate an Atlas Kernel domain pack without loading it."
    )
    parser.add_argument("pack_dir", help="Path to the domain pack directory")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    args = parser.parse_args()

    pack_dir = Path(args.pack_dir)
    if not pack_dir.is_dir():
        print(f"ERROR: '{pack_dir}' is not a directory", file=sys.stderr)
        sys.exit(1)

    results = validate_pack_dir(pack_dir)

    if args.json:
        import json
        print(json.dumps(results, indent=2))
    else:
        print_validation_report(results)

    sys.exit(0 if results["passed"] else 1)


if __name__ == "__main__":
    main()
