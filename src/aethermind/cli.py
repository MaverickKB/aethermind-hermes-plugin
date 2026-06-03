from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from . import core


def emit(data: dict[str, Any], *, out: Path | None = None) -> None:
    payload = json.dumps(data, indent=2, sort_keys=True)
    if out is not None:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(payload + "\n", encoding="utf-8")
        data = {"ok": True, "out": str(out), "format": data.get("format")}
        payload = json.dumps(data, indent=2, sort_keys=True)
    print(payload)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="aethermind")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("init")
    p.add_argument("--project-root", required=True)

    p = sub.add_parser("write-layer")
    p.add_argument("--project-root", required=True)
    p.add_argument("--type", required=True, choices=sorted(core.ALLOWED_LAYER_TYPES))
    p.add_argument("--body", required=True)
    p.add_argument("--ctx", required=True)
    p.add_argument("--author", default="aethermind-cli")
    p.add_argument("--conf", type=float, default=1.0)
    p.add_argument("--marker", action="append", dest="markers", default=[])
    p.add_argument("--evidence", action="append", default=[])
    p.add_argument("--verification", action="append", default=[])

    p = sub.add_parser("read-layers")
    p.add_argument("--project-root", required=True)
    p.add_argument("--ctx-prefix", default="")
    p.add_argument("--type", default="")
    p.add_argument("--marker", default="")
    p.add_argument("--author", default="")
    p.add_argument("--text", default="")
    p.add_argument("--limit", type=int, default=20)

    p = sub.add_parser("write-texture")
    p.add_argument("--project-root", required=True)
    p.add_argument("--body", required=True)
    p.add_argument("--ctx", default="")
    p.add_argument("--marker", default="")

    p = sub.add_parser("read-texture")
    p.add_argument("--project-root", required=True)

    p = sub.add_parser("reorient")
    p.add_argument("--project-root", required=True)
    p.add_argument("--task", required=True)
    p.add_argument("--limit", type=int, default=8)

    p = sub.add_parser("validate-store")
    p.add_argument("--project-root", required=True)

    p = sub.add_parser("manifest")
    p.add_argument("--project-root", required=True)

    p = sub.add_parser("export")
    p.add_argument("--project-root", required=True)
    p.add_argument("--out", type=Path)

    p = sub.add_parser("import")
    p.add_argument("--project-root", required=True)
    p.add_argument("--in", dest="infile", type=Path, required=True)
    p.add_argument("--allow-existing", action="store_true")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "init":
            emit(core.init_store(args.project_root))
        elif args.command == "write-layer":
            emit(
                core.write_layer(
                    args.project_root,
                    layer_type=args.type,
                    body=args.body,
                    ctx=args.ctx,
                    author=args.author,
                    conf=args.conf,
                    markers=args.markers,
                    evidence=args.evidence,
                    verification=args.verification,
                )
            )
        elif args.command == "read-layers":
            emit(
                core.query_layers(
                    args.project_root,
                    ctx_prefix=args.ctx_prefix,
                    layer_type=args.type,
                    marker=args.marker,
                    author=args.author,
                    text=args.text,
                    limit=args.limit,
                )
            )
        elif args.command == "write-texture":
            emit(core.write_texture(args.project_root, body=args.body, ctx=args.ctx, marker=args.marker))
        elif args.command == "read-texture":
            emit(core.read_texture(args.project_root))
        elif args.command == "reorient":
            emit(core.reorient(args.project_root, task=args.task, limit=args.limit))
        elif args.command == "validate-store":
            report = core.evaluate_store(args.project_root)
            emit(report)
            return 0 if report["valid"] else 1
        elif args.command == "manifest":
            emit(core.integrity_manifest(args.project_root))
        elif args.command == "export":
            emit(core.export_store(args.project_root), out=args.out)
        elif args.command == "import":
            payload = json.loads(args.infile.read_text(encoding="utf-8"))
            emit(
                core.import_layers(
                    args.project_root,
                    layers_aem=str(payload.get("layers_aem", "")),
                    texture_aem=str(payload.get("texture_aem", "")),
                    allow_existing=args.allow_existing,
                )
            )
        return 0
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2, sort_keys=True), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
