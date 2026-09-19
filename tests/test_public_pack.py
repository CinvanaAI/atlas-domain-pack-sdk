from pathlib import Path

from atlas_domain_pack_sdk import validate_pack_dir


def test_public_example_pack_passes() -> None:
    pack = Path(__file__).parent.parent / "examples" / "research_notes"
    result = validate_pack_dir(pack)

    assert result["passed"] is True
    assert result["pack_name"] == "research_notes"
    assert result["warnings"] == []
    assert result["errors"] == []
    assert result["files"]["packet_templates.json"]["valid"] == 1


def test_unknown_checkpoint_reference_fails(tmp_path: Path) -> None:
    source = Path(__file__).parent.parent / "examples" / "research_notes"
    pack = tmp_path / "research_notes"
    import shutil

    shutil.copytree(source, pack)
    template_path = pack / "packet_templates.json"
    text = template_path.read_text(encoding="utf-8")
    template_path.write_text(text.replace("verify_evidence_link.v1", "missing_checkpoint.v1"), encoding="utf-8")

    result = validate_pack_dir(pack)
    assert result["passed"] is False
    assert any("unknown checkpoint" in error for error in result["errors"])
