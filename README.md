# AetherMind — OSS shippable (continuity primitive)

**Product:** Public continuity primitive — spec, validators, human-readable `.aem` contract,
reference harness adapters, CI, redacted benchmark pointers.

**Private canon (policy + lineage):**  
`file:///Users/kbandoly/Programming/personhood-stack/docs/aethermind_three_shippable_roots.md`  
`file:///Users/kbandoly/Programming/personhood-stack/docs/aethermind_distribution_provenance.md`

**Hermes validation kit (submodule):** `nous-continuity-validation-kit` →
`https://github.com/MaverickKB/nous-continuity-validation-kit.git` (clone with
`git clone --recurse-submodules`).

## Publish this repo (first time)

`gh` may be unavailable on this machine — create an **empty** public repo on GitHub (e.g.
`MaverickKB/aethermind-oss`), then:

```bash
cd /Users/kbandoly/Programming/aethermind-oss
git remote add origin https://github.com/MaverickKB/aethermind-oss.git   # adjust owner/repo
git push -u origin main --tags
```

CI runs on **push** to `main` (see `.github/workflows/ci.yml`).

## North star (optional research, not OSS requirement)

`personhood-stack/docs/continuity_north_star.md` — not required for OSS installs.

Do not commit secrets. OSS must remain stranger-runnable (no homestead paths).
