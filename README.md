# Atlas Domain Pack SDK

Author the definitions that tell Atlas which graph objects, work packets and checkpoints a domain needs. Validate those definitions before loading a database. This is the kernel's authoring boundary extracted into a small independent package; both repositories retain a validator so each remains usable on its own. [Origin](ORIGIN.md)

## Edit a pack and see what fails

Python 3.11+, from this checkout:

```sh
python -m pip install -e .
python -m examples.walkthrough
atlas-sdk-validate-pack examples/research_notes
python -m atlas_domain_pack_sdk.validate_pack examples/research_notes --json
python -m pip install pytest
python -m pytest -q
```

The [walkthrough](examples/walkthrough.py) validates [Research Notes](examples/research_notes), then uses disposable copies to demonstrate three rejected edits: an unknown checkpoint, a missing checkpoint file still required by a template, and a non-object definition. [The captured result](examples/result.txt) includes the exact per-file reports.

To try your own domain, copy the example directory, change its manifest identity, and edit the definitions. Run the validator after each edit; exit code 0 means its structural checks passed, 1 means failure.

| File | Author's decision |
| --- | --- |
| [pack_manifest.json](examples/research_notes/pack_manifest.json) | Pack identity and version |
| [node_types.json](examples/research_notes/node_types.json) | Kinds of graph objects |
| [edge_types.json](examples/research_notes/edge_types.json) | Kinds of relationships |
| [procedures.json](examples/research_notes/procedures.json) | Described processing steps |
| [checkpoints.json](examples/research_notes/checkpoints.json) | Named verification conditions |
| [packet_templates.json](examples/research_notes/packet_templates.json) | Work shape and required checkpoint references |
| [seed_data.json](examples/research_notes/seed_data.json) | Synthetic starting graph |

## Consume the report

```python
from pathlib import Path
from atlas_domain_pack_sdk.validate_pack import validate_pack_dir
import tempfile
with tempfile.TemporaryDirectory() as folder:
    report = validate_pack_dir(Path(folder))
    assert report["passed"] is False
    assert report["files"]["pack_manifest.json"]["errors"]
```

[validate_pack.py](atlas_domain_pack_sdk/validate_pack.py) checks file shapes, duplicate type names and supported references; [validators.py](atlas_domain_pack_sdk/validators.py) checks individual definitions. Read both errors and warnings: some unresolved optional references produce warnings rather than failure.

## What a pass means

It is a structural authoring check, not proof of seed-data truth or procedure quality. Runtime condition execution belongs to [Atlas Kernel](https://github.com/CinvanaAI/atlas-kernel). Defining a new condition string does not implement it: the kernel must explicitly support that condition, and unknown conditions fail runtime verification.

The SDK command is `atlas-sdk-validate-pack`; the kernel uses `atlas-validate-pack`, so both can be installed together. Pack contents never cause a database or model call here.

The next useful improvement is a shared versioned validation contract between SDK and kernel, so compatible changes cannot drift between their self-contained copies.

[Authoring contract](DOMAIN_PACK_SPEC.md) · [Reference](docs/REFERENCE.md) · [License](LICENSE.md)
