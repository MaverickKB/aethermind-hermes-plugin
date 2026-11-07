"""AetherMind continuity store helpers for the Hermes plugin.

The current baseline encoding is TOML-style `[[layer]]` records because it is
portable and easy to inspect. The invariant is append-only, dense,
machine-readable continuity that lets agents reorient cheaply without preserving
full transcripts.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import tomllib
import uuid
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

ALLOWED_LAYER_TYPES = {
    "fork",
    "friction",
    "discovery",
    "uncertainty",
    "correction",
    "load-bearing",
}

PRESSURE_TYPES = {"friction", "correction", "uncertainty"}
REQUIRED_FIELDS = {"id", "ts", "author", "type", "body", "ctx", "conf"}
FORMAT_VERSION = "aethermind-aem-baseline-v1"

# Remote canonical store. A project_root starting with "jarvis:" is routed
# over HTTP to the Jarvis AetherMind MCP instead of the local filesystem,
# so every host reads and writes the ONE tree (canonical store lives on
# Jarvis; the Mac keeps no live store).
REMOTE_PREFIX = "jarvis:"
REMOTE_MCP_URL = os.environ.get(
    "AETHERMIND_REMOTE_MCP", "http://100.82.24.28:8452/mcp"
)

PRIVATE_PATTERNS = [
    re.compile(r"/Users" + r"/[A-Za-z0-9_.-]+"),
    re.compile(r"/home" + r"/[A-Za-z0-9_.-]+"),
    re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[:=]"),
    re.compile(r"(?i)bearer\s+[a-z0-9._-]{16,}"),
    re.compile(r"(?i)sk-[a-z0-9_-]{20,}"),
]


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def toml_string(value: Any) -> str:
    return json.dumps(str(value), ensure_ascii=False)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [part.strip() for part in value.split(",") if part.strip()]
    if isinstance(value, Iterable):
        return [str(item) for item in value]
    return [str(value)]


def project_paths(project_root: str | Path) -> tuple[Path, Path, Path]:
    root = Path(project_root).expanduser().resolve()
    aem = root / ".aethermind"
    return root, aem / "layers.aem", aem / "texture.aem"


def is_remote(project_root: str | Path) -> bool:
    return str(project_root).startswith(REMOTE_PREFIX)


def remote_store_path(project_root: str | Path) -> str:
    return str(project_root)[len(REMOTE_PREFIX):]


def remote_call(project_root: str | Path, tool: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Call one tool on the Jarvis AetherMind MCP and return its JSON result.

    One-shot MCP session per call: initialize, notify, tools/call. Simple and
    stateless; plugin traffic is a handful of calls per turn.
    """
    import urllib.request

    def post(payload: dict[str, Any], session: str | None) -> tuple[dict[str, Any], str | None]:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        if session:
            headers["Mcp-Session-Id"] = session
        request = urllib.request.Request(
            REMOTE_MCP_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=60) as response:
            raw = response.read().decode("utf-8")
            new_session = response.headers.get("Mcp-Session-Id") or session
        text = raw.strip()
        if not text:
            # Notifications answer 202 with an empty body; that is success.
            return None, new_session
        if text.startswith("{"):
            return json.loads(text), new_session
        for line in text.splitlines():
            # streamable-http may answer as SSE; take the first data line with JSON
            if line.startswith("data:"):
                candidate = line[len("data:"):].strip()
                if candidate.startswith("{"):
                    return json.loads(candidate), new_session
        raise ValueError(f"unparsable MCP response for {tool}")

    init_payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-03-26",
            "capabilities": {},
            "clientInfo": {"name": "aem-store-remote", "version": "1.0"},
        },
    }
    _init_response, session = post(init_payload, None)
    post({"jsonrpc": "2.0", "method": "notifications/initialized"}, session)
    call_payload = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": tool,
            "arguments": {**arguments, "project_root": remote_store_path(project_root)},
        },
    }
    result, _session = post(call_payload, session)
    if "error" in result:
        raise RuntimeError(f"MCP {tool} error: {result['error']}")
    content = result.get("result", {}).get("content", [])
    if not content:
        raise RuntimeError(f"MCP {tool} returned no content")
    return json.loads(content[0]["text"])


