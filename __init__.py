"""AetherMind Hermes plugin."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from . import aem_store, cl2

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


def _cl2_brief_handler(args: dict[str, Any], **_kwargs: Any) -> str:
    return _json(
        cl2.brief(
            str(args["project_root"]),
            budget_tokens=int(args.get("budget_tokens") or 1200),
            task_hint=str(args.get("task_hint") or ""),
            ctx_now=str(args.get("ctx_now") or ""),
        )
    )


def _cl2_store_health_handler(args: dict[str, Any], **_kwargs: Any) -> str:
    return _json(cl2.store_health(str(args["project_root"])))


def _cl2_nutrition_handler(args: dict[str, Any], **_kwargs: Any) -> str:
    layer = {
        "type": str(args["type"]),
        "body": str(args["body"]),
        "ctx": str(args.get("ctx") or ""),
        "markers": args.get("markers"),
        "severity": str(args.get("severity") or ""),
        "evidence": args.get("evidence"),
        "kind": str(args.get("kind") or ""),
    }
    return _json(cl2.nutrition_verdict(layer, aem_store.read_layers(str(args["project_root"]))))


def _cl2_write_layer_handler(args: dict[str, Any], **_kwargs: Any) -> str:
    return _json(
        cl2.write_layer(
            str(args["project_root"]),
            layer_type=str(args["type"]),
            body=str(args["body"]),
            ctx=str(args["ctx"]),
            author=str(args.get("author") or "hermes-aethermind-cl2"),
            conf=float(args.get("conf") or 0.8),
            markers=args.get("markers"),
            mode=str(args.get("mode") or "lint"),
            force_reason=str(args.get("force_reason") or ""),
            evidence=args.get("evidence"),
            verification=args.get("verification"),
            supersedes=args.get("supersedes"),
            recurrence_of=args.get("recurrence_of"),
            review_after=str(args.get("review_after") or ""),
            inherit=str(args.get("inherit") or "posture"),
            action_rule=str(args.get("action_rule") or ""),
            scope=str(args.get("scope") or "repo"),
            severity=str(args.get("severity") or ""),
            domain=str(args.get("domain") or ""),
        )
    )


def _cl2_capsule_handler(args: dict[str, Any], **_kwargs: Any) -> str:
    return _json(
        cl2.capsule(
            str(args["project_root"]),
            posture=str(args.get("posture") or ""),
            open_items=str(args.get("open") or args.get("open_items") or ""),
            next_step=str(args.get("next") or args.get("next_step") or ""),
            invalid=str(args.get("invalid") or ""),
            ctx=str(args.get("ctx") or "boundary/capture"),
            author=str(args.get("author") or "hermes-aethermind-cl2"),
            mode=str(args.get("mode") or "lint"),
            force_reason=str(args.get("force_reason") or ""),
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
    why = f" riv={layer.get('riv')} why={layer.get('why')}" if layer.get("riv") is not None else ""
    return (
        f"- {layer.get('type', 'layer')} {layer.get('ctx', '')}{marker_text}{why}: "
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
        budget = int(os.environ.get("AETHERMIND_CL2_AUTO_BUDGET", "900") or "900")
        bundle = cl2.brief(root, budget_tokens=budget, task_hint=user_message, ctx_now=str(root))
        layers = bundle.get("included") or []
        if layers:
            rendered_layers = "\n".join(_format_layer_for_context(layer) for layer in layers)
        else:
            rendered_layers = "- No AetherMind layers exist for this project yet."
        facts = bundle.get("facts_referred") or []
        fact_text = ""
        if facts:
            fact_lines = [f"- {fact.get('claim_hint')} -> {fact.get('backend')}:{fact.get('ref')}" for fact in facts]
            fact_text = "\nFact-shaped records were not injected as posture; look them up deliberately if needed:\n" + "\n".join(fact_lines)
        context = (
            "[AetherMind CL2 automatic continuity is active]\n"
            f"Project root for AetherMind tools: {root}\n"
            f"CL2 brief budget used: {bundle.get('budget', {}).get('used')} / {bundle.get('budget', {}).get('requested')} est. tokens.\n"
            "The store was initialized/read before this model call. The injected layers are ranked by Re-Inheritance Value: what should change the next action, not just recency.\n"
            "Use the aethermind_* tools for this project. Prefer aethermind_cl2_brief/store_health/nutrition/write_layer/capsule when the task needs budgeted selection, write-quality guidance, or boundary capture. "
            "When the turn produces a load-bearing decision, correction, discovery, friction, or uncertainty, write a compact layer and texture pointer. "
            "Do not write secrets, credentials, raw transcripts, or private prompt text.\n"
            "Relevant CL2-selected AetherMind layers:\n"
            f"{rendered_layers}"
            f"{fact_text}\n"
            "[/AetherMind CL2 automatic continuity]"
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
        "aethermind_cl2_brief",
        "Build a CL2 budgeted Re-Inheritance Value brief: selected continuity that should change the next action, not just recent/topical layers.",
        _object_schema(
            {
                **PROJECT_ROOT,
                "budget_tokens": {"type": "integer", "default": 1200},
                "task_hint": {"type": "string"},
                "ctx_now": {"type": "string"},
            },
            ["project_root"],
        ),
        _cl2_brief_handler,
    ),
    (
        "aethermind_cl2_store_health",
        "Report CL2 continuity-store health: density, nutrition, superseded counts, stale candidates, and SHA-256.",
        _object_schema(PROJECT_ROOT, ["project_root"]),
        _cl2_store_health_handler,
    ),
    (
        "aethermind_cl2_nutrition",
        "Lint a would-be AetherMind layer for CL2 write quality without appending it.",
        _object_schema(
            {
                **PROJECT_ROOT,
                "type": {"type": "string"},
                "body": {"type": "string"},
                "ctx": {"type": "string"},
                "markers": TEXT_ARRAY,
                "evidence": TEXT_ARRAY,
                "severity": {"type": "string"},
                "kind": {"type": "string"},
            },
            ["project_root", "type", "body"],
        ),
        _cl2_nutrition_handler,
    ),
    (
        "aethermind_cl2_write_layer",
        "Append a CL2-gated AetherMind layer with optional v2 fields; lint mode is default and capsules remain v1-compatible.",
        _object_schema(
            {
                **PROJECT_ROOT,
                "type": {"type": "string"},
                "body": {"type": "string"},
                "ctx": {"type": "string"},
                "author": {"type": "string"},
                "conf": {"type": "number", "default": 0.8},
                "markers": TEXT_ARRAY,
                "mode": {"type": "string", "enum": ["lint", "coach", "strict"], "default": "lint"},
                "force_reason": {"type": "string"},
                "evidence": TEXT_ARRAY,
                "verification": TEXT_ARRAY,
                "supersedes": TEXT_ARRAY,
                "recurrence_of": TEXT_ARRAY,
                "review_after": {"type": "string"},
                "inherit": {"type": "string", "enum": ["posture", "fact", "both"], "default": "posture"},
                "action_rule": {"type": "string"},
                "scope": {"type": "string"},
                "severity": {"type": "string"},
                "domain": {"type": "string"},
            },
            ["project_root", "type", "body", "ctx"],
        ),
        _cl2_write_layer_handler,
    ),
    (
        "aethermind_cl2_capsule",
        "Append a bounded CL2 boundary-capture capsule. Stores as type=load-bearing, kind=boundary, marker=boundary for v1 reader compatibility.",
        _object_schema(
            {
                **PROJECT_ROOT,
                "posture": {"type": "string"},
                "open": {"type": "string"},
                "open_items": {"type": "string"},
                "next": {"type": "string"},
                "next_step": {"type": "string"},
                "invalid": {"type": "string"},
                "ctx": {"type": "string", "default": "boundary/capture"},
                "author": {"type": "string"},
                "mode": {"type": "string", "enum": ["lint", "coach", "strict"], "default": "lint"},
                "force_reason": {"type": "string"},
            },
            ["project_root"],
        ),
        _cl2_capsule_handler,
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
