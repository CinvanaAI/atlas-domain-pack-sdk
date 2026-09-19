# Domain Pack Authoring Contract

This document is the bridge between the Atlas Kernel and anyone who creates a new domain pack. Read it before writing a pack.

---

## What a domain pack is

A domain pack is a directory of JSON definition files that extend the Atlas Kernel with new types, procedures, lenses, checkpoints, packet templates, and seed data. The kernel loads packs and registers everything they define. Adding a new domain pack **never requires modifying any file inside `atlas_kernel/`**.

---

## Directory structure

```
domain_packs/
  your_pack_name/
    pack_manifest.json       ← required
    node_types.json          ← required
    edge_types.json          ← required
    procedures.json          ← optional
    lenses.json              ← optional
    checkpoints.json         ← optional
    packet_templates.json    ← optional
    render_templates.json    ← optional
    seed_data.json           ← optional
```

---

## Required fields per file

### `pack_manifest.json`
```json
{
  "pack_name": "your_pack_name",
  "version": "1.0",
  "description": "One sentence describing this domain.",
  "depends_on": []
}
```
Required: `pack_name`, `version`, `description`.

---

### `node_types.json` — array of node type definitions
```json
[
  {
    "type_name": "example_node",
    "description": "What this node type represents.",
    "required_fields": ["name"],
    "allowed_parent_types": ["memory_domain"],
    "version": "1.0"
  }
]
```
Required per entry: `type_name`, `description`.
Optional: `required_fields` (list), `allowed_parent_types` (list), `version`.

---

### `edge_types.json` — array of edge type definitions
```json
[
  {
    "type_name": "example_edge",
    "description": "What this edge type represents.",
    "allowed_source_types": ["example_node"],
    "allowed_target_types": ["example_node"],
    "version": "1.0"
  }
]
```
Required per entry: `type_name`, `description`.
Optional: `allowed_source_types`, `allowed_target_types`, `version`.

---

### `procedures.json` — array of procedure definitions
```json
[
  {
    "name": "Domain.Category.Action.v1",
    "version": "1.0",
    "procedure_type": "inference",
    "description": "What this procedure does.",
    "input_requirements": ["source_fragment", "target_node_id"],
    "output_schema": "ExampleNode + derived_from_edge",
    "steps": [
      "1. First step.",
      "2. Second step.",
      "3. Propose node.",
      "4. Link evidence."
    ]
  }
]
```
Required per entry: `name`, `version`, `procedure_type`, `description`, `output_schema`, `steps`.

---

### `lenses.json` — array of lens definitions
```json
[
  {
    "name": "example_lens.v1",
    "version": "1.0",
    "description": "What this lens does and when it activates.",
    "activation_conditions": [
      "confidence_below_0.7",
      "source_contains_risk_indicator"
    ],
    "amplifies": ["uncertainty"],
    "suppresses": ["confident_positive_framing"],
    "compatible_procedure_ids": ["Domain.Category.Action.v1"]
  }
]
```
Required per entry: `name`, `version`, `description`, `activation_conditions`.

---

### `checkpoints.json` — array of verification checkpoint definitions
```json
[
  {
    "name": "verify_something.v1",
    "version": "1.0",
    "checkpoint_type": "evidence_link",
    "description": "What this checkpoint verifies.",
    "required_inputs": ["proposed_nodes", "proposed_edges"],
    "pass_conditions": ["has_derived_from_edge"],
    "failure_conditions": ["no_derived_from_edge_present"]
  }
]
```
Required per entry: `name`, `version`, `checkpoint_type`, `description`, `pass_conditions`, `failure_conditions`.

**Supported pass condition strings (built-in to CommitEngine):**
- `has_derived_from_edge` — candidate must have at least one proposed edge of type `derived_from`
- `confidence_above_threshold` — candidate confidence must meet the packet's threshold
- `proposed_nodes_not_empty` — candidate must have at least one proposed node

---

### `packet_templates.json` — array of packet template definitions
```json
[
  {
    "template_name": "example_claim",
    "detected_type": "example_claim",
    "description": "Used when a source fragment contains an example claim.",
    "risk_tier": "high",
    "requires_high_reasoning": true,
    "free_first_worker_allowed": false,
    "can_be_preprocessed_locally": false,
    "requires_human_review": false,
    "applicable_procedures": ["Domain.Category.Action.v1"],
    "applicable_lenses": [],
    "applicable_lenses_conditional": [
      {
        "lens": "example_lens.v1",
        "when": { "confidence_below": 0.7 }
      }
    ],
    "required_checkpoints": ["verify_something.v1"],
    "required_output_schema": "ExampleNode",
    "confidence_threshold_for_auto_commit": 0.85
  }
]
```
Required per entry: `template_name`, `detected_type`, `risk_tier`.

Valid `risk_tier` values: `low`, `medium`, `high`, `critical`.
Valid `cost_tier` values (for workers): `free`, `low`, `medium`, `high`.

---

### `seed_data.json` — initial atlas nodes and edges
```json
{
  "nodes": [
    {
      "name": "My Domain",
      "type": "memory_domain",
      "parent_path": "",
      "summary": "The root domain for this pack.",
      "confidence": 1.0
    }
  ],
  "edges": [
    {
      "source": "My Domain",
      "target": "Some Node",
      "type": "contains",
      "label": "contains",
      "summary": "My Domain contains Some Node."
    }
  ]
}
```
Seed insertion is **idempotent** — nodes are matched by name; existing nodes are skipped.
Edges are matched by source+target+type; duplicates are skipped.

---

## How validation errors are reported

Run validation without loading:
```
python -m atlas_kernel.validate_pack domain_packs/your_pack_name
```

On pass:
```
Pack: your_pack_name
Status: PASS

node_types.json: 5 valid
edge_types.json: 3 valid
procedures.json: 1 valid
lenses.json: 1 valid
checkpoints.json: 2 valid
packet_templates.json: 1 valid
seed_data.json: 8 valid

Warnings: 0
```

On failure:
```
Pack: your_pack_name
Status: FAIL

node_types.json: 3 valid, 1 error(s)
  ✗ node_type missing required field 'description' (object: suspicion, field: description)

packet_templates.json: 0 valid, 1 error(s)
  ✗ example_claim: references unknown checkpoint 'verify_something.v2' Did you mean: verify_something.v1?

Warnings: 1
  ⚠  lenses.json > example_lens.v1: references unknown procedure 'Domain.Category.Action.v2' — did you mean one of ['Domain.Category.Action.v1']?

Errors: 2
```

---

## How to add a new pack without touching the kernel

1. Create `domain_packs/your_pack_name/` with the required files.
2. Run validation: `python -m atlas_kernel.validate_pack domain_packs/your_pack_name`
3. Fix any errors.
4. Load the pack in your script:
   ```python
   loader = DomainPackLoader()
   loader.load_pack(Path("domain_packs/your_pack_name"), registry, repo)
   ```
5. Done. No kernel code changes.

---

## Key rules

- `type_name` and `name` must be unique within their category across all loaded packs.
- All `required_checkpoints` in packet templates must reference names defined in `checkpoints.json`.
- All `compatible_procedure_ids` in lenses must reference names defined in `procedures.json`.
- Pack names must be unique — you cannot load the same pack twice.
- Seed loading is idempotent — safe to re-run.
- Domain pack load is atomic — if any file fails validation, nothing is written to the database.
