"""Root Hermes plugin entry point for GitHub installs."""

from __future__ import annotations

from pathlib import Path
import sys

_PLUGIN_ROOT = Path(__file__).resolve().parent
_SRC = _PLUGIN_ROOT / "src"
if _SRC.exists():
    sys.path.insert(0, str(_SRC))

from aethermind.hermes_plugin import register as _register_tools  # noqa: E402


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
    skills_dir = _PLUGIN_ROOT / "skills"
    if not skills_dir.is_dir():
        return
    for child in sorted(skills_dir.iterdir()):
        skill_md = child / "SKILL.md"
        if child.is_dir() and skill_md.exists():
            register_skill(child.name, skill_md, _skill_description(skill_md))


def register(ctx) -> None:
    _register_tools(ctx)
    _register_skills(ctx)
