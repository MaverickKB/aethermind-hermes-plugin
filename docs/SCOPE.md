# Scope

AetherMind is a compact, append-only continuity substrate for local projects. It
preserves the small pieces of working judgment that a future agent session needs
before touching the same project again.

## In Scope

- Creating `.aethermind/layers.aem` and `.aethermind/texture.aem`.
- Appending structured continuity layers.
- Reading and searching project-local layers.
- Writing and reading short texture entries.
- Building a task-relevant reorientation bundle.
- Evaluating store schema, density, privacy, and retrieval signals.
- Exporting, importing, and hashing `.aem` stores.
- Registering those behaviors as Hermes tools.
- Automatically initializing and reading the project-local store through Hermes
  lifecycle hooks.
- Injecting compact continuity guidance before model calls so AetherMind use is
  part of the normal session flow.

## Out Of Scope

- Transcript storage.
- Generic long-term memory.
- Task ledgers or status logs.
- Customer-data storage.
- Deployment orchestration.
- Benchmark or review packets.

Integrators own their UI, routing, policy, and deployment identity. The plugin
provides local continuity tools and Hermes lifecycle enforcement for those
tools.
