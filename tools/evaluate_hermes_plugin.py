#!/usr/bin/env python3
"""Load the AetherMind Hermes adapter and run supported tool smoke tests."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--hermes-agent-root", type=Path, required=True)
    parser.add_argument("--kit-root", type=Path, default=Path.cwd())
    args = parser.parse_args()

    hermes_root = args.hermes_agent_root.expanduser().resolve()
    kit_root = args.kit_root.expanduser().resolve()
    plugin_src = kit_root / "plugins" / "hermes" / "aethermind"
    sys.path.insert(0, str(kit_root / "src"))
    sys.path.insert(0, str(hermes_root))

    with tempfile.TemporaryDirectory(prefix="aem-hermes-plugin-") as tmp:
        home = Path(tmp) / "hermes_home"
        dst = home / "plugins" / "aethermind"
        dst.parent.mkdir(parents=True)
        shutil.copytree(plugin_src, dst)
        (home / "config.yaml").write_text("plugins:\n  enabled:\n    - aethermind\n", encoding="utf-8")
        os.environ["HERMES_HOME"] = str(home)

        from hermes_cli import plugins as plugin_mod
        from tools.registry import registry

        plugin_mod._plugin_manager = plugin_mod.PluginManager()
        plugin_mod.discover_plugins(force=True)
        loaded = plugin_mod.get_plugin_manager().list_plugins()
        work_project = Path(tmp) / "smoke_project"
        init_report = json.loads(registry.dispatch("aethermind_init_store", {"project_root": str(work_project)}))
        write_mission = json.loads(
            registry.dispatch(
                "aethermind_write_layer",
                {
                    "project_root": str(work_project),
                    "type": "load-bearing",
                    "body": "mission: prove Hermes adapter over package core",
                    "ctx": "smoke/mission",
                    "markers": ["mission", "adapter"],
                },
            )
        )
        write_pressure = json.loads(
            registry.dispatch(
                "aethermind_write_layer",
                {
                    "project_root": str(work_project),
                    "type": "friction",
                    "body": "pressure: adapter must not depend on evidence packets",
                    "ctx": "smoke/pressure",
                    "markers": ["pressure", "product-boundary"],
                },
            )
        )
        texture_report = json.loads(registry.dispatch("aethermind_write_texture", {"project_root": str(work_project), "body": "Adapter path stays thin.", "ctx": "smoke/texture", "marker": "!"}))
        read_report = json.loads(registry.dispatch("aethermind_read_layers", {"project_root": str(work_project), "ctx_prefix": "smoke/"}))
        reorient_report = json.loads(registry.dispatch("aethermind_reorient", {"project_root": str(work_project), "task": "Hermes adapter product boundary"}))
        evaluate_report = json.loads(registry.dispatch("aethermind_evaluate_store", {"project_root": str(work_project)}))
        integrity_report = json.loads(registry.dispatch("aethermind_integrity_manifest", {"project_root": str(work_project)}))
        export_report = json.loads(registry.dispatch("aethermind_export_store", {"project_root": str(work_project)}))
        import_project = Path(tmp) / "imported_project"
        import_report = json.loads(registry.dispatch("aethermind_import_layers", {"project_root": str(import_project), "layers_aem": export_report["layers_aem"], "texture_aem": export_report["texture_aem"]}))
        imported_evaluate_report = json.loads(registry.dispatch("aethermind_evaluate_store", {"project_root": str(import_project)}))

        registered = sorted(
            name
            for name in (
                "aethermind_init_store",
                "aethermind_write_layer",
                "aethermind_read_layers",
                "aethermind_write_texture",
                "aethermind_read_texture",
                "aethermind_reorient",
                "aethermind_export_store",
                "aethermind_import_layers",
                "aethermind_integrity_manifest",
                "aethermind_evaluate_store",
            )
            if name in registry._tools
        )

    report = {
        "plugin_loaded": any(item["key"] == "aethermind" and item["enabled"] for item in loaded),
        "registered_tools": registered,
        "init_report": init_report,
        "write_reports": [write_mission, write_pressure],
        "texture_report": texture_report,
        "read_report": read_report,
        "reorient_report": reorient_report,
        "evaluate_report": evaluate_report,
        "integrity_report": integrity_report,
        "export_format": export_report["format"],
        "import_report": import_report,
        "imported_evaluate_report": imported_evaluate_report,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    passed = (
        report["plugin_loaded"]
        and len(report["registered_tools"]) == 10
        and evaluate_report["valid"]
        and imported_evaluate_report["valid"]
        and integrity_report["layer_count"] == import_report["imported_layer_count"]
        and export_report["format"] == "aethermind-aem-baseline-v1"
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
