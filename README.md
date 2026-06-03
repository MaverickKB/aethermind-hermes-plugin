# AetherMind — OSS shippable (continuity primitive)

**Product:** Continuity primitive — spec, validators, human-readable `.aem` contract, reference
Hermes plugin, **local** validation gates. **Git is a local continuity asset** (working copy +
optional bare on your mesh); there is **no** GitHub requirement for this program.

**Private canon (policy + lineage):**  
`file:///Users/kbandoly/Programming/personhood-stack/docs/aethermind_three_shippable_roots.md`  
`file:///Users/kbandoly/Programming/personhood-stack/docs/aethermind_distribution_provenance.md`

## Submodule (local path)

`nous-continuity-validation-kit` is recorded in `.gitmodules` as a **sibling path** to this repo:

`../../AetherMind-Release-Evidence/nous-continuity-validation-kit`

Clone layout on the same machine (example):

```text
~/Programming/
  aethermind-oss/          ← this repo
  AetherMind-Release-Evidence/
    nous-continuity-validation-kit/
```

Then:

```bash
cd /Users/kbandoly/Programming/aethermind-oss
git -c protocol.file.allow=always submodule update --init --recursive
```

If `protocol.file` is blocked, use the same `git -c protocol.file.allow=always` flag for the
initial submodule clone.

## Local CI (authoritative)

No `.github/workflows` — run before tags or release handoff:

```bash
./scripts/ci-local.sh
```

## Publish to **mesh-git** (BandolyNAS bare, preferred)

Authoritative pattern for Ken-owned infrastructure is **local bare git on NAS**, not
third-party hosts:

```bash
# Live inventory (do not assume static list):
bash /Users/kbandoly/.codex/skills/mesh-git/scripts/list_repos.sh

# New bare repo on NAS (example name — pick one):
ssh bandolynas "mkdir -p /volume1/mesh-share/repos/aethermind-oss.git && git init --bare /volume1/mesh-share/repos/aethermind-oss.git"

cd /Users/kbandoly/Programming/aethermind-oss
git remote add origin bandolynas:/volume1/mesh-share/repos/aethermind-oss.git
git push -u origin main --tags
```

SSH alias **`bandolynas`**, paths, and access are defined in the **mesh-git** skill
(`~/.codex/skills/mesh-git/SKILL.md`).

## North star (optional research)

`personhood-stack/docs/continuity_north_star.md` — not required for OSS validation.

Do not commit secrets. Keep distributable trees free of operator-private absolute paths in
**committed** config (runtime env overrides are fine).
