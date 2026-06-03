# Hermes adapter

This directory contains an optional reference adapter that exposes the
AetherMind package through Hermes plugin tools.

The adapter is not the architecture center. It imports `aethermind.core` and
registers Hermes tools over the same library/CLI behavior used by the package.

## Recommended user install

Use the packaged entry-point plugin instead of copying this directory:

```bash
HERMES_AGENT_ROOT="${HERMES_AGENT_ROOT:-$HOME/.hermes/hermes-agent}"
uv pip install --python "$HERMES_AGENT_ROOT/venv/bin/python" /path/to/aethermind
hermes plugins enable aethermind
hermes plugins list
```

The entry point is declared as:

```toml
[project.entry-points."hermes_agent.plugins"]
aethermind = "aethermind.hermes_plugin"
```

This directory remains for source-tree and compatibility testing.

## Smoke test

Smoke test against a local Hermes checkout:

```bash
HERMES_PYTHON=/path/to/hermes/venv/bin/python3 \
HERMES_AGENT_ROOT=/path/to/hermes-agent \
$HERMES_PYTHON tools/evaluate_hermes_plugin.py --hermes-agent-root "$HERMES_AGENT_ROOT"
```

Use the Hermes virtualenv Python when testing local Hermes source so its
dependencies are available.
