from __future__ import annotations

import argparse
import json
from pathlib import Path

from aethermind import core


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()
    report = core.evaluate_store(args.project_root)
    payload = json.dumps(report, indent=2, sort_keys=True)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
