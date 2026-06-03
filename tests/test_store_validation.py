from __future__ import annotations

from pathlib import Path

from aethermind import core


def write_layers(path: Path, text: str) -> None:
    aem = path / ".aethermind"
    aem.mkdir(parents=True)
    (aem / "layers.aem").write_text(text, encoding="utf-8")
    (aem / "texture.aem").write_text("", encoding="utf-8")


def layer_text(**overrides: object) -> str:
    data = {
        "id": '"001"',
        "ts": '"2026-06-03T00:00:00Z"',
        "author": '"pytest"',
        "type": '"load-bearing"',
        "body": '"mission: test"',
        "ctx": '"test/ctx"',
        "conf": "1.0",
        "markers": '["test"]',
    }
    for key, value in overrides.items():
        if value is None:
            data.pop(key, None)
        else:
            data[key] = str(value)
    return "[[layer]]\n" + "\n".join(f"{k} = {v}" for k, v in data.items()) + "\n"


def test_validation_fails_missing_required_field(tmp_path: Path) -> None:
    write_layers(tmp_path, layer_text(body=None))
    report = core.evaluate_store(tmp_path)
    assert report["valid"] is False
    assert any("missing required fields" in err for err in report["errors"])


def test_validation_fails_invalid_layer_type(tmp_path: Path) -> None:
    write_layers(tmp_path, layer_text(type='"memory"'))
    report = core.evaluate_store(tmp_path)
    assert report["valid"] is False
    assert any("invalid type" in err for err in report["errors"])


def test_validation_fails_duplicate_id(tmp_path: Path) -> None:
    write_layers(tmp_path, layer_text() + layer_text(ctx='"test/other"'))
    report = core.evaluate_store(tmp_path)
    assert report["valid"] is False
    assert any("duplicate layer id" in err for err in report["errors"])


def test_validation_fails_marker_not_array(tmp_path: Path) -> None:
    write_layers(tmp_path, layer_text(markers='"test"'))
    report = core.evaluate_store(tmp_path)
    assert report["valid"] is False
    assert any("markers" in err for err in report["errors"])


def test_validation_fails_conf_out_of_range(tmp_path: Path) -> None:
    write_layers(tmp_path, layer_text(conf="1.5"))
    report = core.evaluate_store(tmp_path)
    assert report["valid"] is False
    assert any("conf" in err for err in report["errors"])


def test_validation_fails_private_path_in_body(tmp_path: Path) -> None:
    private_path = "/Users/" + "localuser/private"
    write_layers(tmp_path, layer_text(body=repr(f"operator path {private_path}")))
    report = core.evaluate_store(tmp_path)
    assert report["valid"] is False
    assert any("privacy scan" in err for err in report["errors"])


def test_density_warnings_do_not_fail_store(tmp_path: Path) -> None:
    long_body = " ".join(["routine"] * 90)
    write_layers(tmp_path, layer_text(body=repr(long_body)))
    report = core.evaluate_store(tmp_path)
    assert report["valid"] is True
    assert any("long body" in warning for warning in report["warnings"])
