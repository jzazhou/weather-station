from pathlib import Path
from PIL import ImageFont

FONT_DIR = Path(__file__).parent / "fonts"

CREAM       = (253, 246, 240)   # page background
SURFACE     = (255, 251, 248)   # cards, slightly lighter than page
SURFACE_ALT = (246, 235, 230)   # secondary panels

INK         = (74,  66,  67)    # primary text — warm near-black,
                                # softer than pure black on cream
INK_MUTED   = (154, 140, 135)   # labels, secondary text
INK_FAINT   = (205, 192, 187)   # hairlines, dividers

PINK        = (232, 180, 184)   # accent — indoor
PINK_SOFT   = (245, 222, 224)
SAGE        = (168, 191, 165)   # accent — outdoor
SAGE_SOFT   = (223, 232, 221)
BUTTER      = (243, 225, 192)   # sun, warm highlights
SKY         = (198, 216, 226)   # cloud, sky elements
LAVENDER    = (206, 200, 222)   # night, rain

AQ_COLOURS = {
    "Excellent": (143, 176, 140),
    "Good":      (183, 201, 176),
    "Fair":      (226, 195, 145),
    "Poor":      (216, 154, 154),
    "—":         INK_FAINT,
}

def _font(filename, size):
    return ImageFont.truetype(str(FONT_DIR / filename), size)

F_CLOCK     = _font("Quicksand-Bold.ttf",   40)
F_DATE      = _font("Quicksand-Medium.ttf", 14)
F_TEMP_BIG  = _font("Quicksand-Bold.ttf",   50)
F_TEMP_UNIT = _font("Quicksand-Medium.ttf", 18)
F_HEADING   = _font("Quicksand-Bold.ttf",   12)
F_VALUE     = _font("Quicksand-Medium.ttf", 17)
F_LABEL     = _font("Quicksand-Medium.ttf", 12)
F_SMALL     = _font("Quicksand-Light.ttf",  11)
F_FEELS     = _font("Quicksand-Medium.ttf", 20)