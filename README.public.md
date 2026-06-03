# AetherMind

AetherMind is a project-local continuity primitive for AI agents. It stores dense,
append-only `.aem` layers near the project so future agents can recover the
load-bearing parts of prior work: decisions, corrections, uncertainty, pressure,
rationale, and local salience.

AetherMind is not a generic memory database, transcript archive, task ledger, or
chat log. The current public baseline uses TOML-style records because they are
portable and easy to inspect, but human readability is not the invariant. The
invariant is compact machine-readable continuity that is cheap for agents to scan
and reorient from.

## Install

From a checkout:

```bash
python3 -m pip install -e .
```

## Quick start

```bash
aethermind init --project-root /path/to/project

aethermind write-layer \
  --project-root /path/to/project \
  --type load-bearing \
  --body "mission: keep continuity compact" \
  --ctx "planning/mission" \
  --marker mission

aethermind write-layer \
  --project-root /path/to/project \
  --type friction \
  --body "pressure: do not turn layers into task logs" \
  --ctx "planning/pressure" \
  --marker pressure

aethermind reorient --project-root /path/to/project --task "resume planning"
aethermind validate-store --project-root /path/to/project
aethermind export --project-root /path/to/project --out /tmp/aethermind-export.json
aethermind import --project-root /tmp/imported-project --in /tmp/aethermind-export.json
```

All CLI commands emit JSON.

## Product boundary

Included in this OSS package:

- `.aem` baseline continuity store contract
- Python library and CLI
- store validation, privacy checks, density warnings, and integrity manifests
- export/import helpers
- optional Hermes reference adapter
- public docs and examples

Not included:

- private production orchestration
- benchmark/evidence/proof packets
- generic memory, broad recall, transcript storage, or task logging
- paid-tier coordinator, licensing, CRM, or deployment internals
- any operator-specific home/lab automation or identity surface

## Documentation

- `docs/SCOPE.md` — product scope and non-memory boundary
- `docs/AEM_FORMAT.md` — baseline `.aem` record format
- `docs/CLI.md` — command examples
- `docs/HERMES_PLUGIN.md` — optional Hermes adapter
- `docs/PRIVACY.md` — what not to write into layers
- `docs/ROADMAP.md` — OSS primitive and future boundaries

## License

Apache-2.0. See `LICENSE`.
