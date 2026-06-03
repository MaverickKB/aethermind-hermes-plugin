# CLI

Install from a checkout:

```bash
python3 -m pip install -e .
```

Commands emit JSON.

## Initialize

```bash
aethermind init --project-root ./my-project
```

## Write layers

```bash
aethermind write-layer --project-root ./my-project \
  --type load-bearing \
  --body "mission: preserve compact continuity" \
  --ctx "planning/mission" \
  --marker mission

aethermind write-layer --project-root ./my-project \
  --type uncertainty \
  --body "unknown: final storage encoding may become denser than TOML" \
  --ctx "format/encoding" \
  --marker encoding
```

## Read/search

```bash
aethermind read-layers --project-root ./my-project --ctx-prefix planning/
aethermind read-layers --project-root ./my-project --text continuity
```

## Reorient

```bash
aethermind reorient --project-root ./my-project --task "resume format work"
```

## Validate and manifest

```bash
aethermind validate-store --project-root ./my-project
aethermind manifest --project-root ./my-project
```

`validate-store` exits non-zero when the store has schema or privacy errors.
Density issues are warnings.

## Export/import

```bash
aethermind export --project-root ./my-project --out /tmp/aethermind-export.json
aethermind import --project-root /tmp/imported-project --in /tmp/aethermind-export.json
```
