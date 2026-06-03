from __future__ import annotations

from pathlib import Path

from tools.scan_public_surface import scan_paths


def test_scanner_flags_private_absolute_path(tmp_path: Path) -> None:
    doc = tmp_path / "README.md"
    private_path = "/Users/" + "kbandoly/Programming/private"
    doc.write_text(f"Private path: {private_path}\n", encoding="utf-8")

    report = scan_paths([doc])

    assert report["valid"] is False
    assert report["findings"]
    assert report["findings"][0]["pattern"] == "private_path"


def test_scanner_passes_safe_public_docs(tmp_path: Path) -> None:
    doc = tmp_path / "README.public.md"
    doc.write_text("# AetherMind\n\nA continuity primitive for local project stores.\n", encoding="utf-8")

    report = scan_paths([doc])

    assert report["valid"] is True
    assert report["findings"] == []


def test_scanner_allows_marked_literal_examples(tmp_path: Path) -> None:
    doc = tmp_path / "PRIVACY.md"
    doc.write_text("literal example: /Users/example/project\n", encoding="utf-8")

    report = scan_paths([doc])

    assert report["valid"] is True


def test_scanner_flags_macos_finder_metadata(tmp_path: Path) -> None:
    metadata = tmp_path / ".DS_Store"
    metadata.write_bytes(b"metadata")

    report = scan_paths([tmp_path])

    assert report["valid"] is False
    assert report["findings"]
    assert report["findings"][0]["pattern"] == "disallowed_filename"
    assert report["findings"][0]["match"] == ".DS_Store"
