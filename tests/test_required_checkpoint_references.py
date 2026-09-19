import shutil
from pathlib import Path
import pytest
from atlas_domain_pack_sdk.validate_pack import validate_pack_dir


@pytest.mark.parametrize("checkpoint_file", ["empty", "missing"])
def test_required_checkpoint_must_exist(checkpoint_file, tmp_path):
    source = Path(__file__).resolve().parents[1] / "examples/research_notes"
    target = tmp_path / "research_notes"
    shutil.copytree(source, target)
    checkpoint = target / "checkpoints.json"
    if checkpoint_file == "empty":
        checkpoint.write_text("[]", encoding="utf-8")
    else:
        checkpoint.unlink()
    result = validate_pack_dir(target)
    assert result["passed"] is False
    assert any("unknown checkpoint 'verify_evidence_link.v1'" in error for error in result["errors"])
