"""AetherMind Hermes plugin."""

from __future__ import annotations

import json
import os
import sys
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
    optional_fields = {
        key: args[key]
        for key in (
            "thread_key", "supersedes", "rollback_of", "corrects",
            "recurrence_of", "next", "artifact", "artifact_ref", "anchor", "ref",
            "kind", "label", "host", "repo_root", "content_id", "selector",
            "span_hint", "domain", "symptom", "next_verification",
            "suspected_mechanism", "scope", "severity", "owner_hint",
            "repair", "reason", "replacement", "restored_to", "inline",
            "remote_target", "local_store_reason", "source_tool", "store_kind",
        )
        if key in args and args[key] is not None
    }
    return _json(
        aem_store.write_layer(
            str(args["project_root"]),
            layer_type=str(args["type"]),
            body=str(args["body"]),
            ctx=str(args["ctx"]),
            author=str(args.get("author") or "hermes-aethermind-plugin"),
            conf=args.get("conf", 1.0),
            markers=args.get("markers"),
            evidence=args.get("evidence"),
            verification=args.get("verification"),
            primitive=str(args.get("primitive") or "layer"),
            **optional_fields,
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
            since_ts=str(args.get("since_ts") or ""),
            last_n=int(args["last_n"]) if args.get("last_n") is not None else None,
            markers_any=args.get("markers_any"),
        )
    )


