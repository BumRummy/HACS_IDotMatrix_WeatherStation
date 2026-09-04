from __future__ import annotations

from pathlib import Path
import json
from PIL import Image, ImageDraw

SCENES = (
    "sunny", "partly_cloudy", "cloudy", "rain", "thunderstorm",
    "snow", "windy", "fog", "clear_night", "extreme_heat", "freezing", "default"
)

PACK_VERSION = "v2_fullscreen"


def _giraffe(draw: ImageDraw.ImageDraw, ox: int = -7, oy: int = 0, scarf: bool = False) -> None:
    yellow = (255, 184, 0)
    brown = (116, 61, 16)
    white = (250, 250, 250)
    black = (5, 5, 5)
    red = (220, 20, 35)

    draw.rectangle((27+ox, 27+oy, 36+ox, 53+oy), fill=yellow)
    draw.rectangle((23+ox, 44+oy, 43+ox, 55+oy), fill=yellow)
    draw.rectangle((24+ox, 15+oy, 42+ox, 31+oy), fill=yellow)
    draw.rectangle((38+ox, 21+oy, 50+ox, 29+oy), fill=yellow)
    draw.rectangle((20+ox, 17+oy, 25+ox, 21+oy), fill=yellow)
    draw.rectangle((42+ox, 17+oy, 47+ox, 21+oy), fill=yellow)
    draw.line((28+ox, 16+oy, 27+ox, 10+oy), fill=brown, width=2)
    draw.line((38+ox, 16+oy, 39+ox, 10+oy), fill=brown, width=2)
    draw.rectangle((26+ox, 9+oy, 29+ox, 12+oy), fill=brown)
    draw.rectangle((38+ox, 9+oy, 41+ox, 12+oy), fill=brown)

    for x, y in ((27,18),(35,17),(31,25),(40,25),(28,34),(34,39),(29,48),(39,49)):
        draw.rectangle((x+ox, y+oy, x+2+ox, y+2+oy), fill=brown)

    draw.rectangle((34+ox, 19+oy, 37+ox, 22+oy), fill=white)
    draw.point((36+ox, 21+oy), fill=black)
    draw.line((41+ox, 27+oy, 46+ox, 27+oy), fill=brown)
    draw.point((47+ox, 26+oy), fill=brown)
    draw.rectangle((26+ox, 54+oy, 30+ox, 58+oy), fill=brown)
    draw.rectangle((39+ox, 54+oy, 43+ox, 58+oy), fill=brown)

    if scarf:
        draw.rectangle((24+ox, 31+oy, 40+ox, 35+oy), fill=red)
        draw.rectangle((27+ox, 35+oy, 30+ox, 45+oy), fill=red)


