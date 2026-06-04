# Hermes Plugin

This repository is laid out as a direct Hermes directory plugin. Hermes installs
Git plugins into its plugin directory and loads a plugin when the installed
directory contains:

```text
plugin.yaml
__init__.py
```

`plugin.yaml` declares the plugin metadata and tool names. `__init__.py`
implements `register(ctx)` and registers the AetherMind tools, lifecycle hooks,
and companion skill.

## Install

```bash
hermes plugins install MaverickKB/aethermind-hermes-plugin --enable
hermes plugins list
```

Restart Hermes after enabling. In a running session, `/plugins` should list
`aethermind`.

## Automatic Continuity Hooks

The plugin registers two Hermes lifecycle hooks:

- `on_session_start` initializes `.aethermind/layers.aem` and
  `.aethermind/texture.aem` for the current project root.
- `pre_llm_call` reads task-relevant layers and injects a compact AetherMind
  continuity block into the current user turn.

By default, the project root is the Hermes process working directory. Set
`AETHERMIND_PROJECT_ROOT` to force a specific root.

The injected context tells the agent to use `aethermind_write_layer` when work
produces a durable decision, correction, discovery, friction, or uncertainty.
The plugin does not write synthetic task-summary layers automatically.

The companion skill is plugin-qualified as
`aethermind:aethermind-continuity`. It is available through `skill_view`, not as
a copied `~/.hermes/skills` entry.

## Discovery Debugging

```bash
HERMES_PLUGINS_DEBUG=1 hermes plugins list
hermes logs --level WARNING | grep -i plugin
```

The plugin has no external service dependency. Each tool operates on the project
path supplied in the tool arguments.

For hook behavior, run Hermes from a clean project directory and check that
`.aethermind/layers.aem` and `.aethermind/texture.aem` are created after a fresh
session starts.

## Registered Tools

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
