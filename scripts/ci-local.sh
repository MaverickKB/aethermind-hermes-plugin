#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
trap 'find "$ROOT" -name __pycache__ -prune -exec rm -rf {} +; find "$ROOT" -name "*.pyc" -delete' EXIT

if [ -n "${PYTHON:-}" ]; then
  PY="$PYTHON"
else
  PY="python3"
fi

"$PY" -m py_compile __init__.py aem_store.py

"$PY" - <<'PY'
from __future__ import annotations

import importlib.util
import json
import re
import sys
import tempfile
import types
from pathlib import Path

root = Path.cwd()
required = {
    "LICENSE",
    "README.md",
    "__init__.py",
    "aem_store.py",
    "plugin.yaml",
    "docs/AEM_FORMAT.md",
    "docs/HERMES_PLUGIN.md",
    "docs/PRIVACY.md",
    "docs/SCOPE.md",
    "examples/minimal-project/.aethermind/layers.aem",
    "examples/minimal-project/.aethermind/texture.aem",
    "examples/minimal-project/README.md",
    "skills/aethermind-continuity/SKILL.md",
    "scripts/assemble-product-dist.sh",
    "scripts/ci-local.sh",
}

for rel in required:
    if not (root / rel).exists():
        raise SystemExit(f"missing required file: {rel}")

for forbidden in ("src", "tests", "tools", "plugins", "pyproject.toml"):
    if (root / forbidden).exists():
        raise SystemExit(f"forbidden publish surface still present: {forbidden}")

manifest = (root / "plugin.yaml").read_text(encoding="utf-8")
for expected in ("name: aethermind", "aethermind_write_layer", "aethermind_reorient"):
    if expected not in manifest:
        raise SystemExit(f"plugin.yaml missing {expected!r}")


class CaptureContext:
    def __init__(self) -> None:
        self.tools = {}
        self.skills = {}

    def register_tool(self, *, name, toolset, schema, handler, **_kwargs):
        self.tools[name] = {"toolset": toolset, "schema": schema, "handler": handler}

    def register_skill(self, name, path, description=""):
        self.skills[name] = {"path": str(path), "description": description}


spec = importlib.util.spec_from_file_location(
    "hermes_plugins.aethermind",
    root / "__init__.py",
    submodule_search_locations=[str(root)],
)
if spec is None or spec.loader is None:
    raise SystemExit("could not load plugin module spec")
ns_pkg = types.ModuleType("hermes_plugins")
ns_pkg.__path__ = []
ns_pkg.__package__ = "hermes_plugins"
sys.modules["hermes_plugins"] = ns_pkg
module = importlib.util.module_from_spec(spec)
sys.modules["hermes_plugins.aethermind"] = module
spec.loader.exec_module(module)

ctx = CaptureContext()
module.register(ctx)
expected_tools = {
    "aethermind_init_store",
    "aethermind_write_layer",
    "aethermind_read_layers",
    "aethermind_write_texture",
    "aethermind_read_texture",
    "aethermind_reorient",
    "aethermind_evaluate_store",
    "aethermind_export_store",
    "aethermind_import_layers",
    "aethermind_integrity_manifest",
}
if set(ctx.tools) != expected_tools:
    raise SystemExit(f"unexpected tools: {sorted(ctx.tools)}")
if "aethermind-continuity" not in ctx.skills:
    raise SystemExit("skill registration missing")

with tempfile.TemporaryDirectory(prefix="aethermind-plugin-smoke-") as tmp:
    project = Path(tmp) / "project"
    init = json.loads(ctx.tools["aethermind_init_store"]["handler"]({"project_root": str(project)}))
    write = json.loads(
        ctx.tools["aethermind_write_layer"]["handler"](
            {
                "project_root": str(project),
                "type": "load-bearing",
                "body": "mission: plugin smoke",
                "ctx": "smoke/mission",
                "markers": ["smoke"],
            }
        )
    )
    texture = json.loads(
        ctx.tools["aethermind_write_texture"]["handler"](
            {"project_root": str(project), "body": "Smoke path is clean.", "ctx": "smoke/texture"}
        )
    )
    report = json.loads(ctx.tools["aethermind_evaluate_store"]["handler"]({"project_root": str(project)}))
    exported = json.loads(ctx.tools["aethermind_export_store"]["handler"]({"project_root": str(project)}))
    imported_project = Path(tmp) / "imported"
    imported = json.loads(
        ctx.tools["aethermind_import_layers"]["handler"](
            {
                "project_root": str(imported_project),
                "layers_aem": exported["layers_aem"],
                "texture_aem": exported["texture_aem"],
            }
        )
    )
    imported_report = json.loads(
        ctx.tools["aethermind_evaluate_store"]["handler"]({"project_root": str(imported_project)})
    )

if not (init["ok"] and write["ok"] and texture["ok"] and report["valid"] and imported["ok"] and imported_report["valid"]):
    raise SystemExit("plugin smoke failed")

skip_dirs = {".git", ".aethermind", "__pycache__", ".pytest_cache", ".cairn"}
text_suffixes = {".md", ".py", ".yaml", ".yml", ".txt", ".aem", ".sh"}
patterns = [
    ("private_path", re.compile(r"/Users" + r"/(?!example\b)[A-Za-z0-9_.-]+")),
    ("private_path", re.compile(r"/home" + r"/(?!example\b)[A-Za-z0-9_.-]+")),
    ("secret_assignment", re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[:=]")),
    ("bearer_token", re.compile(r"(?i)bearer\s+[a-z0-9._-]{16,}")),
    ("sk_token", re.compile(r"(?i)sk-[a-z0-9_-]{20,}")),
    (
        "rough_language",
        re.compile(
            "(?i)\\b("
            + "|".join(["fu" + "ck", "fu" + "cking", "id" + "iot", "du" + "mbass", "bull" + "shit", "stu" + "pid"])
            + ")\\b"
        ),
    ),
]
findings = []
for path in sorted(root.rglob("*")):
    if not path.is_file():
        continue
    rel = path.relative_to(root)
    if any(part in skip_dirs for part in rel.parts):
        continue
    if path.name == ".DS_Store":
        findings.append(f"{rel}: disallowed metadata file")
        continue
    if path.suffix not in text_suffixes and path.name not in {"LICENSE", "README.md"}:
        continue
    text = path.read_text(encoding="utf-8", errors="replace")
    for line_no, line in enumerate(text.splitlines(), start=1):
        if "literal example:" in line.lower():
            continue
        for name, pattern in patterns:
            if pattern.search(line):
                findings.append(f"{rel}:{line_no}: {name}")

if findings:
    raise SystemExit("public scan failed:\n" + "\n".join(findings))
PY

printf 'ci-local: ok\n'
