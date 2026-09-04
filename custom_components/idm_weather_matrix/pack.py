from __future__ import annotations

from pathlib import Path
import json

from .const import CONDITION_ALIASES, DEFAULT_LAYOUT


class AnimationPack:
    def __init__(self, path: str, size: int):
        self.path = Path(path)
        self.size = size
        self.manifest = {}
        manifest = self.path / "manifest.json"
        if manifest.exists():
            self.manifest = json.loads(manifest.read_text(encoding="utf-8"))

        self.layout = self.manifest.get("layout", DEFAULT_LAYOUT)
        self.animations = self.manifest.get("animations", {})

    def animation_for(self, condition: str) -> Path:
        key = CONDITION_ALIASES.get(condition, condition or "default")
        filename = self.animations.get(key, f"{key}.gif")
        candidate = self.path / filename
        if candidate.exists():
            return candidate

        default_name = self.animations.get("default", "default.gif")
        default = self.path / default_name
        if default.exists():
            return default

        raise FileNotFoundError(
            f"No animation for '{condition}' and no default.gif in {self.path}"
        )
