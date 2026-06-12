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
- `markers`: retrieval markers; omitted markers are read as an empty list for legacy
  stores, but new writes should include explicit markers when possible.

Canonical v1 layer types for new writes:

- `fork`
- `friction`
- `discovery`
- `uncertainty`
- `correction`
- `load-bearing`

Accepted optional fields include `evidence`, `verification`, `supersedes`,
`rollback_of`, `recurrence_of`, `artifact`, `artifact_ref`, `anchor`, `ref`,
`reason`, `scope`, `severity`, `kind`, `inherit`, `action_rule`, `review_after`,
`domain`, `nutrition`, and `force_reason`.

CL2 boundary capsules are intentionally v1-compatible. Until every configured
reader accepts a raw `boundary` layer type, capsules are encoded as
`type = "load-bearing"` with `kind = "boundary"` and marker `boundary`.

Readers are lenient with legacy or extended stores: omitted `markers` are treated
as `[]`, and non-canonical historical types such as `decision`, `thought`, or
`runtime-validation` are readable. New plugin writes still enforce the canonical
v1 type set unless a CL2 helper explicitly remaps the write into a compatible
shape.

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
