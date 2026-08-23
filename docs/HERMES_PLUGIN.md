# Hermes Plugin

This repository is a direct Hermes directory plugin. Hermes loads the plugin
from `plugin.yaml` and `__init__.py`.

`aethermind_core.py` contains the same project-local continuity engine shipped
by the public primitive. `aem_store.py` adapts that engine to the Hermes tool
contract. The plugin remains self-contained and has no external service
dependency.

## Install

```bash
hermes plugins install MaverickKB/aethermind-hermes-plugin --enable
hermes plugins list
```

Restart Hermes after enabling. In a running session, `/plugins` should list
`aethermind`.

## Project root

The working directory is the default project root. Set
`AETHERMIND_PROJECT_ROOT` to select another root for lifecycle hooks. Every
explicit tool call also requires `project_root`.

The store always belongs beside the project filesystem being described.

## Lifecycle hooks

- `on_session_start` explicitly initializes the project-local AEM store.
- `pre_llm_call` retrieves task-relevant layers and adds a compact continuity
  block to the current turn.

The hook tells the agent which project root to use. It does not create synthetic
task-summary layers.

## Tool groups

Write and read:

- `aethermind_init_store`
- `aethermind_write_layer`
- `aethermind_read_layers`
- `aethermind_write_texture`
- `aethermind_read_texture`
- `aethermind_write_event`
- `aethermind_read_events`
- `aethermind_archive`

Orientation:

- `aethermind_reorient`
- `aethermind_currentness`
- `aethermind_brief`
- `aethermind_brief_anchor`
- `aethermind_gate_check`

Inspection and transfer:

- `aethermind_capabilities`
- `aethermind_audit`
- `aethermind_evaluate_store`
- `aethermind_integrity_manifest`
- `aethermind_export_store`
- `aethermind_import_layers`

## Discovery checks

```bash
HERMES_PLUGINS_DEBUG=1 hermes plugins list
hermes logs --level WARNING | grep -i plugin
```

For hook behavior, start Hermes from a clean project directory and confirm that
`.aethermind/layers.aem` and `.aethermind/texture.aem` appear after a fresh
session starts.

## Upgrade behavior

The 0.2 plugin reads the existing 0.1 AEM records directly. It does not rename or
rewrite the store during installation. See [UPGRADING.md](UPGRADING.md) for the
preservation and rollback path.
