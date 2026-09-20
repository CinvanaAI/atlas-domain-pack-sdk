"""Malformed author input must return a failed report, not crash."""
import json
import shutil
from pathlib import Path
import pytest
from atlas_domain_pack_sdk.validate_pack import validate_pack_dir

@pytest.mark.parametrize("filename,payload", [
    ("pack_manifest.json", []),
    ("node_types.json", [None]),
    ("node_types.json", [{"type_name": [], "description": "Wrong name type"}]),
    ("edge_types.json", [42]),
    ("procedures.json", ["not an object"]),
    ("lenses.json", [None]),
    ("checkpoints.json", [None]),
    ("packet_templates.json", [None]),
    ("seed_data.json", {"nodes": [None], "edges": []}),
    ("seed_data.json", {"nodes": [], "edges": [None]}),
])
def test_malformed_entry_produces_failed_report(tmp_path, filename, payload):
    source = Path(__file__).resolve().parents[1] / "examples/research_notes"
    pack = tmp_path / "research_notes"
    shutil.copytree(source, pack)
    (pack / filename).write_text(json.dumps(payload), encoding="utf-8")
    result = validate_pack_dir(pack)
    assert result["passed"] is False
    assert result["files"][filename]["errors"]
