"""AetherMind Hermes plugin."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from . import aem_store

TOOLSET = "aethermind"
PLUGIN_ROOT = Path(__file__).resolve().parent
AUTO_CONTEXT_LIMIT = 6


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


def _hook_project_root(kwargs: dict[str, Any]) -> Path:
    raw = (
        kwargs.get("project_root")
        or os.environ.get("AETHERMIND_PROJECT_ROOT")
        or os.environ.get("HERMES_PROJECT_ROOT")
        or os.getcwd()
    )
    return Path(str(raw)).expanduser().resolve()


def _format_layer_for_context(layer: dict[str, Any]) -> str:
    markers = ", ".join(str(marker) for marker in layer.get("markers", []))
    marker_text = f" markers=[{markers}]" if markers else ""
    return (
        f"- {layer.get('type', 'layer')} {layer.get('ctx', '')}{marker_text}: "
        f"{layer.get('body', '')}"
    ).strip()


def _aethermind_session_start(**kwargs: Any) -> None:
    root = _hook_project_root(kwargs)
    aem_store.init_store(root)


def _aethermind_pre_llm_call(**kwargs: Any) -> dict[str, str]:
    root = _hook_project_root(kwargs)
    user_message = str(kwargs.get("user_message") or "")
    try:
        aem_store.init_store(root)
        bundle = aem_store.reorient(root, task=user_message, limit=AUTO_CONTEXT_LIMIT)
        layers = bundle.get("continuity_bundle") or []
        if layers:
            rendered_layers = "\n".join(_format_layer_for_context(layer) for layer in layers)
        else:
            rendered_layers = "- No AetherMind layers exist for this project yet."
        context = (
            "[AetherMind automatic continuity is active]\n"
            f"Project root for AetherMind tools: {root}\n"
            "The AetherMind store has been initialized/read before this model call.\n"
            "Use the aethermind_* tools for this project. When the turn produces a "
            "load-bearing decision, correction, discovery, friction, or uncertainty, "
            "call aethermind_write_layer with this project_root and at least one concise marker. "
            "For meaningful work, also call aethermind_write_texture with a compact attention pointer. "
            "Do not write secrets, credentials, raw transcripts, or private prompt text.\n"
            "Relevant AetherMind layers:\n"
            f"{rendered_layers}\n"
            "[/AetherMind automatic continuity]"
        )
        return {"context": context}
    except Exception as exc:
        return {
            "context": (
                "[AetherMind automatic continuity is active but degraded]\n"
                f"Project root attempted: {root}\n"
                f"Initialization/read failed: {exc}\n"
                "If this is a real project, use aethermind_init_store or choose a writable project root before continuing.\n"
                "[/AetherMind automatic continuity]"
            )
        }


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


def _register_hooks(ctx) -> None:
    register_hook = getattr(ctx, "register_hook", None)
    if register_hook is None:
        return
    register_hook("on_session_start", _aethermind_session_start)
    register_hook("pre_llm_call", _aethermind_pre_llm_call)


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
    _register_hooks(ctx)
