# Origin and relationship to Atlas Kernel

This repository extracts the domain-pack authoring boundary from Atlas Kernel as a focused SDK. The same validator remains in the full kernel so that repository is self-contained; this smaller repository exists for pack authors, schema review, and CI use without a database runtime.

The original domain pack described private people and memory data. It is not included. The `research_notes` pack is synthetic and was created specifically for the public snapshots.

Included source consists of the authored contract, validation rules, error types, command-line report, example, and tests. No private seed data, atlas database, runtime state, or model integration is present.
