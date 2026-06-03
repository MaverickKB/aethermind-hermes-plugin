from __future__ import annotations

import argparse
import json
from pathlib import Path

from aethermind import core


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--ctx-prefix", default="")
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()
    report = core.query_layers(args.project_root, ctx_prefix=args.ctx_prefix, limit=args.limit)
    print(json.dumps({"source": str(args.project_root / ".aethermind" / "layers.aem"), "ctx_prefix": args.ctx_prefix, "context_bundle": report["layers"], "layer_count": report["count"]}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
