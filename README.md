# AetherMind Hermes Plugin

AetherMind adds project-local continuity tools to Hermes. It stores compact
`.aem` records beside a project so later agent sessions can recover the
decisions, corrections, discoveries, uncertainty, friction, and verification
that matter.

Version 0.2 uses the same continuity engine and Light v1 methods as the public
AetherMind primitive.

## Install

```bash
hermes plugins install MaverickKB/aethermind-hermes-plugin --enable
hermes plugins list
```

Restart Hermes after enabling the plugin. In a running Hermes session,
`/plugins` should show `aethermind`.

The plugin uses the Hermes process working directory as its default project
root. Set `AETHERMIND_PROJECT_ROOT` when a session must use a different
project root.

## Automatic continuity

The plugin registers two lifecycle hooks:

- `on_session_start` initializes `.aethermind/layers.aem` and
  `.aethermind/texture.aem` when needed;
- `pre_llm_call` reads task-relevant layers and injects a compact continuity
  block before the model call.

Layer creation remains tied to actual project work. The hook does not synthesize
routine task-summary layers.

## Methods

The original plugin methods remain available:

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

Version 0.2 adds:

- `aethermind_capabilities`
- `aethermind_currentness`
- `aethermind_brief`
- `aethermind_brief_anchor`
- `aethermind_audit`
- `aethermind_gate_check`
- `aethermind_write_event`
- `aethermind_read_events`
- `aethermind_archive`

`aethermind_write_layer` also accepts all six Light v1 primitives and their
relationship fields, plus the `next` and remote-work metadata carried by 0.1
records.

## Store layout

```text
.aethermind/
  layers.aem
  texture.aem
  events.aem
  archive.aem
```

Existing 0.1 `layers.aem` and `texture.aem` files remain in place. The first
0.2 write appends to the existing store. See
[Upgrading to 0.2](docs/UPGRADING.md).

## Companion skill

The plugin-qualified skill is:

```text
aethermind:aethermind-continuity
```

Hermes exposes it through `skill_view`.

## Validation

```bash
./scripts/ci-local.sh
```

The validation script compiles the plugin, loads the Hermes registration
surface, exercises the original and 0.2 methods, checks lifecycle hooks, and
checks the public distribution surface.

GitHub Actions runs this same validation on current Ubuntu and Windows runners.
The matrix protects the POSIX `fcntl` backend used on macOS and Linux and the
Windows `msvcrt` backend used by the installed Hermes plugin.

## Documentation

- [Hermes plugin operation](docs/HERMES_PLUGIN.md)
- [AEM Light v1 format](docs/AEM_FORMAT.md)
- [Upgrading to 0.2](docs/UPGRADING.md)
- [Scope](docs/SCOPE.md)
- [Privacy](docs/PRIVACY.md)
- [Change log](CHANGELOG.md)

## License

Apache-2.0. See `LICENSE`.
