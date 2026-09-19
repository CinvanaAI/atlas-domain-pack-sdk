# Security and data handling

Domain-pack definitions can contain seed data. Review that data before committing a pack and keep personal, customer, credential, and private-environment material outside public repositories.

The validator reads only the named pack directory, performs no network calls, and does not execute code from the JSON files. It validates structure and checked references; it is not a content-safety scanner.

When reporting a defect, use the synthetic example or another minimal reproduction rather than attaching a private pack.
