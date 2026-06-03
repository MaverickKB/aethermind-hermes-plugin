from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from aethermind import core


def run_cli(*args: str, cwd: Path) -> dict:
    proc = subprocess.run(
        [sys.executable, "-m", "aethermind.cli", *args],
        cwd=cwd,
        text=True,
        capture_output=True,
        check=True,
    )
    return json.loads(proc.stdout)


def test_write_reorient_export_import_round_trip(tmp_path: Path) -> None:
    project = tmp_path / "project"
    init = core.init_store(project)
    assert init["ok"] is True

    first = core.write_layer(
        project,
        layer_type="load-bearing",
        body="mission: keep continuity compact",
        ctx="test/mission",
        author="pytest",
        markers=["mission", "compact"],
    )
    second = core.write_layer(
        project,
        layer_type="friction",
        body="pressure: avoid turning layers into task logs",
        ctx="test/pressure",
        author="pytest",
        markers=["pressure"],
    )
    assert first["layer"]["id"] != second["layer"]["id"]

    report = core.evaluate_store(project)
    assert report["valid"] is True
    assert report["continuity_properties"]["pressure_capture"] is True
    assert report["warnings"] == []

    bundle = core.reorient(project, task="compact continuity mission")
    assert bundle["selected_count"] >= 1
    assert any(item["type"] == "load-bearing" for item in bundle["continuity_bundle"])

    exported = core.export_store(project)
    imported = tmp_path / "imported"
    imported_report = core.import_layers(
        imported,
        layers_aem=exported["layers_aem"],
        texture_aem=exported["texture_aem"],
    )
    assert imported_report["imported_layer_count"] == 2
    assert core.evaluate_store(imported)["valid"] is True


def test_cli_smoke_outputs_json(tmp_path: Path) -> None:
    root = tmp_path / "cli-project"
    init = run_cli("init", "--project-root", str(root), cwd=Path.cwd())
    assert init["ok"] is True

    write = run_cli(
        "write-layer",
        "--project-root",
        str(root),
        "--type",
        "load-bearing",
        "--body",
        "mission: cli smoke",
        "--ctx",
        "cli/smoke",
        "--marker",
        "smoke",
        cwd=Path.cwd(),
    )
    assert write["ok"] is True

    validate = run_cli("validate-store", "--project-root", str(root), cwd=Path.cwd())
    assert validate["valid"] is True

    export_path = tmp_path / "export.json"
    exported = run_cli("export", "--project-root", str(root), "--out", str(export_path), cwd=Path.cwd())
    assert exported["ok"] is True
    assert export_path.exists()

    imported_root = tmp_path / "imported"
    imported = run_cli("import", "--project-root", str(imported_root), "--in", str(export_path), cwd=Path.cwd())
    assert imported["ok"] is True

    manifest = run_cli("manifest", "--project-root", str(imported_root), cwd=Path.cwd())
    assert manifest["format"] == "aethermind-aem-baseline-v1"
