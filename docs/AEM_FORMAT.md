# `.aem` baseline format

The current package uses a TOML-style baseline representation under:

```text
.aethermind/layers.aem
.aethermind/texture.aem
```

This representation is intentionally easy to inspect, but human readability is
not the AetherMind invariant. The invariant is dense, append-only,
machine-readable continuity that is cheap for agents to scan and reorient from.
Future encodings may be denser, embedded, binary, sidecar-based, or encrypted
where appropriate.

## Layer table

Each layer is a `[[layer]]` table.

Required fields:

- `id` — unique layer identifier
- `ts` — UTC timestamp
- `author` — writer identity
- `type` — one of the canonical layer types
- `body` — compact continuity signal
- `ctx` — context/routing path
- `conf` — confidence from `0.0` to `1.0`
- `markers` — array of retrieval markers

Canonical layer types:

- `fork`
- `friction`
- `discovery`
- `uncertainty`
- `correction`
- `load-bearing`

Accepted optional fields include:

- `evidence`
- `verification`
- `supersedes`
- `rollback_of`
- `recurrence_of`
- `artifact`
- `artifact_ref`
- `anchor`
- `ref`
- `reason`
- `scope`
- `severity`

## Density guidance

A layer is not a note. Prefer compact signals such as:

```toml
[[layer]]
id = "001"
ts = "2026-06-03T00:00:00Z"
author = "agent"
type = "correction"
body = "!AetherMind is continuity substrate, not generic memory."
ctx = "docs/scope"
conf = 1.0
markers = ["scope", "continuity", "correction"]
```

Long prose belongs in docs, project notes, or other higher-cost records unless
the prose itself is load-bearing.

## Texture

`texture.aem` is a lightweight attention/feel pointer. It should stay short. It
is not a report log.
