# Hermes plugin

The Hermes adapter is optional. It is a thin reference adapter over the
`aethermind` package, not the architecture center.

## Recommended install

Install Hermes first:

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
source ~/.bashrc  # or: source ~/.zshrc
```

Install AetherMind into the Hermes Python environment so Hermes can discover the
packaged entry-point plugin. Hermes installs commonly use `uv` and may not have
`pip` inside the virtualenv:

```bash
HERMES_AGENT_ROOT="${HERMES_AGENT_ROOT:-$HOME/.hermes/hermes-agent}"
uv pip install --python "$HERMES_AGENT_ROOT/venv/bin/python" .
```

For a release artifact, replace `.` with the wheel or source distribution path.

Enable the plugin:

```bash
hermes plugins enable aethermind
hermes plugins list
```

Start a new Hermes session after enabling. In a running session, `/plugins`
should show `aethermind` and the tools listed below.

## Source-tree adapter

The source tree also includes a directory plugin for local Hermes checkout smoke
tests:

```text
plugins/hermes/aethermind/
```

Do not use `hermes plugins install owner/repo --enable` against this repository
layout unless the public repository root is the plugin directory. Hermes clones a
Git repository into `~/.hermes/plugins/<name>/` and expects `plugin.yaml` and
`__init__.py` at that installed plugin root. This repository keeps the adapter
nested because the Python package is the product boundary.

For development-only manual testing, copy or symlink the adapter into the user
plugin directory and install the package into Hermes' virtualenv:

```bash
HERMES_AGENT_ROOT="${HERMES_AGENT_ROOT:-$HOME/.hermes/hermes-agent}"
uv pip install --python "$HERMES_AGENT_ROOT/venv/bin/python" -e .

mkdir -p "$HOME/.hermes/plugins"
ln -sfn "$PWD/plugins/hermes/aethermind" "$HOME/.hermes/plugins/aethermind"
hermes plugins enable aethermind
```

If your Hermes virtualenv includes `pip`, the equivalent fallback is:

```bash
"$HERMES_AGENT_ROOT/venv/bin/python" -m pip install .
```

## Smoke test

Supported smoke command against a local Hermes checkout:

```bash
HERMES_PYTHON=/path/to/hermes/venv/bin/python3 \
HERMES_AGENT_ROOT=/path/to/hermes-agent \
$HERMES_PYTHON tools/evaluate_hermes_plugin.py --hermes-agent-root "$HERMES_AGENT_ROOT"
```

Use the Hermes virtualenv Python when testing a local Hermes checkout so Hermes'
Python dependencies are available.

For discovery debugging:

```bash
HERMES_PLUGINS_DEBUG=1 hermes plugins list
hermes logs --level WARNING | grep -i plugin
```

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
