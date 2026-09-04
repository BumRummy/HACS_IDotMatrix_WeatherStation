from __future__ import annotations

from pathlib import Path
import json
from PIL import Image, ImageDraw

SCENES = (
    "sunny", "partly_cloudy", "cloudy", "rain", "thunderstorm",
    "snow", "windy", "fog", "clear_night", "extreme_heat", "freezing", "default"
)


def _giraffe(draw: ImageDraw.ImageDraw, ox: int = 0, oy: int = 0, scarf: bool = False) -> None:
    """Draw a small pixel-art giraffe designed for a 64x64 matrix."""
    yellow = (255, 184, 0)
    brown = (116, 61, 16)
    white = (250, 250, 250)
    black = (5, 5, 5)
    red = (220, 20, 35)

    # Neck/body.
    draw.rectangle((27+ox, 29+oy, 35+ox, 50+oy), fill=yellow)
    draw.rectangle((24+ox, 43+oy, 42+ox, 51+oy), fill=yellow)
    # Head + muzzle.
    draw.rectangle((25+ox, 19+oy, 41+ox, 32+oy), fill=yellow)
    draw.rectangle((37+ox, 24+oy, 47+ox, 31+oy), fill=yellow)
    # Ears and ossicones.
    draw.rectangle((22+ox, 20+oy, 26+ox, 23+oy), fill=yellow)
    draw.rectangle((41+ox, 20+oy, 45+ox, 23+oy), fill=yellow)
    draw.line((29+ox, 19+oy, 28+ox, 15+oy), fill=brown, width=2)
    draw.line((37+ox, 19+oy, 38+ox, 15+oy), fill=brown, width=2)
    draw.rectangle((27+ox, 14+oy, 29+ox, 16+oy), fill=brown)
    draw.rectangle((37+ox, 14+oy, 39+ox, 16+oy), fill=brown)
    # Spots.
    for x, y in ((28,22),(35,20),(31,28),(39,27),(29,35),(34,39),(30,46),(39,47)):
        draw.rectangle((x+ox, y+oy, x+2+ox, y+2+oy), fill=brown)
    # Eye and smile.
    draw.rectangle((34+ox, 23+oy, 36+ox, 25+oy), fill=white)
    draw.point((35+ox, 24+oy), fill=black)
    draw.line((39+ox, 29+oy, 43+ox, 29+oy), fill=brown)
    draw.point((44+ox, 28+oy), fill=brown)
    # Legs.
    draw.rectangle((27+ox, 50+oy, 30+ox, 53+oy), fill=brown)
    draw.rectangle((38+ox, 50+oy, 41+ox, 53+oy), fill=brown)
    if scarf:
        draw.rectangle((25+ox, 32+oy, 39+ox, 35+oy), fill=red)
        draw.rectangle((27+ox, 35+oy, 30+ox, 43+oy), fill=red)


