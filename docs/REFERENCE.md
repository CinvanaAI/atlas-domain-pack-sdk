# Atlas Domain Pack SDK

A small, offline authoring kit for defining and validating domain packs that extend Atlas Kernel without changing kernel code.

Domain packs are plain JSON. They can declare graph types, procedures, reasoning lenses, verification checkpoints, task-packet templates, render templates, and optional seed data. This repository packages the contract and validation layer separately so pack authors do not need a database or the full runtime just to get fast feedback.

## Included

- the complete [domain-pack authoring contract](../DOMAIN_PACK_SPEC.md);
- reusable definition and object validators;
- a cross-file pack validator with human-readable and JSON reports;
- reference checking for checkpoint and procedure names;
- duplicate-type detection and typo suggestions;
- a synthetic, fully valid `research_notes` example;
- tests for the primitive schemas and the complete example pack.

## Quick start

Requires Python 3.11 or newer and uses only the standard library.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e .
atlas-sdk-validate-pack examples\research_notes
atlas-sdk-validate-pack examples\research_notes --json
```

The command exits nonzero when validation fails, making it suitable for a pre-commit hook or CI check.

## Minimal pack

```text
my_pack/
  pack_manifest.json
  node_types.json
  edge_types.json
```

Optional files add procedures, lenses, checkpoints, packet templates, render templates, and seed data. The validator checks each file independently and then performs the cross-file checks it can prove locally.

## What validation means

A passing result means the pack satisfies the published structural contract and its checked references resolve. It does not prove that seed data is true, procedures are wise, or a downstream model will produce good results. Those remain review and evaluation concerns.

## Development

```powershell
python -m pytest -q
python -m pip wheel . --no-deps --no-build-isolation --no-cache-dir -w dist
```

See [ORIGIN.md](../ORIGIN.md) for why this subsystem is published both here and inside Atlas Kernel.