def init_store(project_root: str | Path) -> dict[str, Any]:
    if is_remote(project_root):
        # The canonical store already exists on Jarvis; nothing to create.
        return {"ok": True, "project_root": remote_store_path(project_root), "remote": True}
    root, layers_path, texture_path = project_paths(project_root)
    layers_path.parent.mkdir(parents=True, exist_ok=True)
    layers_path.touch(exist_ok=True)
    texture_path.touch(exist_ok=True)
    return {
        "ok": True,
        "project_root": str(root),
        "layers_path": str(layers_path),
        "texture_path": str(texture_path),
        "format": FORMAT_VERSION,
    }


def _parse_layers_text(text: str) -> list[dict[str, Any]]:
    if not text.strip():
        return []
    data = tomllib.loads(text)
    layers = data.get("layer", data.get("layers", []))
    if not isinstance(layers, list):
        raise ValueError("layers.aem must contain [[layer]] tables")
    return layers


def validate_layers(layers: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    seen_ids: set[str] = set()
    for index, item in enumerate(layers, start=1):
        if not isinstance(item, dict):
            errors.append(f"layer {index} is not a TOML table")
            continue
        missing = sorted(REQUIRED_FIELDS - set(item))
        if missing:
            errors.append(f"layer {index} missing required fields: {missing}")
            continue
        if "markers" not in item:
            item["markers"] = []
        layer_id = str(item["id"])
        if layer_id in seen_ids:
            errors.append(f"duplicate layer id: {layer_id}")
        seen_ids.add(layer_id)
        if item["type"] not in ALLOWED_LAYER_TYPES:
            item.setdefault("kind", str(item["type"]))
        if not isinstance(item["markers"], list) or not all(isinstance(m, str) for m in item["markers"]):
            errors.append(f"layer {index} markers must be an array of strings")
        try:
            conf = float(item["conf"])
        except Exception:
            errors.append(f"layer {index} conf must be numeric")
            continue
        if conf < 0.0 or conf > 1.0:
            errors.append(f"layer {index} conf must be between 0 and 1")
    return errors


def read_layers(project_root: str | Path) -> list[dict[str, Any]]:
    if is_remote(project_root):
        result = remote_call(project_root, "read_layers", {})
        if not result.get("success"):
            raise RuntimeError(f"remote read_layers failed: {result}")
        return result.get("layers", [])
    _root, layers_path, _texture_path = project_paths(project_root)
    if not layers_path.exists() or not layers_path.read_text(encoding="utf-8").strip():
        return []
    layers = _parse_layers_text(layers_path.read_text(encoding="utf-8"))
    errors = validate_layers(layers)
    if errors:
        raise ValueError("; ".join(errors))
    return layers


def layer_to_toml(layer: dict[str, Any]) -> str:
    markers = ", ".join(toml_string(marker) for marker in string_list(layer.get("markers")))
    text = (
        "[[layer]]\n"
        f"id = {toml_string(layer['id'])}\n"
        f"ts = {toml_string(layer['ts'])}\n"
        f"author = {toml_string(layer['author'])}\n"
        f"type = {toml_string(layer['type'])}\n"
        f"body = {toml_string(layer['body'])}\n"
        f"ctx = {toml_string(layer['ctx'])}\n"
        f"conf = {float(layer['conf'])}\n"
        f"markers = [{markers}]\n"
        f"primitive = {toml_string(layer.get('primitive') or 'layer')}\n"
    )
    for key in ("evidence", "verification", "supersedes", "rollback_of", "recurrence_of"):
        values = string_list(layer.get(key))
        if values:
            rendered = ", ".join(toml_string(value) for value in values)
            text += f"{key} = [{rendered}]\n"
    for key in ("artifact", "artifact_ref", "anchor", "ref", "reason", "scope", "severity"):
        if layer.get(key) is not None:
            text += f"{key} = {toml_string(layer[key])}\n"
    return text + "\n"


def write_layer(
    project_root: str | Path,
    *,
    layer_type: str,
    body: str,
    ctx: str,
    author: str = "aethermind-cli",
    conf: float = 1.0,
    markers: Any = None,
    evidence: Any = None,
    verification: Any = None,
    primitive: str = "layer",
) -> dict[str, Any]:
    if layer_type not in ALLOWED_LAYER_TYPES:
        raise ValueError(f"invalid layer_type: {layer_type}")
    if not body:
        raise ValueError("body is required")
    if not ctx:
        raise ValueError("ctx is required")
    if float(conf) < 0.0 or float(conf) > 1.0:
        raise ValueError("conf must be between 0 and 1")
    if is_remote(project_root):
        result = remote_call(project_root, "write_layer", {
            "layer_type": layer_type,
            "body": body,
            "ctx": ctx,
            "conf": float(conf),
            "markers": string_list(markers),
            "author": author,
            "primitive": primitive,
            "evidence": string_list(evidence),
            "verification": string_list(verification),
        })
        if not result.get("success"):
            raise RuntimeError(f"remote write_layer failed: {result}")
        layer = result.get("layer") or {
            "id": result.get("layer_id"),
            "ts": result.get("ts"),
            "author": author,
            "type": layer_type,
            "body": body,
            "ctx": ctx,
            "conf": float(conf),
        }
        return {
            "ok": True,
            "project_root": remote_store_path(project_root),
            "remote": True,
            "layer": layer,
            "layers_sha256": None,
        }
    init_store(project_root)
    root, layers_path, _texture_path = project_paths(project_root)
    layer = {
        "id": str(uuid.uuid4()),
        "ts": now_utc(),
        "author": author,
        "type": layer_type,
        "body": body,
        "ctx": ctx,
        "conf": float(conf),
        "markers": string_list(markers),
        "primitive": primitive,
        "evidence": string_list(evidence),
        "verification": string_list(verification),
    }
    with layers_path.open("a", encoding="utf-8") as handle:
        handle.write(layer_to_toml(layer))
        handle.flush()
        os.fsync(handle.fileno())
    return {"ok": True, "project_root": str(root), "layer": layer, "layers_sha256": sha256_file(layers_path)}


def query_layers(
    project_root: str | Path,
    *,
    ctx_prefix: str = "",
    layer_type: str = "",
    marker: str = "",
    author: str = "",
    text: str = "",
    limit: int = 20,
) -> dict[str, Any]:
    if is_remote(project_root):
        arguments = {"last_n": int(limit)}
        if ctx_prefix:
            arguments["ctx_prefix"] = ctx_prefix
        if layer_type:
            arguments["type"] = layer_type
        if marker:
            arguments["markers_any"] = [marker]
        if author:
            arguments["author"] = author
        if text:
            arguments["text"] = text
        result = remote_call(project_root, "read_layers", arguments)
        if not result.get("success"):
            raise RuntimeError(f"remote read_layers failed: {result}")
        layers = result.get("layers", [])
        return {
            "count": len(layers),
            "layers": layers,
            "store": result.get("store"),
            "remote": True,
        }

    _root, layers_path, _texture_path = project_paths(project_root)
    if not layers_path.exists():
        raise FileNotFoundError(
            f"No AetherMind store at {layers_path}. A remote store needs the jarvis: prefix."
        )
    layers = read_layers(project_root)
    needle = text.lower()
    selected = []
    for layer in layers:
        if ctx_prefix and not str(layer["ctx"]).startswith(ctx_prefix):
            continue
        if layer_type and layer["type"] != layer_type:
            continue
        if marker and marker not in string_list(layer.get("markers")):
            continue
        if author and layer["author"] != author:
            continue
        if needle:
            body_text = str(layer.get("body") or "")
            context_text = str(layer.get("ctx") or "")
            marker_hit = False
            for item in string_list(layer.get("markers")):
                if needle in item.lower():
                    marker_hit = True
                    break
            body_hit = needle in body_text.lower()
            context_hit = needle in context_text.lower()
            if not body_hit and not context_hit and not marker_hit:
                continue
        selected.append(layer)
    selected.sort(key=lambda layer: str(layer["ts"]))
    if limit:
        selected = selected[-int(limit):]
    return {"count": len(selected), "layers": selected, "store": str(layers_path)}


def write_texture(project_root: str | Path, *, body: str, ctx: str = "", marker: str = "") -> dict[str, Any]:
    if not body:
        raise ValueError("body is required")
    if is_remote(project_root):
        result = remote_call(project_root, "write_texture", {
            "body": body,
            "ctx": ctx,
            "marker": marker or None,
        })
        if not result.get("success"):
            raise RuntimeError(f"remote write_texture failed: {result}")
        return {"ok": True, "entry": result.get("entry"), "texture_sha256": None, "remote": True}
    init_store(project_root)
    _root, _layers_path, texture_path = project_paths(project_root)
    entry = body
    if ctx:
        entry += f"\nContext: {ctx}"
    if marker:
        entry += f"\nMarker: {marker}"
    with texture_path.open("a", encoding="utf-8") as handle:
        handle.write(entry + "\n\n")
        handle.flush()
        os.fsync(handle.fileno())
    return {"ok": True, "entry": entry, "texture_sha256": sha256_file(texture_path)}


def read_texture(project_root: str | Path) -> dict[str, Any]:
    if is_remote(project_root):
        result = remote_call(project_root, "read_texture", {})
        if isinstance(result, dict) and result.get("success") is False:
            raise RuntimeError(f"remote read_texture failed: {result}")
        if isinstance(result, dict):
            return {
                "texture": result.get("texture", ""),
                "texture_sha256": result.get("texture_sha256"),
                "remote": True,
            }
        return {"texture": str(result), "texture_sha256": None, "remote": True}
    _root, _layers_path, texture_path = project_paths(project_root)
    text = texture_path.read_text(encoding="utf-8") if texture_path.exists() else ""
    return {"texture": text, "texture_sha256": sha256_file(texture_path) if texture_path.exists() else None}


def _tokens(value: str) -> set[str]:
    return {term for term in re.split(r"[^a-z0-9_-]+", value.lower()) if len(term) > 2}


def score_layer(layer: dict[str, Any], task: str) -> int:
    score = 0
    task_terms = _tokens(task)
    score += len(task_terms & _tokens(str(layer.get("body", ""))))
    score += len(task_terms & _tokens(str(layer.get("ctx", "")))) * 2
    score += len(task_terms & {str(marker).lower() for marker in string_list(layer.get("markers"))}) * 3
    if layer.get("type") in {"load-bearing", "correction", "friction", "uncertainty"}:
        score += 2
    return score


def reorient(project_root: str | Path, *, task: str, limit: int = 8) -> dict[str, Any]:
    layers = read_layers(project_root)
    ranked = sorted(layers, key=lambda layer: (score_layer(layer, task), str(layer.get("ts", ""))), reverse=True)[: int(limit)]
    return {
        "task": task,
        "selected_count": len(ranked),
        "continuity_bundle": [
            {
                "id": str(layer["id"]),
                "ts": str(layer["ts"]),
                "type": str(layer["type"]),
                "ctx": str(layer["ctx"]),
                "markers": string_list(layer.get("markers")),
                "body": str(layer["body"]),
            }
            for layer in ranked
        ],
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
        words = body.split()
        if len(body) > 480 or len(words) > 80:
            warnings.append(f"layer {index} long body; prefer compact continuity signal over prose")
        if str(layer.get("type")) == "discovery" and any(word in body.lower() for word in ("today i", "then i", "after that")):
            warnings.append(f"layer {index} may read like a task log; keep layers load-bearing")
        if not string_list(layer.get("markers")):
            warnings.append(f"layer {index} has no markers; retrieval may be weaker")
    return warnings


def evaluate_store(project_root: str | Path) -> dict[str, Any]:
    if is_remote(project_root):
        raise ValueError("evaluate_store is not supported for remote roots; run it on the owning host")
    root, layers_path, texture_path = project_paths(project_root)
    errors: list[str] = []
    layers: list[dict[str, Any]] = []
    if not layers_path.exists():
        errors.append(f"missing {layers_path}")
    else:
        try:
            raw_layers = _parse_layers_text(layers_path.read_text(encoding="utf-8"))
            errors.extend(validate_layers(raw_layers))
            if not errors:
                layers = raw_layers
        except Exception as exc:
            errors.append(f"layers parse failed: {exc}")

    privacy_hits: list[str] = []
    if layers_path.exists():
        privacy_hits.extend(privacy_findings(layers_path.read_text(encoding="utf-8")))
    if texture_path.exists():
        privacy_hits.extend(privacy_findings(texture_path.read_text(encoding="utf-8")))
    if privacy_hits:
        errors.append(f"privacy scan found private-looking content: {sorted(set(privacy_hits))}")

    warnings = density_warnings(layers) if layers else []
    contexts = Counter(str(layer.get("ctx")) for layer in layers)
    layer_types = Counter(str(layer.get("type")) for layer in layers)
    markers = Counter(str(marker) for layer in layers for marker in string_list(layer.get("markers")))
    properties = {
        "durability": layers_path.exists() and len(layers) > 0,
        "store_health": layers_path.exists() and not errors,
        "reorientation": any(layer.get("type") in {"load-bearing", "discovery"} for layer in layers),
        "pressure_capture": any(layer.get("type") in PRESSURE_TYPES for layer in layers),
        "retrieval_substrate": any(layer.get("ctx") for layer in layers),
        "texture_signal": texture_path.exists() and bool(texture_path.read_text(encoding="utf-8").strip()),
    }
    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
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


def integrity_manifest(project_root: str | Path) -> dict[str, Any]:
    if is_remote(project_root):
        layers = read_layers(project_root)
        return {
            "project_root": remote_store_path(project_root),
            "files": {},
            "layer_count": len(layers),
            "layer_ids": [str(layer["id"]) for layer in layers],
            "created_by": "aethermind",
            "format": FORMAT_VERSION,
            "remote": True,
        }
    root, layers_path, texture_path = project_paths(project_root)
    files: dict[str, Any] = {}
    for path in (layers_path, texture_path):
        if path.exists():
            rel = path.relative_to(root)
            files[str(rel)] = {"sha256": sha256_file(path), "bytes": path.stat().st_size}
    layers = read_layers(project_root)
    return {"project_root": str(root), "files": files, "layer_count": len(layers), "layer_ids": [str(layer["id"]) for layer in layers], "created_by": "aethermind", "format": FORMAT_VERSION}


def export_store(project_root: str | Path) -> dict[str, Any]:
    if is_remote(project_root):
        raise ValueError("export_store is not supported for remote roots; run it on the owning host")
    root, layers_path, texture_path = project_paths(project_root)
    return {
        "format": FORMAT_VERSION,
        "project_name": root.name,
        "manifest": integrity_manifest(project_root),
        "layers_aem": layers_path.read_text(encoding="utf-8") if layers_path.exists() else "",
        "texture_aem": texture_path.read_text(encoding="utf-8") if texture_path.exists() else "",
    }


def import_layers(project_root: str | Path, *, layers_aem: str, texture_aem: str = "", allow_existing: bool = False) -> dict[str, Any]:
    if is_remote(project_root):
        raise ValueError("import_layers is not supported for remote roots; run it on the owning host")
    root, layers_path, texture_path = project_paths(project_root)
    init_store(project_root)
    existing_layers_text = layers_path.read_text(encoding="utf-8")
    existing_texture_text = texture_path.read_text(encoding="utf-8") if texture_path.exists() else ""
    if existing_layers_text.strip() and not allow_existing:
        raise ValueError("target layers.aem is not empty; pass allow_existing=true to append")
    raw_layers = _parse_layers_text(layers_aem)
    errors = validate_layers(raw_layers)
    if errors:
        raise ValueError("; ".join(errors))

    if allow_existing and existing_layers_text.strip():
        existing_layers = _parse_layers_text(existing_layers_text)
        errors = validate_layers(existing_layers + raw_layers)
        if errors:
            raise ValueError("; ".join(errors))

    if allow_existing:
        if existing_layers_text.strip():
            next_layers_text = existing_layers_text.rstrip() + "\n" + layers_aem.rstrip() + "\n"
        else:
            next_layers_text = layers_aem.rstrip() + "\n"
    else:
        next_layers_text = layers_aem.rstrip() + "\n"
    if texture_aem:
        if allow_existing:
            if existing_texture_text.strip():
                next_texture_text = existing_texture_text.rstrip() + "\n" + texture_aem.rstrip() + "\n"
            else:
                next_texture_text = texture_aem.rstrip() + "\n"
        else:
            next_texture_text = texture_aem.rstrip() + "\n"
    else:
        next_texture_text = existing_texture_text

    layers_path.write_text(next_layers_text, encoding="utf-8")
    if texture_aem:
        texture_path.write_text(next_texture_text, encoding="utf-8")
    return {"ok": True, "project_root": str(root), "imported_layer_count": len(raw_layers), "manifest": integrity_manifest(project_root)}
