# Hermes adapter

This directory contains an optional reference adapter that exposes the AetherMind
OSS package through Hermes plugin tools.

The adapter is not the architecture center. It imports `aethermind.core` and
registers Hermes tools over the same library/CLI behavior used by the package.

Smoke test against a local Hermes checkout:

```bash
HERMES_PYTHON=/path/to/hermes/venv/bin/python3 \
HERMES_AGENT_ROOT=/path/to/hermes-agent \
$HERMES_PYTHON tools/evaluate_hermes_plugin.py --hermes-agent-root "$HERMES_AGENT_ROOT"
```

Use the Hermes virtualenv Python when testing local Hermes source so its
dependencies are available.
