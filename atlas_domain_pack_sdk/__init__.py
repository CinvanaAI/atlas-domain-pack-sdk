"""Authoring and validation tools for Atlas-compatible domain packs."""


def validate_pack_dir(pack_dir):
    """Validate a pack without eagerly importing the command-line module."""
    from .validate_pack import validate_pack_dir as _validate_pack_dir

    return _validate_pack_dir(pack_dir)

__all__ = ["validate_pack_dir"]
