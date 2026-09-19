"""Validate the complete pack, then prove a broken reference is rejected."""
import json
import shutil
import tempfile
from pathlib import Path
from atlas_domain_pack_sdk.validate_pack import validate_pack_dir

source = Path(__file__).with_name("research_notes")
good = validate_pack_dir(source)
with tempfile.TemporaryDirectory(prefix="pack-example-") as temporary:
    broken = Path(temporary) / "research_notes"
    shutil.copytree(source, broken)
    path = broken / "packet_templates.json"
    templates = json.loads(path.read_text())
    templates[0]["required_checkpoints"] = ["missing_checkpoint.v1"]
    path.write_text(json.dumps(templates), encoding="utf-8")
    bad = validate_pack_dir(broken)
assert good["passed"] and not bad["passed"]
print(json.dumps({"valid_pack": good, "broken_pack": bad}, indent=2))