def _write_texture_handler(args: dict[str, Any], **_kwargs: Any) -> str:
    return _json(
        aem_store.write_texture(
            str(args["project_root"]),
            body=str(args["body"]),
            ctx=str(args.get("ctx") or ""),
            marker=str(args.get("marker") or ""),
            author=str(args.get("author") or "hermes-aethermind-plugin"),
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


# --- Anchor-scoped deterministic read contract (added 2026-08-05) ---
# The live local deployment now uses the deterministic anchor-scoped brief,
# hash-chain audit, and gate contract. When the canonical core is available on
# this host (Programming/AetherMind/lib), these handlers route through it so
# every running surface shares the SAME read contract. Fall back to the
# bundled reader only when the canonical core is absent.

def _canonical_core() -> Any | None:
    """Resolve the canonical core by file path, never by bare package name.

    The plugin package itself is named ``aethermind``, so ``from aethermind
    import AetherMind`` would resolve to THIS plugin and return None. Load the
    canonical core from its resolved ``core.py`` under a unique module name so
    the read-contract handlers share the SAME code as the running MCP.
    """
    import importlib.util

    candidates = [
        os.environ.get("AETHERMIND_LIB"),
        str(Path.home() / "Programming" / "AetherMind" / "lib"),
    ]
    for candidate in candidates:
        if not candidate:
            continue
        path = Path(candidate).expanduser()
        core_path = path / "aethermind" / "core.py"
        if not core_path.exists():
            continue
        module_name = f"_aethermind_canonical_core_{abs(hash(str(core_path)))}"
        if module_name in sys.modules:
            return sys.modules[module_name].AetherMind
        try:
            spec = importlib.util.spec_from_file_location(module_name, core_path)
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            return getattr(module, "AetherMind", None)
        except Exception:
            return None
    return None


def _layer_dict(layer: Any) -> dict[str, Any]:
    return {
        "id": getattr(layer, "id", None),
        "ts": getattr(layer, "ts", None),
        "type": getattr(layer, "type", None),
        "ctx": getattr(layer, "ctx", None),
        "body": getattr(layer, "body", None),
        "conf": getattr(layer, "conf", None),
        "markers": list(getattr(layer, "markers", []) or []),
        "corrects": list(getattr(layer, "corrects", []) or []),
        "prev_hash": getattr(layer, "prev_hash", None),
    }


def _brief_anchor_handler(args: dict[str, Any], **_kwargs: Any) -> str:
    root = str(args["project_root"])
    anchor = str(args.get("anchor") or "")
    budget = int(args.get("budget") or 4000)
    as_of = str(args.get("as_of") or "") or None
    core = _canonical_core()
    if core is not None:
        try:
            aether = core(root, create=False)
            brief = aether.brief_anchor(anchor=anchor or None, budget=budget, as_of=as_of)
            return _json({
                "source": "canonical-core",
                "anchor": brief["anchor"],
                "must_know": brief["must_know"],
                "unabsorbed_debt": brief["unabsorbed_debt"],
                "kept": [_layer_dict(layer) for layer in brief["kept"]],
                "tombstones": brief["tombstones"],
                "budget": brief["budget"],
                "budget_used": brief["budget_used"],
                "layer_count": brief["layer_count"],
                "determinism_key": brief["determinism_key"],
            })
        except Exception as exc:
            return _json({"source": "canonical-core", "error": f"{type(exc).__name__}: {exc}"})
    # Fallback: bundled reader query filtered by anchor.
    layers = aem_store.query_layers(root, ctx_prefix=anchor, limit=budget)
    return _json({"source": "bundled-fallback", "kept": layers, "tombstones": []})


def _audit_handler(args: dict[str, Any], **_kwargs: Any) -> str:
    root = str(args["project_root"])
    core = _canonical_core()
    if core is not None:
        try:
            aether = core(root, create=False)
            return _json({"source": "canonical-core", **aether.audit()})
        except Exception as exc:
            return _json({"source": "canonical-core", "error": f"{type(exc).__name__}: {exc}"})
    manifest = aem_store.integrity_manifest(root)
    return _json({"source": "bundled-fallback", "manifest": manifest})


def _gate_check_handler(args: dict[str, Any], **_kwargs: Any) -> str:
    root = str(args["project_root"])
    anchor = str(args.get("anchor") or "")
    enforce = bool(args.get("enforce_gate") or False)
    core = _canonical_core()
    if core is not None:
        try:
            aether = core(root, create=False)
            # Accept both contracts: a structured plan object (v0.2.0 shape) or flat
            # anchor/planned_type/planned_ctx/enforce_gate args (original shape).
            plan = args.get("plan") if isinstance(args.get("plan"), dict) else None
            if plan is None:
                plan = {
                    "anchor": anchor or None,
                    "planned_type": str(args.get("planned_type") or "layer"),
                    "planned_ctx": str(args.get("planned_ctx") or ""),
                    "enforce_gate": enforce,
                }
            return _json({"source": "canonical-core", **aether.gate_check(plan, anchor=anchor or None)})
        except Exception as exc:
            return _json({"source": "canonical-core", "error": f"{type(exc).__name__}: {exc}"})
    return _json({"source": "bundled-fallback", "verdict": "advisory", "must_know": []})


# The launch surface is the user's home directory on every host that runs
# this profile (Mac and Jarvis alike); project stores never live there.
LAUNCH_DIRS = {str(Path.home())}
REQUIRED_CLI_MCP = (
    "aethermind",
    "aethermind_jarvis",
    "aethermind_atlas",
    "cairn_world_state",
    "ember-helmet",
    "mesh",
    "shared_context",
    "wallclock",
)


def _is_launch_directory(root: Path) -> bool:
    try:
        resolved = str(root.expanduser().resolve())
    except OSError:
        return False
    return resolved in LAUNCH_DIRS


def _hermes_profile_config_path() -> Path:
    hermes_home = os.environ.get("HERMES_HOME") or ""
    if hermes_home:
        return Path(hermes_home).expanduser() / "config.yaml"
    return Path.home() / ".hermes" / "config.yaml"


def _ensure_cli_continuity_mcp() -> None:
    """Keep desktop/cli MCP allowlist from dropping continuity servers.

    If platform_toolsets.cli names any MCP server, Hermes treats that list as
    an allowlist and silently omits every other enabled MCP server. Hermes
    updates and `hermes tools` saves freeze that list. Re-add the Cairn
    continuity servers when they are missing. Do not rewrite the rest of
    the file.
    """
    config_path = _hermes_profile_config_path()
    if not config_path.is_file():
        return
    try:
        original = config_path.read_text(encoding="utf-8")
    except OSError:
        return
    lines = original.splitlines(keepends=True)
    platform_index = None
    for index, line in enumerate(lines):
        if line.rstrip("\n") == "platform_toolsets:":
            platform_index = index
            break
    if platform_index is None:
        return
    cli_index = None
    scan = platform_index + 1
    while scan < len(lines):
        stripped = lines[scan].rstrip("\n")
        if stripped and not stripped.startswith(" ") and not stripped.startswith("\t"):
            break
        if stripped == "  cli:":
            cli_index = scan
            break
        scan += 1
    if cli_index is None:
        return
    entry_start = cli_index + 1
    entry_end = entry_start
    present = []
    while entry_end < len(lines):
        stripped = lines[entry_end].rstrip("\n")
        if stripped.startswith("    - "):
            present.append(stripped[6:].strip())
            entry_end += 1
            continue
        break
    missing = []
    for name in REQUIRED_CLI_MCP:
        if name not in present:
            missing.append(name)
    if not missing:
        return
    insert_at = entry_end
    new_lines = []
    for name in missing:
        new_lines.append(f"    - {name}\n")
    updated = "".join(lines[:insert_at] + new_lines + lines[insert_at:])
    backup_path = config_path.with_name(config_path.name + ".continuity-heal.bak")
    try:
        if not backup_path.exists():
            backup_path.write_text(original, encoding="utf-8")
        config_path.write_text(updated, encoding="utf-8")
    except OSError:
        return


def _capabilities_handler(args: dict[str, Any], **_kwargs: Any) -> str:
    return _json(aem_store.runtime_capabilities(str(args["project_root"])))


def _currentness_handler(args: dict[str, Any], **_kwargs: Any) -> str:
    return _json(
        aem_store.currentness(
            str(args["project_root"]), as_of=args.get("as_of")
        )
    )


def _brief_handler(args: dict[str, Any], **_kwargs: Any) -> str:
    return _json(
        aem_store.brief(str(args["project_root"]), as_of=args.get("as_of"))
    )


def _write_event_handler(args: dict[str, Any], **_kwargs: Any) -> str:
    return _json(
        aem_store.write_event(
            str(args["project_root"]),
            event_type=str(args["type"]),
            body=str(args["body"]),
            ctx=str(args["ctx"]),
            author=str(args.get("author") or "hermes-aethermind-plugin"),
        )
    )


def _read_events_handler(args: dict[str, Any], **_kwargs: Any) -> str:
    return _json(aem_store.read_events(str(args["project_root"])))


def _archive_handler(args: dict[str, Any], **_kwargs: Any) -> str:
    return _json(
        aem_store.archive(
            str(args["project_root"]),
            layer_ids=[str(value) for value in args["layer_ids"]],
            reason=str(args.get("reason") or ""),
        )
    )


def _hook_project_root(kwargs: dict[str, Any]) -> Path | str:
    raw = (
        kwargs.get("project_root")
        or os.environ.get("AETHERMIND_PROJECT_ROOT")
        or os.environ.get("HERMES_PROJECT_ROOT")
        or os.getcwd()
    )
    raw = str(raw)
    if raw.startswith(aem_store.REMOTE_PREFIX):
        return raw
    resolved = Path(raw).expanduser().resolve()
    # Desktop Hermes lives under ~/.hermes, and the hook payload stamps that
    # process directory as cwd. The chat UI's home directory never arrives.
    # Treat the Hermes install, and any directory inside it, as the user's home.
    install = _hermes_profile_config_path().parent.resolve()
    shared_home = Path.home() / ".hermes"
    try:
        shared_home = shared_home.resolve()
    except OSError:
        pass
    if resolved == install or install in resolved.parents or resolved == shared_home or shared_home in resolved.parents:
        # Cairn continuity is the one Jarvis ledger, not a Mac directory beside
        # the home folder. The store path is deliberate infrastructure on the
        # Jarvis host (not the client's home), so it is built from parts to keep
        # personal path literals out of the public source; override with
        # AETHERMIND_REMOTE_STORE when the store moves.
        remote_store_home = "/hom" + "e/master"
        return aem_store.REMOTE_PREFIX + os.environ.get(
            "AETHERMIND_REMOTE_STORE",
            remote_store_home + "/.local/share/aethermind-cloud/projects/personal",
        )
    return resolved


def _is_launch_root(root: Any) -> bool:
    if not isinstance(root, Path):
        # Remote canonical roots (jarvis:...) are never the launch directory.
        return False
    return _is_launch_directory(root)


def _tree_brief_if_available(root: Path | str) -> str | None:
    """Return the whole-store tree brief when the project has a summary tree.

    The one-tree trunk (canonical store on Jarvis) renders through the Jarvis
    MCP when the root is remote (jarvis:...). Local roots render from their
    derived tree.aem through the canonical engine. Project stores without a
    tree keep the legacy CL2 brief path so nothing else changes.
    """
    budget = int(os.environ.get("AETHERMIND_TREE_BUDGET", "3600") or "3600")
    if aem_store.is_remote(root):
        try:
            payload = aem_store.remote_call(root, "view", {"budget_chars": budget})
        except Exception:
            return None
        if not payload.get("success"):
            return None
        view = payload.get("view", "")
        return (
            f"{view}\n"
            f"[tree brief: {payload.get('est_tokens')}/900 est. tokens, "
            f"{payload.get('chars')} chars, deterministic from tree.aem]"
        )
    tree_path = root / ".aethermind" / "tree.aem"
    if not tree_path.exists():
        return None
    budget = int(os.environ.get("AETHERMIND_TREE_BUDGET", "3600") or "3600")
    lib_path = os.environ.get(
        "AETHERMIND_LIB_PATH",
        str(Path.home() / "Programming" / "AetherMind" / "lib"),
    )
    try:
        if lib_path not in sys.path:
            sys.path.insert(0, lib_path)
        from aethermind.view import render_view, view_cost

        text = render_view(str(root), budget_chars=budget)
        cost = view_cost(text)
        return (
            f"{text}\n"
            f"[tree brief: {cost['est_tokens']}/900 est. tokens, {cost['chars']} chars, "
            f"deterministic from tree.aem]"
        )
    except Exception:
        pass
    try:
        import subprocess

        script = (
            "import sys, json; sys.path.insert(0, %r); "
            "from aethermind.view import render_view, view_cost; "
            "text = render_view(%r, budget_chars=%d); "
            "print(json.dumps({'text': text, **view_cost(text)}))"
            % (lib_path, str(root), budget)
        )
        result = subprocess.run(
            [sys.executable, "-c", script], capture_output=True, text=True, timeout=120
        )
        if result.returncode != 0:
            return None
        payload = json.loads(result.stdout.strip().splitlines()[-1])
        return (
            f"{payload['text']}\n"
            f"[tree brief: {payload['est_tokens']}/900 est. tokens, {payload['chars']} chars, "
            f"deterministic from tree.aem]"
        )
    except Exception:
        return None


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
    if _is_launch_root(root):
        return
    aem_store.init_store(root)


def _aethermind_pre_llm_call(**kwargs: Any) -> dict[str, str] | None:
    root = _hook_project_root(kwargs)
    if _is_launch_root(root):
        return None
    user_message = str(kwargs.get("user_message") or "")
    try:
        aem_store.init_store(root)
        tree_brief = _tree_brief_if_available(root)
        if tree_brief is not None:
            tree_budget = int(os.environ.get("AETHERMIND_TREE_BUDGET", "3600") or "3600")
            body_section = (
                "Whole-store tree brief (deterministic from tree.aem; walk deeper with the "
                "aethermind view and zoom MCP tools):\n" + tree_brief
            )
            budget_line = f"Tree brief budget: {tree_budget} chars."
            context = (
                "[AetherMind CL2 automatic continuity is active]\n"
                f"Project root for AetherMind tools: {root}\n"
                f"{budget_line}\n"
                "The store was initialized/read before this model call. The tree brief covers "
                "every record coarsely, must-know corrections in full, and the newest records; "
                "it is not a substitute for reading complete corrections before using them. "
                "When the turn produces a load-bearing decision, correction, discovery, friction, "
                "or uncertainty, write a compact layer and texture pointer. "
                "Do not write secrets, credentials, raw transcripts, or private prompt text.\n"
                f"{body_section}\n"
                "[/AetherMind CL2 automatic continuity]"
            )
            return {"context": context}
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
                "next": TEXT_ARRAY,
                "primitive": {
                    "type": "string",
                    "enum": sorted(aem_store.ALLOWED_LIGHT_PRIMITIVES),
                },
                "thread_key": {"type": "string"},
                "supersedes": TEXT_ARRAY,
                "rollback_of": TEXT_ARRAY,
                "corrects": TEXT_ARRAY,
                "recurrence_of": TEXT_ARRAY,
                "artifact": {"type": "string"},
                "artifact_ref": {"type": "string"},
                "anchor": {"type": "string"},
                "ref": {"type": "string"},
                "kind": {"type": "string"},
                "label": {"type": "string"},
                "host": {"type": "string"},
                "repo_root": {"type": "string"},
                "content_id": {"type": "string"},
                "selector": {"type": "string"},
                "span_hint": {"type": "string"},
                "domain": {"type": "string"},
                "symptom": {"type": "string"},
                "next_verification": {"type": "string"},
                "suspected_mechanism": {"type": "string"},
                "scope": {"type": "string"},
                "severity": {"type": "string"},
                "owner_hint": {"type": "string"},
                "repair": {"type": "string"},
                "reason": {"type": "string"},
                "replacement": {"type": "string"},
                "restored_to": {"type": "string"},
                "remote_target": {"type": "string"},
                "local_store_reason": {"type": "string"},
                "source_tool": {"type": "string"},
                "store_kind": {"type": "string"},
                "inline": {"type": "boolean"},
            },
            ["project_root", "type", "body", "ctx"],
        ),
        _write_layer_handler,
    ),
    (
        "aethermind_read_layers",
        "Search AetherMind layers by text. text matches body, context, and markers. A jarvis: root reads the remote store. Any other root is a local file, and a missing file is an error, not an empty result.",
        _object_schema(
            {
                **PROJECT_ROOT,
                "ctx_prefix": {"type": "string"},
                "type": {"type": "string"},
                "marker": {"type": "string"},
                "author": {"type": "string"},
                "text": {"type": "string"},
                "limit": {"type": "integer", "default": 20},
                "since_ts": {"type": "string"},
                "last_n": {"type": "integer"},
                "markers_any": TEXT_ARRAY,
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
                "author": {"type": "string"},
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
        "Export the AEM store contents through the tool response.",
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
    (
        "aethermind_capabilities",
        "Return the AetherMind runtime identity, format, and methods.",
        _object_schema(PROJECT_ROOT, ["project_root"]),
        _capabilities_handler,
    ),
    (
        "aethermind_currentness",
        "Return active heads and inactive lineage without rewriting history.",
        _object_schema(
            {**PROJECT_ROOT, "as_of": {"type": "string"}}, ["project_root"]
        ),
        _currentness_handler,
    ),
    (
        "aethermind_brief",
        "Return the current scoped continuity brief.",
        _object_schema(
            {**PROJECT_ROOT, "as_of": {"type": "string"}}, ["project_root"]
        ),
        _brief_handler,
    ),
    (
        "aethermind_brief_anchor",
        "Read contract: anchor-scoped deterministic brief with must-know corrections, unabsorbed debt, tombstones, and a determinism key. Same ledger + same budget = byte-identical output.",
        _object_schema(
            {
                **PROJECT_ROOT,
                "anchor": {"type": "string"},
                "budget": {"type": "integer", "minimum": 0, "default": 4000},
                "as_of": {"type": "string"},
            },
            ["project_root"],
        ),
        _brief_anchor_handler,
    ),
    (
        "aethermind_audit",
        "Read contract: scan the ledger hash chain and report integrity (chain breaks, legacy prefix, chain start).",
        _object_schema(PROJECT_ROOT, ["project_root"]),
        _audit_handler,
    ),
    (
        "aethermind_gate_check",
        "Check a proposed mutation against must-know corrections. Accepts a structured plan object or flat anchor/planned_type/planned_ctx/enforce_gate args. Advisory by default; enforce_gate=true rejects when unabsorbed corrections block.",
        _object_schema(
            {
                **PROJECT_ROOT,
                "plan": {"type": "object"},
                "anchor": {"type": "string"},
                "planned_type": {"type": "string", "default": "layer"},
                "planned_ctx": {"type": "string"},
                "enforce_gate": {"type": "boolean", "default": False},
            },
            ["project_root"],
        ),
        _gate_check_handler,
    ),
    (
        "aethermind_write_event",
        "Append a routine observation to events.aem.",
        _object_schema(
            {
                **PROJECT_ROOT,
                "type": {"type": "string"},
                "body": {"type": "string"},
                "ctx": {"type": "string"},
                "author": {"type": "string"},
            },
            ["project_root", "type", "body", "ctx"],
        ),
        _write_event_handler,
    ),
    (
        "aethermind_read_events",
        "Read routine observations from events.aem.",
        _object_schema(PROJECT_ROOT, ["project_root"]),
        _read_events_handler,
    ),
    (
        "aethermind_archive",
        "Copy selected layers to archive.aem and append a tombstone to layers.aem.",
        _object_schema(
            {
                **PROJECT_ROOT,
                "layer_ids": TEXT_ARRAY,
                "reason": {"type": "string"},
            },
            ["project_root", "layer_ids"],
        ),
        _archive_handler,
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
    # Companion owns companion delivery. It must not disable AetherMind CL2
    # injection; those are different channels.
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
    _ensure_cli_continuity_mcp()
    _register_hooks(ctx)
