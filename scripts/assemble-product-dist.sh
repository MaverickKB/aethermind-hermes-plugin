#!/usr/bin/env bash
set -euo pipefail

VERSION="${1:-v0.1.0-rc.2}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
STAGING="${AETHERMIND_STAGING:-$(cd "$ROOT/.." && pwd)/aethermind-distributable-staging/drops}"
NAME="aethermind-oss-${VERSION#v}"
DROP="$STAGING/$NAME"
TARBALL="$STAGING/$NAME.tar.gz"

cd "$ROOT"

if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "refusing to assemble: working tree has tracked changes" >&2
  git status --short >&2
  exit 1
fi

if [ -n "$(git ls-files --others --exclude-standard)" ]; then
  echo "refusing to assemble: untracked files present" >&2
  git status --short --untracked-files=all >&2
  exit 1
fi

./scripts/ci-local.sh

rm -rf "$DROP" "$TARBALL" "$TARBALL.sha256"
mkdir -p "$DROP"

copy_path() {
  local path="$1"
  if [ -e "$path" ]; then
    mkdir -p "$DROP/$(dirname "$path")"
    cp -R "$path" "$DROP/$path"
  fi
}

for path in README.md README.public.md LICENSE pyproject.toml SECURITY.md CONTRIBUTING.md docs src tools tests examples plugins scripts/ci-local.sh; do
  copy_path "$path"
done

rm -rf "$DROP/.git" "$DROP/.hermes" "$DROP/.aethermind"
find "$DROP" \( -name __pycache__ -o -name .pytest_cache \) -prune -exec rm -rf {} + 2>/dev/null || true
find "$DROP" -name '*.pyc' -delete

(
  cd "$DROP"
  find . -type f -not -name MANIFEST.sha256 -print0 | sort -z | xargs -0 shasum -a 256 > MANIFEST.sha256
)

(
  cd "$STAGING"
  tar -czf "$TARBALL" "$NAME"
  shasum -a 256 "$TARBALL" > "$TARBALL.sha256"
)

echo "$DROP"
echo "$TARBALL"
