# `.aem` Format

An AetherMind store lives under a project root:

```text
.aethermind/layers.aem
.aethermind/texture.aem
```

The baseline format uses TOML-style `[[layer]]` records. Human readability is
useful, but the invariant is compact, append-only, machine-readable continuity.

## Layer Records

Each layer is a `[[layer]]` table.

Required fields:

- `id`: unique layer identifier
- `ts`: UTC timestamp
- `author`: writer identity
- `type`: canonical layer type
- `body`: compact continuity signal
- `ctx`: routing context
- `conf`: confidence from `0.0` to `1.0`
- `markers`: retrieval markers

Canonical layer types:

- `fork`
- `friction`
- `discovery`
- `uncertainty`
- `correction`
- `load-bearing`

Accepted optional fields include `evidence`, `verification`, `supersedes`,
`rollback_of`, `recurrence_of`, `artifact`, `artifact_ref`, `anchor`, `ref`,
`reason`, `scope`, and `severity`.

## Example

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

## Texture

`texture.aem` stores short attention pointers. It should stay brief. It is not a
report log.
