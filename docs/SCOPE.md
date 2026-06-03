# Scope

AetherMind OSS is the continuity primitive: a compact, append-only project-local
substrate that preserves working judgment for future agents.

It is not generic memory. It is not transcript storage, broad recall, task
logging, or a chat archive. `.aem` layers should be dense signals about what a
future agent must not lose: decisions, corrections, uncertainty, friction,
pressure, rationale, local salience, evidence pointers, supersession, rollback,
and recurrence.

## In scope

- Baseline `.aem` store contract.
- Append-only layer semantics.
- Python library and CLI.
- Store validation, privacy scanning, density warnings, export/import, and
  integrity manifests.
- Optional Hermes reference adapter over the same package core.
- Public docs and examples that explain package behavior.

## Out of scope

- Private production orchestration or deployment claims.
- Benchmark, evidence, proof, or reviewer packets.
- Generic memory product positioning.
- Transcript archives and task ledgers.
- Paid coordinator, licensing, CRM, pricing, or enterprise internals.
- Operator-specific automation, identity surfaces, or private runtime endpoints.

## Product boundary

AetherMind OSS ships the substrate behavior. Integrators own their UI, agent
routing, policy, and deployment identity. Future commercial tiers may build on
the same primitive, but this package stands alone and should work without any
private service.
