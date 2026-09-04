from __future__ import annotations

from pathlib import Path
import hashlib
import json
import tempfile
import zipfile

from .const import CONDITION_ALIASES, DEFAULT_LAYOUT


class AnimationPack:
    def __init__(self, path: str, size: int):
        source = Path(path)
        self.size = size

        if source.suffix.lower() == ".zip":
            digest = hashlib.sha1(str(source.resolve()).encode()).hexdigest()[:12]
            extracted = Path(tempfile.gettempdir()) / "idm_weather_matrix" / digest
            marker = extracted / ".ready"
            if not marker.exists():
                extracted.mkdir(parents=True, exist_ok=True)
                with zipfile.ZipFile(source, "r") as archive:
                    archive.extractall(extracted)
                marker.write_text("ok", encoding="utf-8")
            self.path = extracted
        else:
            self.path = source

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
