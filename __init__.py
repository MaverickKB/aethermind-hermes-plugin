"""AetherMind Hermes plugin."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from . import aem_store

TOOLSET = "aethermind"
PLUGIN_ROOT = Path(__file__).resolve().parent


def _json(data: dict[str, Any]) -> str:
    return json.dumps(data, indent=2, sort_keys=True)


def _init_store_handler(args: dict[str, Any], **_kwargs: Any) -> str:
    return _json(aem_store.init_store(str(args["project_root"])))


def _write_layer_handler(args: dict[str, Any], **_kwargs: Any) -> str:
    return _json(
        aem_store.write_layer(
            str(args["project_root"]),
            layer_type=str(args["type"]),
            body=str(args["body"]),
            ctx=str(args["ctx"]),
            author=str(args.get("author") or "hermes-aethermind-plugin"),
            conf=float(args.get("conf") or 1.0),
            markers=args.get("markers"),
            evidence=args.get("evidence"),
            verification=args.get("verification"),
        )
    )


def _read_layers_handler(args: dict[str, Any], **_kwargs: Any) -> str:
    return _json(
        aem_store.query_layers(
            str(args["project_root"]),
            ctx_prefix=str(args.get("ctx_prefix") or ""),
            layer_type=str(args.get("type") or ""),
            marker=str(args.get("marker") or ""),
            author=str(args.get("author") or ""),
            text=str(args.get("text") or ""),
            limit=int(args.get("limit") or 20),
        )
    )


def _write_texture_handler(args: dict[str, Any], **_kwargs: Any) -> str:
    return _json(
        aem_store.write_texture(
            str(args["project_root"]),
            body=str(args["body"]),
            ctx=str(args.get("ctx") or ""),
            marker=str(args.get("marker") or ""),
        )
    )


def _read_texture_handler(args: dict[str, Any], **_kwargs: Any) -> str:
    return _json(aem_store.read_texture(str(args["project_root"])))


def _reorient_handler(args: dict[str, Any], **_kwargs: Any) -> str:
    return _json(
        aem_store.reorient(
            str(args["project_root"]),
            task=str(args["task"]),
            limit=int(args.get("limit") or 8),
        )
    )


def _evaluate_store_handler(args: dict[str, Any], **_kwargs: Any) -> str:
    return _json(aem_store.evaluate_store(str(args["project_root"])))


def _export_store_handler(args: dict[str, Any], **_kwargs: Any) -> str:
    return _json(aem_store.export_store(str(args["project_root"])))


def _import_layers_handler(args: dict[str, Any], **_kwargs: Any) -> str:
    return _json(
        aem_store.import_layers(
            str(args["project_root"]),
            layers_aem=str(args["layers_aem"]),
            texture_aem=str(args.get("texture_aem") or ""),
            allow_existing=bool(args.get("allow_existing") or False),
        )
    )


def _integrity_manifest_handler(args: dict[str, Any], **_kwargs: Any) -> str:
    return _json(aem_store.integrity_manifest(str(args["project_root"])))


def _object_schema(properties: dict[str, Any], required: list[str]) -> dict[str, Any]:
    return {"type": "object", "properties": properties, "required": required}


PROJECT_ROOT = {"project_root": {"type": "string"}}
TEXT_ARRAY = {"type": "array", "items": {"type": "string"}}

TOOL_SPECS = [
    (
        "aethermind_init_store",
        "Initialize an AetherMind store in a project root.",
        _object_schema(PROJECT_ROOT, ["project_root"]),
        _init_store_handler,
    ),
    (
        "aethermind_write_layer",
        "Append a compact AetherMind continuity layer.",
        _object_schema(
            {
                **PROJECT_ROOT,
                "type": {
                    "type": "string",
                    "enum": sorted(aem_store.ALLOWED_LAYER_TYPES),
                },
                "body": {"type": "string"},
                "ctx": {"type": "string"},
                "author": {"type": "string"},
                "conf": {"type": "number", "default": 1.0},
                "markers": TEXT_ARRAY,
                "evidence": TEXT_ARRAY,
                "verification": TEXT_ARRAY,
            },
            ["project_root", "type", "body", "ctx"],
        ),
        _write_layer_handler,
    ),
    (
        "aethermind_read_layers",
        "Read or search AetherMind continuity layers.",
        _object_schema(
            {
                **PROJECT_ROOT,
                "ctx_prefix": {"type": "string"},
                "type": {"type": "string"},
                "marker": {"type": "string"},
                "author": {"type": "string"},
                "text": {"type": "string"},
                "limit": {"type": "integer", "default": 20},
            },
            ["project_root"],
        ),
        _read_layers_handler,
    ),
    (
        "aethermind_write_texture",
        "Append a short AetherMind texture entry.",
        _object_schema(
            {
                **PROJECT_ROOT,
                "body": {"type": "string"},
                "ctx": {"type": "string"},
                "marker": {"type": "string"},
            },
            ["project_root", "body"],
        ),
        _write_texture_handler,
    ),
    (
        "aethermind_read_texture",
        "Read the AetherMind texture file.",
        _object_schema(PROJECT_ROOT, ["project_root"]),
        _read_texture_handler,
    ),
    (
        "aethermind_reorient",
        "Build a task-relevant reorientation bundle from AetherMind layers.",
        _object_schema(
            {
                **PROJECT_ROOT,
                "task": {"type": "string"},
                "limit": {"type": "integer", "default": 8},
            },
            ["project_root", "task"],
        ),
        _reorient_handler,
    ),
    (
        "aethermind_evaluate_store",
        "Evaluate an AetherMind store for schema, privacy, density, and retrieval signals.",
        _object_schema(PROJECT_ROOT, ["project_root"]),
        _evaluate_store_handler,
    ),
    (
        "aethermind_export_store",
        "Export an AetherMind store as JSON.",
        _object_schema(PROJECT_ROOT, ["project_root"]),
        _export_store_handler,
    ),
    (
        "aethermind_import_layers",
        "Import a sanitized AetherMind layers.aem payload into a project store.",
        _object_schema(
            {
                **PROJECT_ROOT,
                "layers_aem": {"type": "string"},
                "texture_aem": {"type": "string"},
                "allow_existing": {"type": "boolean", "default": False},
            },
            ["project_root", "layers_aem"],
        ),
        _import_layers_handler,
    ),
    (
        "aethermind_integrity_manifest",
        "Return SHA-256 hashes and layer IDs for an AetherMind store.",
        _object_schema(PROJECT_ROOT, ["project_root"]),
        _integrity_manifest_handler,
    ),
]


def _skill_description(skill_md: Path) -> str:
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return ""
    parts = text.split("---", 2)
    if len(parts) < 3:
        return ""
    for line in parts[1].splitlines():
        key, sep, value = line.partition(":")
        if sep and key.strip() == "description":
            return value.strip().strip('"')
    return ""


def _register_skills(ctx) -> None:
    register_skill = getattr(ctx, "register_skill", None)
    if register_skill is None:
        return
    skills_dir = PLUGIN_ROOT / "skills"
    if not skills_dir.is_dir():
        return
    for child in sorted(skills_dir.iterdir()):
        skill_md = child / "SKILL.md"
        if child.is_dir() and skill_md.exists():
            register_skill(child.name, skill_md, _skill_description(skill_md))


def register(ctx) -> None:
    for name, description, parameters, handler in TOOL_SPECS:
        ctx.register_tool(
            name=name,
            toolset=TOOLSET,
            schema={
                "name": name,
                "description": description,
                "parameters": parameters,
            },
            handler=handler,
        )
    _register_skills(ctx)
