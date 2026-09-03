"""Hermes adapter over the public AetherMind continuity engine."""

from __future__ import annotations

import hashlib
import os
import re
import tempfile
from collections import Counter
from dataclasses import asdict
from pathlib import Path
from typing import Any, Iterable

from . import aethermind_core as core

ALLOWED_LAYER_TYPES = core.ALLOWED_LAYER_TYPES
ALLOWED_LIGHT_PRIMITIVES = core.ALLOWED_LIGHT_PRIMITIVES
PRESSURE_TYPES = {"friction", "correction", "uncertainty"}
FORMAT_VERSION = core.FORMAT_VERSION

PRIVATE_PATTERNS = [
    re.compile(r"/Users" + r"/[A-Za-z0-9_.-]+"),
    re.compile(r"/home" + r"/[A-Za-z0-9_.-]+"),
    re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[:=]"),
    re.compile(r"(?i)bearer\s+[a-z0-9._-]{16,}"),
    re.compile(r"(?i)sk-[a-z0-9_-]{20,}"),
]


def string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [part.strip() for part in value.split(",") if part.strip()]
    if isinstance(value, Iterable):
        return [str(item) for item in value]
    return [str(value)]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _fsync_directory(path: Path) -> None:
    """Persist directory entry changes where the host supports it."""

    try:
        directory_fd = os.open(path, os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)


def _atomic_replace_text(path: Path, text: str) -> None:
    """Durably replace one AEM text file in its owning store."""

    handle, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(handle, "w", encoding="utf-8") as temporary:
            if path.exists() and hasattr(os, "fchmod"):
                os.fchmod(temporary.fileno(), path.stat().st_mode & 0o777)
            temporary.write(text)
            temporary.flush()
            os.fsync(temporary.fileno())
        os.replace(temporary_name, path)
        _fsync_directory(path.parent)
    finally:
        if os.path.exists(temporary_name):
            os.unlink(temporary_name)


def project_paths(project_root: str | Path) -> tuple[Path, Path, Path]:
    root = Path(project_root).expanduser().resolve()
    store = root / ".aethermind"
    return root, store / "layers.aem", store / "texture.aem"


def _aether(project_root: str | Path, *, create: bool = False) -> core.AetherMind:
    return core.AetherMind(project_root, create=create)


def _layer_dict(layer: core.AetherLayer) -> dict[str, Any]:
    payload = asdict(layer)
    receipt = getattr(layer, "receipt_hash", None)
    if receipt:
        payload["receipt_hash"] = receipt
    return payload


def init_store(project_root: str | Path) -> dict[str, Any]:
    root, layers_path, texture_path = project_paths(project_root)
    result = core.initialize_store(root)
    layers_path.touch(exist_ok=True)
    texture_path.touch(exist_ok=True)
    return {
        "ok": True,
        **result,
        "layers_path": str(layers_path),
        "texture_path": str(texture_path),
        "format": FORMAT_VERSION,
    }


def read_layers(project_root: str | Path) -> list[dict[str, Any]]:
    return [_layer_dict(layer) for layer in _aether(project_root).read_layers()]


