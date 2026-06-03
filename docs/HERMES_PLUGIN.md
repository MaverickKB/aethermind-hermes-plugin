# Hermes plugin

The Hermes adapter is optional. It is a thin reference adapter over the
`aethermind` package, not the architecture center.

Plugin directory:

```text
plugins/hermes/aethermind/
```

Supported smoke command against a local Hermes checkout:

```bash
HERMES_PYTHON=/path/to/hermes/venv/bin/python3 \
HERMES_AGENT_ROOT=/path/to/hermes-agent \
$HERMES_PYTHON tools/evaluate_hermes_plugin.py --hermes-agent-root "$HERMES_AGENT_ROOT"
```

Use the Hermes virtualenv Python when testing a local Hermes checkout so Hermes'
Python dependencies are available.

Registered tools:

- `aethermind_init_store`
- `aethermind_write_layer`
- `aethermind_read_layers`
- `aethermind_write_texture`
- `aethermind_read_texture`
- `aethermind_reorient`
- `aethermind_evaluate_store`
- `aethermind_export_store`
- `aethermind_import_layers`
- `aethermind_integrity_manifest`
