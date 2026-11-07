"""AetherMind CL2 helpers for the Hermes plugin.

CL2 is additive over the v1 `.aem` contract. It keeps v1 layer types valid and
stores boundary capsules as `type="load-bearing"`, `kind="boundary"`, marker
`boundary` until every reader accepts a first-class CL2 boundary type.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import math
import re
import textwrap
import uuid
from pathlib import Path
from typing import Any, Iterable

from . import aem_store

TYPE_BASE = {
    "correction": 1.0,
    "load-bearing": 0.9,
    "friction": 0.7,
    "fork": 0.7,
    "uncertainty": 0.6,
    "discovery": 0.5,
}

TYPE_BOUNDS = {
    "correction": 1800,
    "load-bearing": 1800,
    "friction": 1400,
    "uncertainty": 1400,
    "fork": 1400,
    "discovery": 1200,
}

NARRATION_PATTERNS = [
    re.compile(r"\b(i|we)\s+(created|updated|ran|edited|changed|added|removed|fixed)\b", re.I),
    re.compile(r"\b(task|work)\s+(complete|done|finished)\b", re.I),
    re.compile(r"\bfiles?\s+(created|changed|modified)\b", re.I),
]

POSTURE_PATTERNS = [
    re.compile(
        r"\b(do not|don't|never|must|should|because|instead|avoid|blocked|failed|wrong|stale|supersed|verify|boundary|permission|contract|invariant|posture|open|next|invalid|preserve|use)\b",
        re.I,
    ),
    re.compile(r"[!?~>]"),
]


def _layers_path(project_root: str | Path) -> Path | None:
    if aem_store.is_remote(project_root):
        return None
    _root, layers_path, _texture = aem_store.project_paths(project_root)
    return layers_path


def _sha256(path: Path | None) -> str | None:
    if path is None:
        return None
    if not path.exists():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _now_utc() -> str:
    return dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_ts(value: Any) -> dt.datetime | None:
    if not value:
        return None
    if isinstance(value, dt.datetime):
        return value if value.tzinfo else value.replace(tzinfo=dt.UTC)
    try:
        return dt.datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def _token_estimate(text: str) -> int:
    return max(1, math.ceil(len(text) / 4))


def _toml_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return str(value)
    if isinstance(value, (list, tuple, set)):
        return "[" + ", ".join(_toml_value(v) for v in value) + "]"
    if value is None:
        return json.dumps("")
    return json.dumps(str(value), ensure_ascii=False)


REMOTE_LAYER_FIELDS = (
    "layer_type", "body", "ctx", "conf", "markers", "author", "primitive",
    "thread_key", "supersedes", "rollback_of", "corrects", "evidence",
    "recurrence_of", "verification", "artifact", "artifact_ref", "anchor",
    "ref", "kind", "label", "host", "repo_root", "content_id", "selector",
    "span_hint", "domain", "symptom", "next_verification",
    "suspected_mechanism", "scope", "severity", "owner_hint", "repair",
    "reason", "replacement", "restored_to", "inline",
)


def _append_layer(project_root: str | Path, layer: dict[str, Any]) -> dict[str, Any]:
    if aem_store.is_remote(project_root):
        arguments = {}
        for key in REMOTE_LAYER_FIELDS:
            value = layer.get(key)
            if value not in (None, "", []):
                arguments[key] = value
        # The remote tool expects the type under the name layer_type.
        if "layer_type" not in arguments and layer.get("type") is not None:
            arguments["layer_type"] = layer["type"]
        arguments.pop("type", None)
        result = aem_store.remote_call(project_root, "write_layer", arguments)
        if not result.get("success"):
            raise RuntimeError(f"remote write_layer failed: {result}")
        stored = result.get("layer") or layer
        return {
            "ok": True,
            "project_root": aem_store.remote_store_path(project_root),
            "remote": True,
            "layer": stored,
            "layers_sha256": None,
        }
    aem_store.init_store(project_root)
    path = _layers_path(project_root)
    ordered = ["id", "ts", "author", "type", "body", "ctx", "conf", "markers", "primitive"]
    keys = ordered + [key for key in sorted(layer) if key not in ordered]
    lines = ["[[layer]]"]
    for key in keys:
        value = layer.get(key)
        if value not in (None, "", []):
            lines.append(f"{key} = {_toml_value(value)}")
    with path.open("a", encoding="utf-8") as handle:
        if path.stat().st_size:
            handle.write("\n")
        handle.write("\n".join(lines) + "\n")
        handle.flush()
    return {"ok": True, "project_root": str(Path(project_root).expanduser().resolve()), "layer": layer, "layers_sha256": _sha256(path)}


def live_ids(layers: Iterable[dict[str, Any]]) -> tuple[set[str], set[str]]:
    all_ids: set[str] = set()
    superseded: set[str] = set()
    for layer in layers:
        layer_id = str(layer.get("id", ""))
        if layer_id:
            all_ids.add(layer_id)
        for target in layer.get("supersedes", []) or []:
            superseded.add(str(target))
    return all_ids - superseded, superseded


def is_boundary(layer: dict[str, Any]) -> bool:
    markers = set(aem_store.string_list(layer.get("markers")))
    return layer.get("type") == "boundary" or layer.get("kind") == "boundary" or "boundary" in markers


def nutrition_verdict(layer: dict[str, Any], existing: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    body = str(layer.get("body", "")).strip()
    layer_type = str(layer.get("type", ""))
    markers = aem_store.string_list(layer.get("markers"))
    evidence = aem_store.string_list(layer.get("evidence"))
    verdict = "dense"
    reasons: list[str] = []
    suggestions: list[str] = []

    if layer_type not in aem_store.ALLOWED_LAYER_TYPES:
        verdict = "questionable"
        reasons.append(f"unknown or experimental layer type {layer_type!r}")
        suggestions.append("Use a v1 layer type; for capsules use type='load-bearing', kind='boundary', marker='boundary'.")

    if not body:
        return {"verdict": "transcript", "reasons": ["empty body"], "suggestions": ["Write the consequence future agents must inherit."]}

    bound = 900 if is_boundary(layer) else TYPE_BOUNDS.get(layer_type, 1400)
    if len(body) > bound:
        verdict = "transcript"
        reasons.append(f"body length {len(body)} exceeds bound {bound}")
        suggestions.append("Compress to posture/action/evidence; move logs or prose elsewhere.")
    if body.count("\n") + 1 > 8:
        verdict = "transcript"
        reasons.append("body has too many lines; likely pasted notes/logs")
        suggestions.append("Use evidence pointers rather than raw transcript/log content.")

    posture_hits = sum(1 for pattern in POSTURE_PATTERNS if pattern.search(body))
    narration_hits = sum(1 for pattern in NARRATION_PATTERNS if pattern.search(body))
    if narration_hits and not posture_hits:
        verdict = "memory_shaped" if verdict == "dense" else verdict
        reasons.append("routine work narration rather than inherited posture")
        suggestions.append("Redirect routine change narration to git/docs; write only what changes next behavior.")
    elif posture_hits == 0 and layer_type in {"load-bearing", "correction"}:
        verdict = "questionable" if verdict == "dense" else verdict
        reasons.append("high-value type lacks obvious behavioral consequence")
        suggestions.append("Add the decision/correction/action rule future agents must inherit.")

    if layer_type in {"load-bearing", "correction"} and not is_boundary(layer) and str(layer.get("severity", "")).lower() == "high" and not evidence:
        verdict = "questionable" if verdict == "dense" else verdict
        reasons.append("high-severity checkable claim has no evidence pointer")
        suggestions.append("Add evidence refs or lower severity.")

    if existing:
        normalized = re.sub(r"\W+", " ", body.lower()).strip()
        for old in existing[-50:]:
            old_norm = re.sub(r"\W+", " ", str(old.get("body", "")).lower()).strip()
            if normalized and old_norm and normalized == old_norm:
                verdict = "questionable" if verdict == "dense" else verdict
                reasons.append(f"duplicate of existing layer {old.get('id')}")
                suggestions.append("Use recurrence_of or supersedes instead of restating a live record.")
                break

    if not reasons:
        reasons.append("record has continuity shape and acceptable density")
    return {"verdict": verdict, "reasons": reasons, "suggestions": suggestions, "markers": markers}


def _age_days(layer: dict[str, Any]) -> float:
    ts = _parse_ts(layer.get("ts"))
    if not ts:
        return 9999.0
    return max(0.0, (dt.datetime.now(dt.UTC) - ts).total_seconds() / 86400)


def _freshness(layer: dict[str, Any]) -> tuple[float, list[str]]:
    age = _age_days(layer)
    flags: list[str] = []
    if is_boundary(layer):
        value = 1.0 if age <= 2 else 0.3 if age <= 14 else 0.12
    elif layer.get("type") in {"correction", "load-bearing"}:
        value = 0.5 ** (age / 120) if age < 2000 else 0.5
    else:
        value = 0.5 ** (age / 60) if age < 2000 else 0.3
    review_after = layer.get("review_after")
    if review_after:
        try:
            if dt.datetime.now(dt.UTC).date() > dt.date.fromisoformat(str(review_after)[:10]):
                value *= 0.5
                flags.append("past review_after; stale candidate")
        except ValueError:
            flags.append("invalid review_after")
    return max(0.05, value), flags


def _scope_match(layer: dict[str, Any], ctx_now: str, task_hint: str) -> tuple[float, str]:
    ctx = str(layer.get("ctx", ""))
    scope = str(layer.get("scope", "") or "repo")
    haystack = f"{ctx_now} {task_hint}".lower()
    task_words = set(re.findall(r"[a-z0-9_-]{4,}", haystack))
    if ctx and (ctx.lower() in haystack or (haystack.strip() and haystack.strip() in ctx.lower())):
        return 1.0, "scope exact"
    if scope.startswith("area:") and scope[5:].lower() in haystack:
        return 1.0, "area match"
    if scope == "global":
        return 0.7, "global scope"
    if scope == "host":
        return 0.5, "host scope"
    ctx_words = set(re.findall(r"[a-z0-9_-]{4,}", ctx.lower()))
    marker_words = set()
    for marker in aem_store.string_list(layer.get("markers")):
        marker_words.update(re.findall(r"[a-z0-9_-]{4,}", marker.lower()))
    if task_words and (ctx_words | marker_words) & task_words:
        return 0.9, "ctx/marker lexical overlap"
    body_words = set(re.findall(r"[a-z0-9_-]{4,}", str(layer.get("body", "")).lower()))
    body_overlap = body_words & task_words
    if task_words and len(body_overlap) >= 2:
        return 0.65, "body lexical overlap"
    if task_words:
        return 0.25, "repo fallback weak match"
    return 0.8, "repo scope"


def riv_score(layer: dict[str, Any], superseded: set[str], ctx_now: str = "", task_hint: str = "") -> tuple[float, list[str]]:
    if str(layer.get("id", "")) in superseded:
        return 0.0, ["superseded"]
    base = 0.9 if is_boundary(layer) else TYPE_BASE.get(str(layer.get("type", "")), 0.4)
    why = [f"type {layer.get('type', 'unknown')}"]
    freshness, flags = _freshness(layer)
    scope, scope_reason = _scope_match(layer, ctx_now, task_hint)
    why.append(scope_reason)
    markers = set(aem_store.string_list(layer.get("markers")))
    pressure = 1.0
    if "?" in markers:
        pressure += 0.35; why.append("unresolved ?")
    if ">" in markers:
        pressure += 0.35; why.append("handoff >")
    if "!" in markers:
        pressure += 0.2; why.append("pressure !")
    if "~" in markers:
        pressure *= 0.8; why.append("tentative ~")
    severity = {"low": 0.8, "medium": 1.0, "high": 1.25}.get(str(layer.get("severity", "medium")).lower(), 1.0)
    nutrition = str(layer.get("nutrition") or nutrition_verdict(layer, [])["verdict"])
    nutrition_factor = 1.0
    if nutrition in {"transcript", "memory_shaped"}:
        nutrition_factor = 0.35
        why.append(f"low-density {nutrition}")
    elif nutrition == "questionable":
        nutrition_factor = 0.75
        why.append("questionable density")
    recurrence = len(aem_store.string_list(layer.get("recurrence_of")))
    score = base * freshness * scope * pressure * severity * nutrition_factor * (1 + 0.25 * min(recurrence, 4))
    why.extend(flags)
    return round(score, 4), why


def brief(project_root: str | Path, budget_tokens: int = 1200, task_hint: str = "", ctx_now: str = "") -> dict[str, Any]:
    layers = aem_store.read_layers(project_root)
    _live, superseded = live_ids(layers)
    scored: list[tuple[float, list[str], dict[str, Any]]] = []
    facts: list[dict[str, str]] = []
    for layer in layers:
        if str(layer.get("inherit", "posture") or "posture") == "fact":
            facts.append({"ref": str(layer.get("id", "")), "claim_hint": textwrap.shorten(str(layer.get("body", "")), width=100), "backend": "none", "freshness": f"as_of {str(layer.get('ts', 'unknown'))[:10]}"})
            continue
        score, why = riv_score(layer, superseded, ctx_now=ctx_now, task_hint=task_hint)
        if score > 0:
            scored.append((score, why, layer))
    scored.sort(key=lambda item: (-item[0], str(item[2].get("ctx", "")), str(item[2].get("id", ""))))

    floor_markers = {"?", ">"}
    # Floor unresolved/handoff layers only when they still have meaningful task
    # relevance after scoring. Otherwise a recent high-pressure incident in a
    # different domain can drown the user's current mission.
    floor = [
        item for item in scored
        if item[0] >= 0.45
        and "repo fallback weak match" not in item[1]
        and floor_markers & set(aem_store.string_list(item[2].get("markers")))
    ]
    ordered = floor + [item for item in scored if item not in floor]
    included = []
    used = 0
    omitted = 0
    ctx_counts: dict[str, int] = {}
    for score, why, layer in ordered:
        cluster = str(layer.get("ctx", "")).split("/")[0] or "root"
        if ctx_counts.get(cluster, 0) >= 4 and not (floor_markers & set(aem_store.string_list(layer.get("markers")))):
            omitted += 1
            continue
        body = str(layer.get("body", ""))
        action = str(layer.get("action_rule") or "")
        rendered = body
        fidelity = "full"
        if score < 0.55 or used + _token_estimate(rendered) > budget_tokens:
            rendered = action or textwrap.shorten(body, width=180, placeholder="…")
            fidelity = "action_rule"
        tokens = _token_estimate(rendered)
        if used + tokens > budget_tokens:
            omitted += 1
            continue
        included.append({"id": layer.get("id"), "type": layer.get("type"), "kind": layer.get("kind"), "ctx": layer.get("ctx"), "markers": aem_store.string_list(layer.get("markers")), "riv": score, "why": "; ".join(why), "fidelity": fidelity, "body": rendered, "tokens": tokens})
        used += tokens
        ctx_counts[cluster] = ctx_counts.get(cluster, 0) + 1
    return {"project_root": str(Path(project_root).expanduser().resolve()), "included": included, "floor": [str(item[2].get("id")) for item in floor], "facts_referred": facts, "superseded_count": len(superseded), "omitted_count": omitted + max(0, len(scored) - len(included) - omitted), "budget": {"requested": budget_tokens, "used": used}, "layers_sha256": _sha256(_layers_path(project_root))}


def store_health(project_root: str | Path) -> dict[str, Any]:
    layers = aem_store.read_layers(project_root)
    live, superseded = live_ids(layers)
    type_counts: dict[str, int] = {}
    nutrition_counts: dict[str, int] = {}
    lengths: dict[str, list[int]] = {}
    stale = 0
    forced = 0
    for layer in layers:
        typ = str(layer.get("type", "unknown"))
        type_counts[typ] = type_counts.get(typ, 0) + 1
        lengths.setdefault(typ, []).append(len(str(layer.get("body", ""))))
        nutrition = str(layer.get("nutrition") or nutrition_verdict(layer, [])["verdict"])
        nutrition_counts[nutrition] = nutrition_counts.get(nutrition, 0) + 1
        if layer.get("force_reason"):
            forced += 1
        _fresh, flags = _freshness(layer)
        if any("stale" in flag for flag in flags):
            stale += 1
    total = max(1, len(layers))
    bad = nutrition_counts.get("memory_shaped", 0) + nutrition_counts.get("transcript", 0)
    questionable = nutrition_counts.get("questionable", 0)
    avg_len = sum(len(str(layer.get("body", ""))) for layer in layers) / total
    density = max(0, round(100 - bad * 18 - questionable * 7 - forced * 5 - stale * 3 - max(0, (avg_len - 900) / 20), 1))
    return {"project_root": str(Path(project_root).expanduser().resolve()), "layer_count": len(layers), "live_count": len(live), "superseded_count": len(superseded), "type_counts": type_counts, "nutrition": nutrition_counts, "forced_append_count": forced, "stale_candidate_count": stale, "avg_body_length": {k: round(sum(v) / len(v), 1) for k, v in lengths.items() if v}, "density_score": density, "layers_sha256": _sha256(_layers_path(project_root))}


def _new_layer_id(existing: list[dict[str, Any]]) -> str:
    numeric = [int(str(layer.get("id"))) for layer in existing if str(layer.get("id", "")).isdigit()]
    return f"{max(numeric) + 1:04d}" if numeric else str(uuid.uuid4())


def write_layer(project_root: str | Path, *, layer_type: str, body: str, ctx: str, author: str = "hermes-aethermind-cl2", conf: float = 0.8, markers: Any = None, mode: str = "lint", force_reason: str = "", **optional: Any) -> dict[str, Any]:
    if not body:
        raise ValueError("body is required")
    if not ctx:
        raise ValueError("ctx is required")
    layers_path = _layers_path(project_root)
    existing = aem_store.read_layers(project_root) if layers_path and layers_path.exists() else []
    marker_list = aem_store.string_list(markers)
    if layer_type == "boundary":
        layer_type = "load-bearing"
        optional.setdefault("kind", "boundary")
        if "boundary" not in marker_list:
            marker_list.append("boundary")
    if layer_type not in aem_store.ALLOWED_LAYER_TYPES:
        raise ValueError(f"invalid layer_type: {layer_type}")
    layer = {"id": _new_layer_id(existing), "ts": _now_utc(), "author": author, "type": layer_type, "body": body, "ctx": ctx, "conf": float(conf), "markers": marker_list, "primitive": "layer"}
    for key, value in optional.items():
        if value not in (None, "", []):
            layer[key] = aem_store.string_list(value) if key in {"evidence", "verification", "supersedes", "rollback_of", "recurrence_of"} else value
    verdict = nutrition_verdict(layer, existing)
    layer["nutrition"] = verdict["verdict"]
    if force_reason:
        layer["force_reason"] = force_reason
    if mode in {"coach", "strict"} and verdict["verdict"] in {"memory_shaped", "transcript"} and not force_reason:
        return {"ok": False, "blocked": True, "nutrition": verdict, "layer_preview": layer, "coach": "Rewrite or resubmit with force_reason to append honestly."}
    return {**_append_layer(project_root, layer), "nutrition": verdict}


def build_capsule_body(posture: str, open_items: str, next_step: str, invalid: str) -> str:
    parts = [("POSTURE", posture), ("OPEN", open_items), ("NEXT", next_step), ("INVALID", invalid)]
    return textwrap.shorten("; ".join(f"{name}: {text.strip()}" for name, text in parts if text and text.strip()), width=900, placeholder="…")


def capsule(project_root: str | Path, *, posture: str = "", open_items: str = "", next_step: str = "", invalid: str = "", ctx: str = "boundary/capture", author: str = "hermes-aethermind-cl2", mode: str = "lint", force_reason: str = "") -> dict[str, Any]:
    body = build_capsule_body(posture, open_items, next_step, invalid)
    return write_layer(project_root, layer_type="boundary", body=body, ctx=ctx, author=author, conf=0.85, markers=[">", "?" if open_items else "!"], mode=mode, force_reason=force_reason, inherit="posture", action_rule=next_step, scope="repo", severity="high")
