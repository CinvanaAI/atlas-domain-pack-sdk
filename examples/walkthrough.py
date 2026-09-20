"""Validate a real pack, then reject three common authoring mistakes."""
import json
import shutil
import tempfile
from pathlib import Path
from atlas_domain_pack_sdk.validate_pack import validate_pack_dir

source = Path(__file__).with_name("research_notes")
good = validate_pack_dir(source)
results = {}
with tempfile.TemporaryDirectory(prefix="pack-example-") as temporary:
    for mistake in ("unknown_checkpoint", "missing_checkpoint_file", "non_object_definition"):
        pack = Path(temporary) / mistake
        shutil.copytree(source, pack)
        if mistake == "unknown_checkpoint":
            path = pack / "packet_templates.json"
            templates = json.loads(path.read_text(encoding="utf-8"))
            templates[0]["required_checkpoints"] = ["missing_checkpoint.v1"]
            path.write_text(json.dumps(templates), encoding="utf-8")
        elif mistake == "missing_checkpoint_file":
            (pack / "checkpoints.json").unlink()
        else:
            (pack / "node_types.json").write_text("[null]", encoding="utf-8")
        results[mistake] = validate_pack_dir(pack)
        assert not results[mistake]["passed"]
assert good["passed"]
print(json.dumps({"valid_pack": good, "rejected_edits": results}, indent=2))
