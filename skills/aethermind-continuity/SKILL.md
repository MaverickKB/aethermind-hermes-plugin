---
name: aethermind-continuity
description: Use when a Hermes session needs to create, read, validate, or reorient from project-local AetherMind continuity layers.
---

# AetherMind Continuity

AetherMind stores compact, append-only `.aem` records beside a project. Use it
for load-bearing continuity: decisions, corrections, uncertainty, pressure,
rationale, and evidence pointers that future agents need before touching the
same project.

## Before Writing

1. Identify the real project root.
2. Prefer compact continuity signals over transcripts, logs, or task summaries.
3. Do not write secrets, credentials, private paths, raw prompts, transcripts,
   or high-volume logs into `.aem` layers.

## Common Tools

- `aethermind_init_store` creates `.aethermind/layers.aem` and
  `.aethermind/texture.aem`.
- `aethermind_write_layer` appends a structured continuity layer.
- `aethermind_read_layers` searches stored layers. A root that starts with `jarvis:` is the remote store. Any other root is a local file. A missing local file is an error, not an empty result.
- `aethermind_reorient` builds a task-relevant continuity bundle.
- `aethermind_currentness` separates active heads from inactive lineage.
- `aethermind_brief` and `aethermind_brief_anchor` return compact current state.
- `aethermind_write_event` keeps routine observations in `events.aem`.
- `aethermind_archive` copies selected records to `archive.aem` and appends
  their tombstone to `layers.aem`.
- `aethermind_evaluate_store` validates schema, privacy, density, and continuity
  properties.

## CL2 Upgrade Tools

Use these when the store is large/noisy, a write may be low-quality, or a session
is ending and needs explicit boundary capture:

- `aethermind_cl2_brief` builds a budgeted Re-Inheritance Value brief: records
  are selected because they should change the next action, not merely because
  they are recent or topically similar.
- `aethermind_cl2_store_health` reports density/nutrition, stale candidates,
  superseded counts, and SHA-256.
- `aethermind_cl2_nutrition` lints a would-be layer without appending it.
- `aethermind_cl2_write_layer` appends with CL2 optional fields and lint/coach/
  strict modes.
- `aethermind_cl2_capsule` writes POSTURE / OPEN / NEXT / INVALID boundary
  capture.

Boundary capsules remain v1-reader compatible: they are written as
`type = "load-bearing"`, `kind = "boundary"`, marker `boundary` until all
configured readers support a raw CL2 `boundary` type.

## Layer Guidance

Use layer types intentionally:

- `load-bearing` for decisions or constraints that future agents must preserve.
- `correction` for mistakes, changed assumptions, or repeated failure modes.
- `friction` for pressure that shaped the work.
- `uncertainty` for unresolved facts that change the next step.
- `discovery` for evidence-backed findings.
- `fork` for alternate paths or abandoned branches.

Keep each layer short enough to scan quickly.

Use `primitive = "artifact-reference"`, `anchor`, `pressure-event`,
`supersession`, or `rollback` only when the corresponding relationship is part
of the continuity being recorded. Otherwise use the base `layer` primitive.
