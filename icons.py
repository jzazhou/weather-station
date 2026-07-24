import math
from functools import lru_cache

from PIL import Image, ImageDraw

from theme import BUTTER, SKY, LAVENDER, SURFACE_ALT, INK_FAINT

SCALE = 4

def _sun(d, cx, cy, r, colour=BUTTER):
    """Disc with eight tapered rays."""
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=colour)

    ray_inner = r * 1.35
    ray_outer = r * 1.85
    for i in range(8):
        # Eight rays, 45 degrees apart. math.radians converts to the
        # radians that sin/cos expect.
        angle = math.radians(i * 45)
        dx, dy = math.cos(angle), math.sin(angle)
        d.line(
            [cx + dx * ray_inner, cy + dy * ray_inner,
             cx + dx * ray_outer, cy + dy * ray_outer],
            fill=colour,
            width=int(r * 0.22),
        )
     
        
def _moon(d, cx, cy, r, colour=SURFACE_ALT):
    """
    Crescent, made by drawing a disc then erasing an offset disc.

    Filling with (0,0,0,0) works because ImageDraw writes pixel values
    directly rather than blending — so a fully transparent fill on an
    RGBA image punches a hole rather than doing nothing.
    """
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=colour)
    off = r * 0.55
    d.ellipse(
        [cx - r + off, cy - r - off * 0.4,
         cx + r + off, cy + r - off * 0.4],
        fill=(0, 0, 0, 0),
    )
    
    
def _cloud(d, cx, cy, w, colour=SKY):
    """
    Cloud built from three overlapping circles plus a rounded base.
    cx, cy is the centre of the base bar; w is total width.
    """
    h = w * 0.42
    # Flat-bottomed body
    d.rounded_rectangle(
        [cx - w / 2, cy - h * 0.35, cx + w / 2, cy + h * 0.45],
        radius=h * 0.5,
        fill=colour,
    )
    # Three puffs of decreasing size across the top
    for frac, size in ((-0.24, 0.34), (0.02, 0.46), (0.26, 0.30)):
        r = w * size / 2
        px = cx + w * frac
        py = cy - h * 0.30
        d.ellipse([px - r, py - r, px + r, py + r], fill=colour)


def _raindrops(d, cx, cy, w, colour=LAVENDER, count=3):
    """Short slanted strokes below a cloud."""
    spacing = w * 0.26
    start_x = cx - spacing * (count - 1) / 2
    for i in range(count):
        x = start_x + i * spacing
        d.line(
            [x, cy, x - w * 0.07, cy + w * 0.20],
            fill=colour,
            width=int(w * 0.055),
        )


def _snowflakes(d, cx, cy, w, colour=SKY, count=3):
    """Small dots standing in for falling snow."""
    spacing = w * 0.26
    start_x = cx - spacing * (count - 1) / 2
    r = w * 0.045
    for i in range(count):
        x = start_x + i * spacing
        y = cy + (w * 0.10 if i % 2 == 0 else w * 0.19)
        d.ellipse([x - r, y - r, x + r, y + r], fill=colour)


def _bolt(d, cx, cy, w, colour=BUTTER):
    """Lightning bolt as a single polygon."""
    s = w * 0.30
    d.polygon(
        [
            (cx + s * 0.15, cy),
            (cx - s * 0.35, cy + s * 0.75),
            (cx - s * 0.02, cy + s * 0.75),
            (cx - s * 0.22, cy + s * 1.5),
            (cx + s * 0.40, cy + s * 0.55),
            (cx + s * 0.05, cy + s * 0.55),
        ],
        fill=colour,
    )

def _mist(d, cx, cy, w, colour=INK_FAINT):
    """Three horizontal bars of varying length."""
    for i, frac in enumerate((0.85, 1.0, 0.7)):
        y = cy + (i - 1) * w * 0.20
        half = w * frac / 2
        d.rounded_rectangle(
            [cx - half, y - w * 0.045, cx + half, y + w * 0.045],
            radius=w * 0.045,
            fill=colour,
        )


@lru_cache(maxsize=32)
def weather_icon(condition_id, is_day, size):
    S = size * SCALE
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    cx = cy = S / 2

    if condition_id is None:
        _cloud(d, cx, cy, S * 0.72, colour=INK_FAINT)

    elif 200 <= condition_id < 300:                 # thunderstorm
        _cloud(d, cx, cy - S * 0.10, S * 0.74, colour=LAVENDER)
        _bolt(d, cx, cy + S * 0.14, S)

    elif 300 <= condition_id < 600:                 # drizzle and rain
        heavy = condition_id >= 502
        _cloud(d, cx, cy - S * 0.10, S * 0.74)
        _raindrops(d, cx, cy + S * 0.17, S * 0.74,
                   count=4 if heavy else 3)

    elif 600 <= condition_id < 700:                 # snow
        _cloud(d, cx, cy - S * 0.10, S * 0.74)
        _snowflakes(d, cx, cy + S * 0.17, S * 0.74)

    elif 700 <= condition_id < 800:                 # mist, fog, haze
        _mist(d, cx, cy, S * 0.78)

    elif condition_id == 800:                       # clear
        if is_day:
            _sun(d, cx, cy, S * 0.22)
        else:
            _moon(d, cx, cy, S * 0.26)

    elif condition_id == 801:                       # few clouds
        if is_day:
            _sun(d, cx + S * 0.16, cy - S * 0.16, S * 0.17)
        else:
            _moon(d, cx + S * 0.16, cy - S * 0.16, S * 0.19)
        _cloud(d, cx - S * 0.05, cy + S * 0.10, S * 0.66)

    else:                                           # 802-804 cloudy
        _cloud(d, cx + S * 0.06, cy - S * 0.06, S * 0.52,
               colour=SURFACE_ALT)
        _cloud(d, cx - S * 0.06, cy + S * 0.08, S * 0.68)

    return img.resize((size, size), Image.LANCZOS)