def _scene(name: str, frame: int) -> Image.Image:
    im = Image.new("RGB", (64, 64), (2, 4, 9))
    d = ImageDraw.Draw(im)

    if name in ("sunny", "partly_cloudy", "cloudy", "default"):
        d.rectangle((0, 0, 63, 63), fill=(5, 24, 55))
        if name != "cloudy":
            cx, cy = 54, 18
            r = 5 + (1 if frame % 4 == 1 else 0)
            d.ellipse((cx-r, cy-r, cx+r, cy+r), fill=(255, 197, 0))
            for dx, dy in ((0,-9),(0,9),(-9,0),(9,0),(-6,-6),(6,6),(-6,6),(6,-6)):
                px, py = cx+dx, cy+dy
                if 0 <= px < 64 and 0 <= py < 64:
                    d.point((px, py), fill=(255, 220, 50))
        if name in ("partly_cloudy", "cloudy"):
            for x, y in ((7,17),(14,16),(22,18),(44,34),(51,32),(58,34)):
                d.ellipse((x-4,y-2,x+5,y+3), fill=(235,235,235))
        _giraffe(d)

    elif name == "rain":
        d.rectangle((0, 0, 63, 63), fill=(3, 16, 32))
        d.pieslice((11, 7, 49, 33), 180, 360, fill=(238, 36, 45))
        d.line((30, 20, 30, 50), fill=(210,210,210), width=1)
        d.arc((27, 46, 35, 55), 0, 180, fill=(210,210,210))
        _giraffe(d, oy=5)
        for i in range(16):
            x = (i * 9 + frame * 3) % 64
            y = (i * 7 + frame * 4) % 64
            d.line((x, y, max(0,x-1), min(63,y+2)), fill=(0, 205, 255))

    elif name == "thunderstorm":
        d.rectangle((0, 0, 63, 63), fill=(4, 7, 13))
        for x in (8, 18, 47, 57):
            d.ellipse((x-7, 8, x+7, 17), fill=(115,115,125))
        _giraffe(d)
        if frame in (1, 2):
            d.line((54,18,48,29,53,29,46,43), fill=(255,225,0), width=2)
        for i in range(10):
            x = (i*11 + frame*2) % 64
            y = 18 + ((i*8 + frame*4) % 43)
            d.line((x,y,max(0,x-1),min(63,y+2)), fill=(90,120,150))

    elif name == "snow":
        d.rectangle((0, 0, 63, 63), fill=(5, 22, 48))
        _giraffe(d, scarf=True)
        for i in range(20):
            x = (i*13 + frame*2) % 64
            y = (i*9 + frame*2) % 64
            d.point((x,y), fill=(250,250,255))
            if i % 4 == 0 and 1 <= x <= 62:
                d.line((x-1,y,x+1,y), fill=(250,250,255))

    elif name == "windy":
        d.rectangle((0, 0, 63, 63), fill=(5, 25, 45))
        _giraffe(d, ox=-4)
        for row in range(5):
            y = 7 + row*11
            shift = (frame*3 + row*5) % 15
            d.arc((2+shift,y,31+shift,y+8), 190, 345, fill=(230,245,255))
        for i in range(5):
            x = 6 + ((i*15 + frame*4) % 54)
            y = 8 + i*10
            d.line((x,y,x+4,y+2), fill=(90,200,45), width=2)

    elif name == "fog":
        d.rectangle((0, 0, 63, 63), fill=(55, 58, 60))
        d.polygon((4,58,13,14,22,58), fill=(25,30,28))
        d.polygon((43,58,53,10,63,58), fill=(25,30,28))
        _giraffe(d, oy=2)
        for row in range(6):
            y = 12 + row*8
            shift = (frame*2 + row*3) % 10
            d.line((0+shift,y,48+shift,y), fill=(165,165,165), width=2)

    elif name == "clear_night":
        d.rectangle((0, 0, 63, 63), fill=(1, 7, 20))
        d.ellipse((48,7,61,20), fill=(238,238,225))
        _giraffe(d)
        for i in range(14):
            x = 3 + (i*17 % 58)
            y = 3 + (i*11 % 56)
            if (i + frame) % 3 != 0:
                d.point((x,y), fill=(255,215,35))

    elif name == "extreme_heat":
        d.rectangle((0, 0, 63, 63), fill=(88, 15, 4))
        d.ellipse((48,6,62,20), fill=(255,175,0))
        _giraffe(d)
        for i in range(7):
            x = 7 + i*8
            y = 12 + ((i*5 + frame*3) % 42)
            d.point((x,y), fill=(0,195,255))
            if y < 63:
                d.point((x,y+1), fill=(0,150,225))
        for x in (15, 42):
            d.arc((x,36-frame%3,x+8,51-frame%3), 180, 350, fill=(255,80,0))

    elif name == "freezing":
        d.rectangle((0, 0, 63, 63), fill=(3, 15, 35))
        _giraffe(d, scarf=True)
        for i in range(18):
            x = (i*13 + frame) % 64
            y = (i*7 + frame*2) % 64
            d.point((x,y), fill=(240,250,255))
        for p in range(3):
            bx = 45 + ((frame + p*2) % 10)
            by = 27 - p
            d.point((min(62,bx),by), fill=(225,245,255))

    return im


def ensure_builtin_pack(base_dir: Path) -> Path:
    out = base_dir / "idm_weather_matrix" / "giraffe_default"
    marker = out / f".{PACK_VERSION}_ready"
    if marker.exists():
        return out

    out.mkdir(parents=True, exist_ok=True)
    # Force replacement of old cached artwork after an integration update.
    for old in out.glob("*.gif"):
        old.unlink(missing_ok=True)
    (out / "manifest.json").unlink(missing_ok=True)
    for old_marker in out.glob(".*_ready"):
        old_marker.unlink(missing_ok=True)

    for name in SCENES:
        frames = [_scene(name, i) for i in range(8)]
        frames[0].save(
            out / f"{name}.gif",
            save_all=True,
            append_images=frames[1:],
            duration=125,
            loop=0,
            disposal=2,
            optimize=True,
        )

    manifest = {
        "name": "Giraffe Weather Fullscreen",
        "resolution": [64, 64],
        "layout": {
            "clock": {"x":9,"y":0,"w":46,"h":10,"align":"center","background":None,"foreground":[255,255,255]},
            "temperature": {"x":0,"y":54,"w":23,"h":10,"align":"left","background":None,"foreground":[255,255,255]},
            "condition": {"x":24,"y":54,"w":40,"h":10,"align":"right","background":None,"foreground":[255,255,255]}
        },
        "animations": {name: f"{name}.gif" for name in SCENES}
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    marker.write_text("ok", encoding="utf-8")
    return out
