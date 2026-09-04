from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from PIL import Image, ImageDraw, ImageSequence
import io

@dataclass
class RenderValues:
    clock: str
    temperature: str
    condition: str

FONT_5X7 = {
    "0": ["01110","10001","10011","10101","11001","10001","01110"],
    "1": ["00100","01100","00100","00100","00100","00100","01110"],
    "2": ["01110","10001","00001","00010","00100","01000","11111"],
    "3": ["11110","00001","00001","01110","00001","00001","11110"],
    "4": ["00010","00110","01010","10010","11111","00010","00010"],
    "5": ["11111","10000","10000","11110","00001","00001","11110"],
    "6": ["01110","10000","10000","11110","10001","10001","01110"],
    "7": ["11111","00001","00010","00100","01000","01000","01000"],
    "8": ["01110","10001","10001","01110","10001","10001","01110"],
    "9": ["01110","10001","10001","01111","00001","00001","01110"],
    ":": ["0","1","0","0","1","0","0"],
    "°": ["011","101","011","000","000","000","000"],
    "-": ["00000","00000","00000","11111","00000","00000","00000"],
    " ": ["0","0","0","0","0","0","0"],
}

FONT_3X5 = {
    "A": ["010","101","111","101","101"], "B": ["110","101","110","101","110"],
    "C": ["011","100","100","100","011"], "D": ["110","101","101","101","110"],
    "E": ["111","100","110","100","111"], "F": ["111","100","110","100","100"],
    "G": ["011","100","101","101","011"], "H": ["101","101","111","101","101"],
    "I": ["111","010","010","010","111"], "J": ["001","001","001","101","010"],
    "K": ["101","101","110","101","101"], "L": ["100","100","100","100","111"],
    "M": ["101","111","111","101","101"], "N": ["101","111","111","111","101"],
    "O": ["010","101","101","101","010"], "P": ["110","101","110","100","100"],
    "Q": ["010","101","101","111","011"], "R": ["110","101","110","101","101"],
    "S": ["011","100","010","001","110"], "T": ["111","010","010","010","010"],
    "U": ["101","101","101","101","111"], "V": ["101","101","101","101","010"],
    "W": ["101","101","111","111","101"], "X": ["101","101","010","101","101"],
    "Y": ["101","101","010","010","010"], "Z": ["111","001","010","100","111"],
    "0": ["111","101","101","101","111"], "1": ["010","110","010","010","111"],
    "2": ["110","001","010","100","111"], "3": ["110","001","010","001","110"],
    "4": ["101","101","111","001","001"], "5": ["111","100","110","001","110"],
    "6": ["011","100","111","101","111"], "7": ["111","001","010","010","010"],
    "8": ["111","101","111","101","111"], "9": ["111","101","111","001","110"],
    " ": ["0","0","0","0","0"], "-": ["000","000","111","000","000"],
}

CONDITION_LABELS = {
    "clear night": "CLEAR", "partly cloudy": "CLOUDY", "lightning rainy": "THUNDER",
    "thunderstorm": "THUNDER", "rainy": "RAIN", "rain": "RAIN", "snowy": "SNOW",
    "snow": "SNOW", "windy": "WINDY", "fog": "FOGGY", "sunny": "SUNNY",
    "extreme heat": "HOT", "freezing": "FREEZING",
}

class GifRenderer:
    def __init__(self, size: int):
        self.size = size
        self._cache = {}

    def _load(self, path: Path):
        key = (str(path), path.stat().st_mtime_ns)
        if key in self._cache:
            return self._cache[key]
        with Image.open(path) as im:
            frames = []
            durations = []
            for frame in ImageSequence.Iterator(im):
                f = frame.convert("RGB").resize((self.size, self.size), Image.Resampling.NEAREST)
                frames.append(f.copy())
                durations.append(frame.info.get("duration", im.info.get("duration", 100)))
            loop = im.info.get("loop", 0)
        self._cache = {key: (frames, durations, loop)}
        return self._cache[key]

    def render(self, path: Path, layout: dict, values: RenderValues) -> bytes:
        frames, durations, loop = self._load(path)
        out_frames = []
        condition_key = values.condition.lower().strip()
        condition_text = CONDITION_LABELS.get(condition_key, values.condition.upper().replace("_", " "))
        for base in frames:
            frame = base.copy()
            draw = ImageDraw.Draw(frame)
            self._draw_region(draw, layout["clock"], values.clock, FONT_5X7, 1)
            self._draw_region(draw, layout["temperature"], values.temperature, FONT_5X7, 1)
            self._draw_region(draw, layout["condition"], condition_text, FONT_3X5, 1)
            out_frames.append(frame)
        bio = io.BytesIO()
        out_frames[0].save(
            bio, format="GIF", save_all=True, append_images=out_frames[1:],
            duration=durations, loop=loop, disposal=2, optimize=False,
        )
        return bio.getvalue()

    @staticmethod
    def _glyph_size(pattern):
        return max(len(row) for row in pattern), len(pattern)

    def _measure(self, text, font, spacing, scale):
        widths = []
        height = 0
        for ch in text:
            glyph = font.get(ch, font.get(" "))
            gw, gh = self._glyph_size(glyph)
            widths.append(gw * scale)
            height = max(height, gh * scale)
        return sum(widths) + max(0, len(widths)-1) * spacing * scale, height

    def _draw_pixel_text(self, draw, xy, text, font, color, spacing=1, scale=1):
        cursor, y = xy
        for ch in text:
            glyph = font.get(ch, font.get(" "))
            gw, _ = self._glyph_size(glyph)
            for gy, row in enumerate(glyph):
                for gx, bit in enumerate(row):
                    if bit == "1":
                        x0 = cursor + gx * scale
                        y0 = y + gy * scale
                        draw.rectangle((x0, y0, x0 + scale - 1, y0 + scale - 1), fill=color)
            cursor += (gw + spacing) * scale

    def _draw_region(self, draw, region, text, font, glyph_spacing=1):
        x, y, w, h = (int(region[k]) for k in ("x", "y", "w", "h"))
        bg = region.get("background", [0, 0, 0])
        fg = tuple(region.get("foreground", [255, 255, 255]))
        align = region.get("align", "left")
        if bg is not None:
            draw.rectangle((x, y, x + w - 1, y + h - 1), fill=tuple(bg))

        scale = 1
        while True:
            tw, th = self._measure(text, font, glyph_spacing, scale + 1)
            if tw <= w - 2 and th <= h - 2:
                scale += 1
            else:
                break
        tw, th = self._measure(text, font, glyph_spacing, scale)
        if align == "center":
            tx = x + max(0, (w - tw) // 2)
        elif align == "right":
            tx = x + max(0, w - tw - 1)
        else:
            tx = x + 1
        ty = y + max(0, (h - th) // 2)

        # One-pixel black shadow keeps white text readable without a black bar.
        self._draw_pixel_text(draw, (tx + 1, ty + 1), text, font, (0, 0, 0), glyph_spacing, scale)
        self._draw_pixel_text(draw, (tx, ty), text, font, fg, glyph_spacing, scale)
