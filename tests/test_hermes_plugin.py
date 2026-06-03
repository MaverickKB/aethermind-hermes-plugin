from __future__ import annotations

import json
import importlib.util
from pathlib import Path
from typing import Any

from aethermind import hermes_plugin


class CaptureContext:
    def __init__(self) -> None:
        self.tools: dict[str, dict[str, Any]] = {}
        self.skills: dict[str, Path] = {}

    def register_tool(
        self,
        *,
        name: str,
        toolset: str,
        schema: dict[str, Any],
        handler: Any,
        **kwargs: Any,
    ) -> None:
        self.tools[name] = {
            "toolset": toolset,
            "schema": schema,
            "handler": handler,
            "kwargs": kwargs,
        }

    def register_skill(self, name: str, path: Path, description: str = "") -> None:
        self.skills[name] = path


def test_hermes_entrypoint_registers_aethermind_tools(tmp_path: Path) -> None:
    ctx = CaptureContext()
    hermes_plugin.register(ctx)

    assert sorted(ctx.tools) == [
        "aethermind_evaluate_store",
        "aethermind_export_store",
        "aethermind_import_layers",
        "aethermind_init_store",
        "aethermind_integrity_manifest",
        "aethermind_read_layers",
        "aethermind_read_texture",
        "aethermind_reorient",
        "aethermind_write_layer",
        "aethermind_write_texture",
    ]
    assert {tool["toolset"] for tool in ctx.tools.values()} == {"aethermind"}

    project = tmp_path / "project"
    init = json.loads(
        ctx.tools["aethermind_init_store"]["handler"]({"project_root": str(project)})
    )
    assert init["ok"] is True

    write = json.loads(
        ctx.tools["aethermind_write_layer"]["handler"](
            {
                "project_root": str(project),
                "type": "load-bearing",
                "body": "mission: hermes entrypoint smoke",
                "ctx": "test/hermes",
                "markers": ["hermes"],
            }
        )
    )
    assert write["ok"] is True

    evaluate = json.loads(
        ctx.tools["aethermind_evaluate_store"]["handler"](
            {"project_root": str(project)}
        )
    )
    assert evaluate["valid"] is True


def test_root_plugin_entrypoint_registers_tools_and_skills() -> None:
    plugin_root = Path(__file__).resolve().parents[1]
    spec = importlib.util.spec_from_file_location(
        "aethermind_root_plugin_for_test",
        plugin_root / "__init__.py",
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    ctx = CaptureContext()
    module.register(ctx)

    assert "aethermind_init_store" in ctx.tools
    assert "aethermind_reorient" in ctx.tools
    assert ctx.skills == {
        "aethermind-continuity": plugin_root
        / "skills"
        / "aethermind-continuity"
        / "SKILL.md"
    }
    skill_description = ctx.skills["aethermind-continuity"].read_text(encoding="utf-8")
    assert "description:" in skill_description