def _scene(name: str, frame: int) -> Image.Image:
    im = Image.new("RGB", (64, 64), (2, 4, 9))
    d = ImageDraw.Draw(im)
    # UI regions are deliberately left dark; renderer overwrites them anyway.
    d.rectangle((0, 0, 63, 10), fill=(0, 0, 0))
    d.rectangle((0, 53, 63, 63), fill=(0, 0, 0))

    if name in ("sunny", "partly_cloudy", "cloudy", "default"):
        d.rectangle((0, 11, 63, 52), fill=(5, 24, 55))
        if name != "cloudy":
            cx, cy = 50, 21
            r = 5 + (1 if frame % 4 == 1 else 0)
            d.ellipse((cx-r, cy-r, cx+r, cy+r), fill=(255, 197, 0))
            for dx, dy in ((0,-9),(0,9),(-9,0),(9,0),(-6,-6),(6,6),(-6,6),(6,-6)):
                d.point((cx+dx, cy+dy), fill=(255, 220, 50))
        if name in ("partly_cloudy", "cloudy"):
            for x, y in ((7,19),(13,18),(19,20),(42,31),(48,29),(54,31)):
                d.ellipse((x-4,y-2,x+5,y+3), fill=(235,235,235))
        _giraffe(d)

    elif name == "rain":
        d.rectangle((0, 11, 63, 52), fill=(3, 16, 32))
        # Umbrella.
        d.pieslice((17, 14, 47, 36), 180, 360, fill=(238, 36, 45))
        d.line((32, 25, 32, 47), fill=(210,210,210), width=1)
        d.arc((29, 43, 36, 50), 0, 180, fill=(210,210,210))
        _giraffe(d, oy=3)
        for i in range(13):
            x = (i * 9 + frame * 3) % 64
            y = 12 + ((i * 7 + frame * 4) % 38)
            d.line((x, y, max(0,x-1), min(52,y+2)), fill=(0, 205, 255))

    elif name == "thunderstorm":
        d.rectangle((0, 11, 63, 52), fill=(4, 7, 13))
        for x in (9, 18, 47, 55):
            d.ellipse((x-7, 14, x+7, 21), fill=(115,115,125))
        _giraffe(d)
        if frame in (1, 2):
            d.line((51,22,47,30,51,30,46,40), fill=(255,225,0), width=2)
        for i in range(8):
            x = (i*11 + frame*2) % 64
            y = 24 + ((i*8 + frame*4) % 25)
            d.line((x,y,max(0,x-1),y+2), fill=(90,120,150))

    elif name == "snow":
        d.rectangle((0, 11, 63, 52), fill=(5, 22, 48))
        _giraffe(d, scarf=True)
        for i in range(18):
            x = (i*13 + frame*2) % 64
            y = 12 + ((i*9 + frame*2) % 39)
            d.point((x,y), fill=(250,250,255))
            if i % 4 == 0:
                d.line((x-1,y,x+1,y), fill=(250,250,255))

    elif name == "windy":
        d.rectangle((0, 11, 63, 52), fill=(5, 25, 45))
        _giraffe(d, ox=2)
        for row in range(4):
            y = 17 + row*9
            shift = (frame*3 + row*5) % 15
            d.arc((2+shift,y,31+shift,y+8), 190, 345, fill=(230,245,255))
        for i in range(4):
            x = 8 + ((i*15 + frame*4) % 50)
            y = 16 + i*8
            d.line((x,y,x+4,y+2), fill=(90,200,45), width=2)

    elif name == "fog":
        d.rectangle((0, 11, 63, 52), fill=(55, 58, 60))
        # Trees behind fog.
        d.polygon((7,48,14,24,21,48), fill=(25,30,28))
        d.polygon((45,48,53,21,61,48), fill=(25,30,28))
        _giraffe(d, oy=2)
        for row in range(5):
            y = 22 + row*6
            shift = (frame*2 + row*3) % 10
            d.line((0+shift,y,48+shift,y), fill=(165,165,165), width=2)

    elif name == "clear_night":
        d.rectangle((0, 11, 63, 52), fill=(1, 7, 20))
        d.ellipse((47,14,59,26), fill=(238,238,225))
        _giraffe(d)
        for i in range(12):
            x = 4 + (i*17 % 56)
            y = 14 + (i*11 % 34)
            if (i + frame) % 3 != 0:
                d.point((x,y), fill=(255,215,35))

    elif name == "extreme_heat":
        d.rectangle((0, 11, 63, 52), fill=(88, 15, 4))
        d.ellipse((47,14,59,26), fill=(255,175,0))
        _giraffe(d)
        # Sweat + shimmer.
        for i in range(6):
            x = 7 + i*9
            y = 18 + ((i*5 + frame*3) % 28)
            d.point((x,y), fill=(0,195,255))
            d.point((x,y+1), fill=(0,150,225))
        for x in (18, 44):
            d.arc((x,37-frame%3,x+7,49-frame%3), 180, 350, fill=(255,80,0))

    elif name == "freezing":
        d.rectangle((0, 11, 63, 52), fill=(3, 15, 35))
        _giraffe(d, scarf=True)
        for i in range(15):
            x = (i*13 + frame) % 64
            y = 12 + ((i*7 + frame*2) % 39)
            d.point((x,y), fill=(240,250,255))
        # Animated breath.
        for p in range(3):
            bx = 47 + ((frame + p*2) % 8)
            by = 29 - p
            d.point((min(62,bx),by), fill=(225,245,255))

    return im


def ensure_builtin_pack(base_dir: Path) -> Path:
    """Generate the bundled giraffe pack on first use and return its directory."""
    out = base_dir / "idm_weather_matrix" / "giraffe_default"
    marker = out / ".v1_ready"
    if marker.exists():
        return out

    out.mkdir(parents=True, exist_ok=True)
    for name in SCENES:
        frames = [_scene(name, i) for i in range(6)]
        frames[0].save(
            out / f"{name}.gif",
            save_all=True,
            append_images=frames[1:],
            duration=140,
            loop=0,
            disposal=2,
            optimize=True,
        )

    manifest = {
        "name": "Giraffe Weather",
        "resolution": [64, 64],
        "layout": {
            "clock": {"x":11,"y":0,"w":42,"h":11,"align":"center","background":[0,0,0],"foreground":[255,255,255]},
            "temperature": {"x":0,"y":53,"w":26,"h":11,"align":"left","background":[0,0,0],"foreground":[255,255,255]},
            "condition": {"x":27,"y":53,"w":37,"h":11,"align":"right","background":[0,0,0],"foreground":[255,255,255]}
        },
        "animations": {name: f"{name}.gif" for name in SCENES}
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    marker.write_text("ok", encoding="utf-8")
    return out
