# AetherMind Hermes Plugin

AetherMind adds project-local continuity tools to Hermes. It stores compact,
append-only `.aem` records beside a project so future agent sessions can recover
the decisions, corrections, uncertainty, and pressure that matter without
preserving full transcripts.

When enabled, the plugin also registers Hermes lifecycle hooks. Fresh Hermes
sessions automatically initialize/read the project `.aethermind` store and
inject a short AetherMind continuity block before model calls.

This repository is the Hermes plugin distribution. It is intentionally small:

- `plugin.yaml` and `__init__.py` are the Hermes plugin entry point.
- `aem_store.py` contains the local `.aem` store behavior.
- `skills/aethermind-continuity/` provides the companion Hermes skill.
- `docs/` and `examples/` describe the public store contract.

## Install

```bash
hermes plugins install MaverickKB/aethermind-hermes-plugin --enable
hermes plugins list
```

Restart Hermes after enabling the plugin. In a running Hermes session,
`/plugins` should show `aethermind`.

After restart, run Hermes from the project directory you want AetherMind to
cover. The plugin uses the process working directory as the default project
root. You can override it with `AETHERMIND_PROJECT_ROOT`.

## Automatic Use

The plugin registers:

- `on_session_start`, which creates `.aethermind/layers.aem` and
  `.aethermind/texture.aem` for the current project if they do not exist.
- `pre_llm_call`, which reads relevant layers and injects an AetherMind
  continuity block into the current user turn.

That injected block tells the agent to use the `aethermind_*` tools and to write
layers for load-bearing decisions, corrections, discoveries, friction, or
uncertainty. The plugin does not fabricate routine task-summary layers; it
keeps meaningful layer creation tied to actual project work.

The companion skill is plugin-qualified:

```text
aethermind:aethermind-continuity
```

Hermes exposes that skill through `skill_view`. It is not copied into
`~/.hermes/skills` and does not appear in the flat skills list.

## Tools

The plugin registers:

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

## What AetherMind Is

AetherMind is a continuity substrate, not a general memory database. Use it for
small, durable signals that help the next agent understand the project state:

- decisions and constraints that should not be rediscovered;
- corrections to wrong assumptions;
- unresolved uncertainty that changes the next step;
- friction or pressure that shaped the work;
- evidence and verification pointers.

## What It Is Not

AetherMind is not a transcript archive, task log, chat history, analytics store,
or deployment platform. Keep layers compact and avoid writing secrets, private
operator paths, customer data, raw prompts, or high-volume logs.

## Validation

From the repository root:

```bash
./scripts/ci-local.sh
```

The validation script compiles the plugin, smoke-tests the Hermes registration
surface, verifies lifecycle hook behavior, checks the example store, and scans
the public files for common publishing mistakes.

## Documentation

- `docs/SCOPE.md` defines the product boundary.
- `docs/AEM_FORMAT.md` describes the baseline `.aem` record format.
- `docs/HERMES_PLUGIN.md` covers Hermes installation and discovery notes.
- `docs/PRIVACY.md` describes safe layer hygiene.

## License

Apache-2.0. See `LICENSE`.
