from pathlib import Path
import tomllib


def test_sdk_console_command_does_not_claim_kernel_name():
    metadata = tomllib.loads((Path(__file__).resolve().parents[1] / "pyproject.toml").read_text(encoding="utf-8"))
    assert metadata["project"]["scripts"] == {"atlas-sdk-validate-pack": "atlas_domain_pack_sdk.validate_pack:main"}
