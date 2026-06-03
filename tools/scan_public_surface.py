from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Iterable

SKIP_DIRS = {".git", ".pytest_cache", "__pycache__", ".mypy_cache", ".ruff_cache", "dist", "build"}
TEXT_SUFFIXES = {".md", ".py", ".toml", ".yaml", ".yml", ".txt", ".aem", ".json"}

PATTERNS = [
    ("private_path", re.compile(r"/Users/(?!example\b)[A-Za-z0-9_.-]+")),
    ("private_path", re.compile(r"/home/(?!example\b)[A-Za-z0-9_.-]+")),
    ("secret_assignment", re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[:=]")),
    ("bearer_token", re.compile(r"(?i)bearer\s+[a-z0-9._-]{16,}")),
    ("sk_token", re.compile(r"(?i)sk-[a-z0-9_-]{20,}")),
]
OUT_OF_SCOPE_TERMS = [
    "Cairn" + " Companion",
    "Home" + " Assistant",
    "homestead" + " endpoint",
    "private" + " LAN",
]
ALLOW_LITERAL_MARKERS = ("literal example", "example only", "example:")


def iter_files(paths: Iterable[Path]) -> Iterable[Path]:
    for raw in paths:
        path = raw.expanduser().resolve()
        if not path.exists():
            continue
        if path.is_file():
            if path.suffix in TEXT_SUFFIXES or path.name in {"LICENSE", "README", "README.md"}:
                yield path
            continue
        for child in path.rglob("*"):
            if any(part in SKIP_DIRS for part in child.parts):
                continue
            if child.is_file() and (child.suffix in TEXT_SUFFIXES or child.name in {"LICENSE", "README", "README.md"}):
                yield child


def _line_allowed(line: str) -> bool:
    lower = line.lower()
    return any(marker in lower for marker in ALLOW_LITERAL_MARKERS)


def scan_paths(paths: Iterable[Path]) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    scanned: list[str] = []
    for path in iter_files(paths):
        scanned.append(str(path))
        text = path.read_text(encoding="utf-8", errors="replace")
        for line_no, line in enumerate(text.splitlines(), start=1):
            if _line_allowed(line):
                continue
            for name, pattern in PATTERNS:
                for match in pattern.finditer(line):
                    findings.append({"path": str(path), "line": line_no, "pattern": name, "match": match.group(0)})
            for term in OUT_OF_SCOPE_TERMS:
                if term in line:
                    findings.append({"path": str(path), "line": line_no, "pattern": "out_of_scope_term", "match": term})
    return {"valid": not findings, "scanned": scanned, "findings": findings}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--public-allowlist", nargs="*", type=Path, default=[])
    parser.add_argument("--public-root", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    paths: list[Path] = []
    if args.public_root:
        paths.append(args.public_root)
    paths.extend(args.public_allowlist)
    if not paths:
        parser.error("pass --public-root or --public-allowlist")
    report = scan_paths(paths)
    if args.json or report["valid"]:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