def validate_layers(layers: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    for index, item in enumerate(layers, start=1):
        try:
            layer = core.LayerStore._layer_from_item(item)
            if layer.id in seen:
                raise ValueError(f"duplicate layer id: {layer.id}")
            seen.add(layer.id)
        except (KeyError, TypeError, ValueError) as exc:
            errors.append(f"layer {index}: {exc}")
    return errors


def write_layer(
    project_root: str | Path,
    *,
    layer_type: str,
    body: str,
    ctx: str,
    author: str = "hermes-aethermind-plugin",
    conf: float = 1.0,
    markers: Any = None,
    evidence: Any = None,
    verification: Any = None,
    primitive: str = "layer",
    **fields: Any,
) -> dict[str, Any]:
    if isinstance(conf, bool) or not isinstance(conf, (int, float)):
        raise ValueError("conf must be a number, not bool or another scalar type")
    init_store(project_root)
    aether = _aether(project_root)
    layer = aether.write_layer(
        type=layer_type,
        body=body,
        ctx=ctx,
        author=author,
        conf=float(conf),
        markers=string_list(markers),
        evidence=string_list(evidence),
        verification=string_list(verification),
        primitive=primitive,
        **fields,
    )
    return {
        "ok": True,
        "project_root": str(aether.project_root),
        "layer": _layer_dict(layer),
        "layers_sha256": sha256_file(aether.layers_path),
    }


def query_layers(
    project_root: str | Path,
    *,
    ctx_prefix: str = "",
    layer_type: str = "",
    marker: str = "",
    author: str = "",
    text: str = "",
    limit: int = 20,
    since_ts: str = "",
    last_n: int | None = None,
    markers_any: Any = None,
) -> dict[str, Any]:
    aether = _aether(project_root)
    layers = aether.read_layers(
        type=layer_type or None,
        author=author or None,
        since_ts=since_ts or None,
        last_n=last_n,
        ctx_prefix=ctx_prefix or None,
        markers_any=string_list(markers_any) or ([marker] if marker else None),
    )
    if text:
        needle = text.lower()
        layers = [
            layer
            for layer in layers
            if needle in layer.body.lower() or needle in layer.ctx.lower()
        ]
    if last_n is not None:
        selected = layers
    else:
        ordered = sorted(layers, key=lambda layer: layer.ts)
        selected = ordered[-max(0, int(limit)) :]
    return {"count": len(selected), "layers": [_layer_dict(layer) for layer in selected]}


def write_texture(
    project_root: str | Path,
    *,
    body: str,
    ctx: str = "",
    marker: str = "",
    author: str = "hermes-aethermind-plugin",
) -> dict[str, Any]:
    init_store(project_root)
    semantic_marker = marker if marker in {"?", "!", "~", ">"} else None
    rendered_body = body
    if marker and semantic_marker is None:
        rendered_body = f"{body}\nMarker: {marker}"
    entry = _aether(project_root).write_texture(
        body=rendered_body,
        ctx=ctx or "aethermind/texture",
        marker=semantic_marker,
        author=author,
    )
    return {
        "ok": True,
        "entry": entry,
        "texture_sha256": sha256_file(_aether(project_root).texture_path),
    }


def read_texture(project_root: str | Path) -> dict[str, Any]:
    aether = _aether(project_root)
    text = aether.read_texture()
    return {
        "texture": text,
        "texture_sha256": sha256_file(aether.texture_path)
        if aether.texture_path.exists()
        else None,
    }


def _tokens(value: str) -> set[str]:
    return {
        term
        for term in re.split(r"[^a-z0-9_-]+", value.lower())
        if len(term) > 2
    }


def _score_layer(layer: dict[str, Any], task: str) -> int:
    task_terms = _tokens(task)
    score = len(task_terms & _tokens(str(layer.get("body", ""))))
    score += len(task_terms & _tokens(str(layer.get("ctx", "")))) * 2
    score += len(
        task_terms
        & {str(marker).lower() for marker in string_list(layer.get("markers"))}
    ) * 3
    if layer.get("type") in {"load-bearing", "correction", "friction", "uncertainty"}:
        score += 2
    return score


def reorient(
    project_root: str | Path,
    *,
    task: str,
    limit: int = 8,
) -> dict[str, Any]:
    layers = read_layers(project_root)
    ranked = sorted(
        layers,
        key=lambda layer: (_score_layer(layer, task), str(layer.get("ts", ""))),
        reverse=True,
    )[: int(limit)]
    return {
        "task": task,
        "selected_count": len(ranked),
        "continuity_bundle": ranked,
    }


def privacy_findings(text: str) -> list[str]:
    findings: list[str] = []
    for pattern in PRIVATE_PATTERNS:
        findings.extend(match.group(0) for match in pattern.finditer(text))
    return sorted(set(findings))


def density_warnings(layers: list[dict[str, Any]]) -> list[str]:
    warnings: list[str] = []
    for index, layer in enumerate(layers, start=1):
        body = str(layer.get("body", ""))
        if len(body) > 480 or len(body.split()) > 80:
            warnings.append(f"layer {index} has a long body")
        if not string_list(layer.get("markers")):
            warnings.append(f"layer {index} has no markers")
    return warnings


def evaluate_store(project_root: str | Path) -> dict[str, Any]:
    root, layers_path, texture_path = project_paths(project_root)
    errors: list[str] = []
    layers: list[dict[str, Any]] = []
    if not layers_path.exists():
        errors.append(f"missing {layers_path}")
    else:
        try:
            layers = read_layers(project_root)
        except Exception as exc:
            errors.append(str(exc))

    privacy_hits: list[str] = []
    for path in (layers_path, texture_path):
        if path.exists():
            privacy_hits.extend(privacy_findings(path.read_text(encoding="utf-8")))
    if privacy_hits:
        errors.append(
            f"private-looking content found: {sorted(set(privacy_hits))}"
        )

    contexts = Counter(str(layer.get("ctx")) for layer in layers)
    layer_types = Counter(str(layer.get("type")) for layer in layers)
    markers = Counter(
        str(marker)
        for layer in layers
        for marker in string_list(layer.get("markers"))
    )
    properties = {
        "durability": layers_path.exists() and bool(layers),
        "store_health": layers_path.exists() and not errors,
        "reorientation": any(
            layer.get("type") in {"load-bearing", "discovery"}
            for layer in layers
        ),
        "pressure_capture": any(
            layer.get("type") in PRESSURE_TYPES for layer in layers
        ),
        "retrieval_substrate": any(layer.get("ctx") for layer in layers),
        "texture_signal": (
            texture_path.exists()
            and bool(texture_path.read_text(encoding="utf-8").strip())
        ),
    }
    return {
        "valid": not errors,
        "errors": errors,
        "warnings": density_warnings(layers),
        "project_root": str(root),
        "layers_sha256": sha256_file(layers_path) if layers_path.exists() else None,
        "texture_sha256": sha256_file(texture_path) if texture_path.exists() else None,
        "layer_count": len(layers),
        "contexts": dict(sorted(contexts.items())),
        "layer_types": dict(sorted(layer_types.items())),
        "markers": dict(sorted(markers.items())),
        "continuity_properties": properties,
        "format": FORMAT_VERSION,
    }


def runtime_capabilities(project_root: str | Path) -> dict[str, Any]:
    return core.runtime_capabilities(project_root)


def currentness(project_root: str | Path, *, as_of: str | None = None) -> dict[str, Any]:
    result = _aether(project_root).currentness(as_of=as_of)
    return {
        **result,
        "history": [_layer_dict(layer) for layer in result["history"]],
        "active_heads": [_layer_dict(layer) for layer in result["active_heads"]],
        "unresolved_currentness": [
            _layer_dict(layer) for layer in result["unresolved_currentness"]
        ],
    }


def brief(project_root: str | Path, *, as_of: str | None = None) -> dict[str, Any]:
    result = _aether(project_root).brief(as_of=as_of)
    return {
        **result,
        "digests": [_layer_dict(layer) for layer in result["digests"]],
        "deltas": [_layer_dict(layer) for layer in result["deltas"]],
    }


def brief_anchor(
    project_root: str | Path,
    *,
    anchor: str | None = None,
    budget: int = 4000,
    as_of: str | None = None,
) -> dict[str, Any]:
    result = _aether(project_root).brief_anchor(
        anchor=anchor, budget=budget, as_of=as_of
    )
    return {
        **result,
        "kept": [_layer_dict(layer) for layer in result["kept"]],
    }


def audit(project_root: str | Path) -> dict[str, Any]:
    return _aether(project_root).audit()


def gate_check(
    project_root: str | Path,
    *,
    plan: dict[str, Any],
    anchor: str | None = None,
) -> dict[str, Any]:
    return _aether(project_root).gate_check(plan, anchor=anchor)


def write_event(
    project_root: str | Path,
    *,
    event_type: str,
    body: str,
    ctx: str,
    author: str = "hermes-aethermind-plugin",
) -> dict[str, Any]:
    init_store(project_root)
    return _aether(project_root).write_event(
        type=event_type, body=body, ctx=ctx, author=author
    )


def read_events(project_root: str | Path) -> dict[str, Any]:
    return _aether(project_root).read_events()


def archive(
    project_root: str | Path,
    *,
    layer_ids: list[str],
    reason: str = "",
) -> dict[str, Any]:
    return _aether(project_root).archive(layer_ids, reason=reason)


def integrity_manifest(project_root: str | Path) -> dict[str, Any]:
    root = Path(project_root).expanduser().resolve()
    store = root / ".aethermind"
    files: dict[str, Any] = {}
    for name in ("layers.aem", "texture.aem", "events.aem", "archive.aem"):
        path = store / name
        if path.exists():
            files[str(path.relative_to(root))] = {
                "sha256": sha256_file(path),
                "bytes": path.stat().st_size,
            }
    layers = read_layers(project_root)
    return {
        "project_root": str(root),
        "files": files,
        "layer_count": len(layers),
        "layer_ids": [str(layer["id"]) for layer in layers],
        "created_by": "aethermind",
        "format": FORMAT_VERSION,
    }


def export_store(project_root: str | Path) -> dict[str, Any]:
    root = Path(project_root).expanduser().resolve()
    store = root / ".aethermind"

    def text(name: str) -> str:
        path = store / name
        return path.read_text(encoding="utf-8") if path.exists() else ""

    return {
        "format": FORMAT_VERSION,
        "project_name": root.name,
        "manifest": integrity_manifest(project_root),
        "layers_aem": text("layers.aem"),
        "texture_aem": text("texture.aem"),
        "events_aem": text("events.aem"),
        "archive_aem": text("archive.aem"),
    }


def _validated_layers_payload(payload: str) -> list[dict[str, Any]]:
    with tempfile.TemporaryDirectory(prefix="aethermind-plugin-import-") as tmp:
        path = Path(tmp) / "layers.aem"
        path.write_text(payload, encoding="utf-8")
        report = core.LayerStore(path).read_report()
        if report.issues:
            issue = report.issues[0]
            raise ValueError(
                f"layer {issue.record_index} at byte {issue.byte_offset}: "
                f"{issue.message}"
            )
        return [_layer_dict(layer) for layer in report.layers]


def import_layers(
    project_root: str | Path,
    *,
    layers_aem: str,
    texture_aem: str = "",
    allow_existing: bool = False,
) -> dict[str, Any]:
    incoming = _validated_layers_payload(layers_aem)
    root, layers_path, texture_path = project_paths(project_root)
    init_store(root)
    existing_layers = layers_path.read_text(encoding="utf-8")
    existing_texture = texture_path.read_text(encoding="utf-8")
    if existing_layers.strip() and not allow_existing:
        raise ValueError(
            "target layers.aem is not empty; pass allow_existing=true to append"
        )

    combined_layers = layers_aem.rstrip() + "\n"
    if allow_existing and existing_layers.strip():
        combined_layers = (
            existing_layers.rstrip() + "\n" + layers_aem.rstrip() + "\n"
        )
    imported = _validated_layers_payload(combined_layers)

    combined_texture = existing_texture
    if texture_aem:
        if allow_existing and existing_texture.strip():
            combined_texture = (
                existing_texture.rstrip() + "\n" + texture_aem.rstrip() + "\n"
            )
        else:
            combined_texture = texture_aem.rstrip() + "\n"

    _atomic_replace_text(layers_path, combined_layers)

    if texture_aem:
        _atomic_replace_text(texture_path, combined_texture)

    return {
        "ok": True,
        "project_root": str(root),
        "imported_layer_count": len(incoming),
        "layer_count": len(imported),
        "manifest": integrity_manifest(root),
    }
