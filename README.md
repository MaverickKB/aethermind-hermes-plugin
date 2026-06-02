# AetherMind — OSS shippable (continuity primitive)

**Product:** Public continuity primitive — spec, validators, human-readable `.aem` contract,
reference harness adapters, CI, redacted benchmark pointers.

**Private canon (policy + lineage):**  
`file:///Users/kbandoly/Programming/personhood-stack/docs/aethermind_three_shippable_roots.md`  
`file:///Users/kbandoly/Programming/personhood-stack/docs/aethermind_distribution_provenance.md`

**Staging / kit source today:** `AetherMind-Release-Evidence/nous-continuity-validation-kit/` (exists
on Ken’s Mac — verified 2026-06-04).

## Bring the kit into this repo

**Submodule (preferred once Git allows local clones):**

```bash
cd /Users/kbandoly/Programming/aethermind-oss
# If `git submodule add` fails with: transport 'file' not allowed
git -c protocol.file.allow=always submodule add \
  ../../AetherMind-Release-Evidence/nous-continuity-validation-kit \
  nous-continuity-validation-kit
```

**Alternatives:** `git subtree add` from the kit repo; or `rsync -a --delete` (loses shared
history — use only as last resort).

## North star (optional research, not OSS requirement)

Do not commit secrets. OSS must remain stranger-runnable (no homestead paths).
