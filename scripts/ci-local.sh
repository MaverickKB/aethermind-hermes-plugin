#!/usr/bin/env bash
# Local continuity gate: no third-party CI host. Run before tag or handoff.
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
kit="${root}/nous-continuity-validation-kit"
if [[ ! -d "${kit}/tools" ]]; then
  echo "ci-local: missing submodule at ${kit}; run: git submodule update --init" >&2
  exit 1
fi
cd "${kit}"
python3 -m pytest -q
python3 tools/validate_aem_store.py --project-root fixtures/minimal-aem-project
python3 tools/validate_benchmark_packet.py \
  --zip evidence/first-benchmark-redacted/public-redacted-proof.zip \
  --sha256-file evidence/first-benchmark-redacted/public-redacted-proof.zip.sha256
echo "ci-local: ok"
