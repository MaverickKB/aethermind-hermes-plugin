#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [ -n "${PYTHON:-}" ]; then
  PY="$PYTHON"
elif [ -x "$ROOT/.venv/bin/python3" ]; then
  PY="$ROOT/.venv/bin/python3"
elif [ -x "$ROOT/venv/bin/python3" ]; then
  PY="$ROOT/venv/bin/python3"
else
  PY="python3"
fi

if ! PYTHONPATH=src "$PY" -c 'import pytest' >/dev/null 2>&1; then
  CI_VENV="$(mktemp -d /tmp/aethermind-ci-venv.XXXXXX)"
  trap 'rm -rf "$CI_VENV"' EXIT
  "$PY" -m venv "$CI_VENV"
  "$CI_VENV/bin/python" -m pip install -q --upgrade pip pytest
  PY="$CI_VENV/bin/python"
fi

rm -rf /tmp/aethermind-ci-smoke

PYTHONPATH=src "$PY" -m py_compile src/aethermind/*.py tools/*.py plugins/hermes/aethermind/*.py
PYTHONPATH=src "$PY" -m pytest -q
PYTHONPATH=src "$PY" -m aethermind.cli init --project-root /tmp/aethermind-ci-smoke/project >/tmp/aethermind-ci-smoke-init.json
PYTHONPATH=src "$PY" -m aethermind.cli write-layer --project-root /tmp/aethermind-ci-smoke/project --type load-bearing --body "mission: ci smoke" --ctx "ci/smoke" --marker smoke >/tmp/aethermind-ci-smoke-write1.json
PYTHONPATH=src "$PY" -m aethermind.cli write-layer --project-root /tmp/aethermind-ci-smoke/project --type friction --body "pressure: ci smoke captures pressure" --ctx "ci/pressure" --marker pressure >/tmp/aethermind-ci-smoke-write2.json
PYTHONPATH=src "$PY" -m aethermind.cli validate-store --project-root /tmp/aethermind-ci-smoke/project >/tmp/aethermind-ci-smoke-validate.json
PYTHONPATH=src "$PY" -m aethermind.cli reorient --project-root /tmp/aethermind-ci-smoke/project --task "resume ci smoke" >/tmp/aethermind-ci-smoke-reorient.json
PYTHONPATH=src "$PY" -m aethermind.cli export --project-root /tmp/aethermind-ci-smoke/project --out /tmp/aethermind-ci-smoke/export.json >/tmp/aethermind-ci-smoke-export.json
PYTHONPATH=src "$PY" -m aethermind.cli import --project-root /tmp/aethermind-ci-smoke/imported --in /tmp/aethermind-ci-smoke/export.json >/tmp/aethermind-ci-smoke-import.json
PYTHONPATH=src "$PY" -m aethermind.cli manifest --project-root /tmp/aethermind-ci-smoke/imported >/tmp/aethermind-ci-smoke-manifest.json
PYTHONPATH=src "$PY" tools/scan_public_surface.py --public-allowlist README.md docs src tools examples tests plugins scripts pyproject.toml SECURITY.md CONTRIBUTING.md LICENSE >/tmp/aethermind-ci-smoke-scan.json
PYTHONPATH=src "$PY" tools/validate_aem_store.py --project-root examples/minimal-project >/tmp/aethermind-ci-smoke-fixture.json
PYTHONPATH=src "$PY" tools/replay_aem_context.py --project-root examples/minimal-project --ctx-prefix example/ >/tmp/aethermind-ci-smoke-replay.json

printf 'ci-local: ok\n'
