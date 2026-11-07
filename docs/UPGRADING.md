# Upgrading the Hermes plugin to 0.2

The 0.2 plugin reads the existing 0.1 AEM store directly. Installation does not
rewrite project continuity.

## Preserve the installed plugin and project store

Before replacing an existing plugin checkout, preserve its directory using the
normal Hermes backup or source-control workflow.

For each active project whose continuity is not already versioned:

```bash
cp -R .aethermind .aethermind.pre-0.2
```

## Install the update

```bash
hermes plugins install MaverickKB/aethermind-hermes-plugin --enable
```

Restart Hermes, then confirm that `/plugins` lists `aethermind`.

## Verify the existing store

Use the existing project root:

```text
aethermind_evaluate_store(project_root="<project-root>")
aethermind_capabilities(project_root="<project-root>")
aethermind_currentness(project_root="<project-root>")
```

The existing layer count should remain unchanged until the next real write.

## Continue

The original method names remain valid. New fields and primitives are additive,
and new records append after the existing bytes.

When transferring AEM text through `aethermind_import_layers`, leave
`allow_existing=false` for an empty target. Use `allow_existing=true` only when
the imported records should follow the target's existing records. The plugin
validates the complete combined layer stream before replacing `layers.aem`.
When texture content is included, it preserves existing texture first and
replaces `texture.aem` through the same durable file-write path.

## Rollback

Restore the prior plugin checkout, then restore
`.aethermind.pre-0.2` only if the project store itself must also return to the
preserved point. Keep the 0.2 store copy until any new records have been
reviewed and carried forward.
