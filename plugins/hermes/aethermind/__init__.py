"""Hermes adapter for the AetherMind OSS continuity primitive."""

from __future__ import annotations

import json
from typing import Any

from aethermind.core import (
    export_store,
    evaluate_store,
    import_layers,
    init_store,
    integrity_manifest,
    query_layers,
    read_texture,
    reorient,
    write_layer,
    write_texture,
)

TOOLSET = "aethermind"


def _json(data: dict[str, Any]) -> str:
    return json.dumps(data, indent=2, sort_keys=True)


def _init_store_handler(args: dict[str, Any], **_kwargs: Any) -> str:
    return _json(init_store(str(args["project_root"])))


def _write_layer_handler(args: dict[str, Any], **_kwargs: Any) -> str:
    return _json(
        write_layer(
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
        query_layers(
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
    return _json(write_texture(str(args["project_root"]), body=str(args["body"]), ctx=str(args.get("ctx") or ""), marker=str(args.get("marker") or "")))


def _read_texture_handler(args: dict[str, Any], **_kwargs: Any) -> str:
    return _json(read_texture(str(args["project_root"])))


def _reorient_handler(args: dict[str, Any], **_kwargs: Any) -> str:
    return _json(reorient(str(args["project_root"]), task=str(args["task"]), limit=int(args.get("limit") or 8)))


def _evaluate_store_handler(args: dict[str, Any], **_kwargs: Any) -> str:
    return _json(evaluate_store(str(args["project_root"])))


def _export_store_handler(args: dict[str, Any], **_kwargs: Any) -> str:
    return _json(export_store(str(args["project_root"])))


def _import_layers_handler(args: dict[str, Any], **_kwargs: Any) -> str:
    return _json(import_layers(str(args["project_root"]), layers_aem=str(args["layers_aem"]), texture_aem=str(args.get("texture_aem") or ""), allow_existing=bool(args.get("allow_existing") or False)))


def _integrity_manifest_handler(args: dict[str, Any], **_kwargs: Any) -> str:
    return _json(integrity_manifest(str(args["project_root"])))


def register(ctx: Any) -> None:
    ctx.register_tool(
        name="aethermind_init_store",
        toolset=TOOLSET,
        schema={"name": "aethermind_init_store", "description": "Initialize an AetherMind .aem store in a project root.", "parameters": {"type": "object", "properties": {"project_root": {"type": "string"}}, "required": ["project_root"]}},
        handler=_init_store_handler,
    )
    ctx.register_tool(
        name="aethermind_write_layer",
        toolset=TOOLSET,
        schema={"name": "aethermind_write_layer", "description": "Append an AetherMind continuity layer.", "parameters": {"type": "object", "properties": {"project_root": {"type": "string"}, "type": {"type": "string", "enum": ["fork", "friction", "discovery", "uncertainty", "correction", "load-bearing"]}, "body": {"type": "string"}, "ctx": {"type": "string"}, "author": {"type": "string"}, "conf": {"type": "number", "default": 1.0}, "markers": {"type": "array", "items": {"type": "string"}}, "evidence": {"type": "array", "items": {"type": "string"}}, "verification": {"type": "array", "items": {"type": "string"}}}, "required": ["project_root", "type", "body", "ctx"]}},
        handler=_write_layer_handler,
    )
    ctx.register_tool(
        name="aethermind_read_layers",
        toolset=TOOLSET,
        schema={"name": "aethermind_read_layers", "description": "Read/search AetherMind continuity layers.", "parameters": {"type": "object", "properties": {"project_root": {"type": "string"}, "ctx_prefix": {"type": "string"}, "type": {"type": "string"}, "marker": {"type": "string"}, "author": {"type": "string"}, "text": {"type": "string"}, "limit": {"type": "integer", "default": 20}}, "required": ["project_root"]}},
        handler=_read_layers_handler,
    )
    ctx.register_tool(name="aethermind_write_texture", toolset=TOOLSET, schema={"name": "aethermind_write_texture", "description": "Append a short AetherMind texture entry.", "parameters": {"type": "object", "properties": {"project_root": {"type": "string"}, "body": {"type": "string"}, "ctx": {"type": "string"}, "marker": {"type": "string"}}, "required": ["project_root", "body"]}}, handler=_write_texture_handler)
    ctx.register_tool(name="aethermind_read_texture", toolset=TOOLSET, schema={"name": "aethermind_read_texture", "description": "Read the AetherMind texture file.", "parameters": {"type": "object", "properties": {"project_root": {"type": "string"}}, "required": ["project_root"]}}, handler=_read_texture_handler)
    ctx.register_tool(name="aethermind_reorient", toolset=TOOLSET, schema={"name": "aethermind_reorient", "description": "Build a task-relevant reorientation bundle from AetherMind layers.", "parameters": {"type": "object", "properties": {"project_root": {"type": "string"}, "task": {"type": "string"}, "limit": {"type": "integer", "default": 8}}, "required": ["project_root", "task"]}}, handler=_reorient_handler)
    ctx.register_tool(name="aethermind_evaluate_store", toolset=TOOLSET, schema={"name": "aethermind_evaluate_store", "description": "Evaluate an AetherMind store for schema, privacy, density warnings, and continuity properties.", "parameters": {"type": "object", "properties": {"project_root": {"type": "string"}}, "required": ["project_root"]}}, handler=_evaluate_store_handler)
    ctx.register_tool(name="aethermind_export_store", toolset=TOOLSET, schema={"name": "aethermind_export_store", "description": "Export an AetherMind store as JSON.", "parameters": {"type": "object", "properties": {"project_root": {"type": "string"}}, "required": ["project_root"]}}, handler=_export_store_handler)
    ctx.register_tool(name="aethermind_import_layers", toolset=TOOLSET, schema={"name": "aethermind_import_layers", "description": "Import a sanitized AetherMind layers.aem payload into a project store.", "parameters": {"type": "object", "properties": {"project_root": {"type": "string"}, "layers_aem": {"type": "string"}, "texture_aem": {"type": "string"}, "allow_existing": {"type": "boolean", "default": False}}, "required": ["project_root", "layers_aem"]}}, handler=_import_layers_handler)
    ctx.register_tool(name="aethermind_integrity_manifest", toolset=TOOLSET, schema={"name": "aethermind_integrity_manifest", "description": "Return SHA-256 hashes and layer IDs for an AetherMind store.", "parameters": {"type": "object", "properties": {"project_root": {"type": "string"}}, "required": ["project_root"]}}, handler=_integrity_manifest_handler)
