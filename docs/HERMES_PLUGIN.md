# Hermes Plugin

This repository is laid out as a direct Hermes directory plugin. Hermes installs
Git plugins into its plugin directory and loads a plugin when the installed
directory contains:

```text
plugin.yaml
__init__.py
```

`plugin.yaml` declares the plugin metadata and tool names. `__init__.py`
implements `register(ctx)` and registers the AetherMind tools and companion
skill.

## Install

```bash
hermes plugins install MaverickKB/aethermind-hermes-plugin --enable
hermes plugins list
```

Restart Hermes after enabling. In a running session, `/plugins` should list
`aethermind`.

## Discovery Debugging

```bash
HERMES_PLUGINS_DEBUG=1 hermes plugins list
hermes logs --level WARNING | grep -i plugin
```

The plugin has no external service dependency. Each tool operates on the project
path supplied in the tool arguments.

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
