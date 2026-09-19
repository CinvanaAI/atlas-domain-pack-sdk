# Atlas Domain Pack SDK

Design an Atlas domain pack and catch broken definitions before running a graph.

Author an Atlas domain pack and catch malformed definitions or cross-file references before loading a database.

## See it work

**Input:** The seven-file Research Notes example and a copy with missing_checkpoint.v 1.

**Result:** The original pack passes; the changed template reports its unknown checkpoint.

[Read the captured output](examples/result.txt) | [Inspect the example](examples/walkthrough.py)

Python 3.11 or newer. From the repository root:

```sh
python -m pip install -e .
python -m examples.walkthrough
```

The example uses synthetic material and runs offline. The captured output comes from executing this example, not a hand-written mockup.

## How it works

A pack is a directory of JSON definitions. The validator checks files, duplicate types, and supported cross-file references without creating a database. The walkthrough validates the supplied Research Notes pack, then changes one checkpoint reference in a temporary copy to show the exact failure.

Implementation: [atlas_domain_pack_sdk/validate_pack.py](atlas_domain_pack_sdk/validate_pack.py), [atlas_domain_pack_sdk/validators.py](atlas_domain_pack_sdk/validators.py), [examples/research_notes](examples/research_notes).

## Limits

Structural validation does not establish the truth of seed data or the quality of a procedure. Runtime checkpoint execution belongs to Atlas Kernel. The SDK command is `atlas-sdk-validate-pack`; Atlas Kernel keeps `atlas-validate-pack`, so both can be installed together. The module form is `python -m atlas_domain_pack_sdk.validate_pack examples/research_notes`.

[Reference and CLI details](docs/REFERENCE.md) | [Origin](ORIGIN.md) | [MIT license](LICENSE.md)

Required checkpoint names must resolve even when `checkpoints.json` is missing or empty. A pack may omit that file only when its templates do not require those checkpoints.
