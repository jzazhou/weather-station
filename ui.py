from datetime import datetime

from PIL import Image, ImageDraw, ImageEnhance

from icons import weather_icon
from theme import (
    CREAM, SURFACE, INK, INK_MUTED, INK_FAINT,
    PINK, PINK_SOFT, SAGE, SAGE_SOFT, AQ_COLOURS,
    F_CLOCK, F_DATE, F_TEMP_BIG, F_TEMP_UNIT,
    F_HEADING, F_VALUE, F_LABEL, F_SMALL, F_FEELS,
)

WIDTH, HEIGHT = 480, 320

PAD        = 16
HEADER_H   = 68
CARD_TOP   = 76
CARD_BOT   = 274
CARD_W     = (WIDTH - PAD * 3) // 2      # two equal columns
LEFT_X     = PAD
RIGHT_X    = PAD * 2 + CARD_W

DIM_START_HOUR = 22   # 10pm
DIM_END_HOUR   = 7    # 7am
DIM_LEVEL      = 0.45 # 45% brightness overnight

def _stat(d, x, y, label, value):
    """Draws a small label with a larger value beneath it."""
    d.text((x, y), label.upper(), font=F_LABEL, fill=INK_MUTED)
    d.text((x, y + 15), value, font=F_VALUE, fill=INK)
    
def _pill(d, x, y, text, colour):
    """
    Rounded badge with centred text — used for air quality.

    textbbox measures the pixel dimensions the string will occupy,
    which is how we size the badge to fit its contents rather than
    guessing a fixed width.
    """
    bbox = d.textbbox((0, 0), text, font=F_HEADING)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pad_x, pad_y = 10, 6
    d.rounded_rectangle(
        [x, y, x + tw + pad_x * 2, y + th + pad_y * 2 + 2],
        radius=(th + pad_y * 2) / 2,
        fill=colour,
    )
    d.text((x + pad_x, y + pad_y - 1), text, font=F_HEADING, fill=SURFACE)


def _big_temp(d, x, y, value, accent):
    """
    Large temperature with a smaller degree unit beside it.

    Returns nothing; draws in place. The unit is positioned using the
    measured width of the number so it sits correctly no matter how
    many digits there are.
    """
    text = "—" if value is None else f"{value:.1f}"
    d.text((x, y), text, font=F_TEMP_BIG, fill=INK)
    bbox = d.textbbox((x, y), text, font=F_TEMP_BIG)
    d.text((bbox[2] + 4, y + 14), "°C", font=F_TEMP_UNIT, fill=accent)


def render(data, now=None):
    """
    Builds one frame.

    'data' is a snapshot dict from DataStore. Every field may be None,
    and the layout must survive that — at boot, and during any network
    or sensor outage, None is the truthful value.
    """
    if now is None:
        now = datetime.now()

    img = Image.new("RGB", (WIDTH, HEIGHT), CREAM)
    d = ImageDraw.Draw(img)

    # ---------------- Header: clock and date ----------------
    d.text((PAD + 4, 12), now.strftime("%H:%M"), font=F_CLOCK, fill=INK)

    # anchor="rm" means right-middle: the text's right edge sits at the
    # given x. Right-aligning without needing to measure the string.
    d.text((WIDTH - PAD - 4, 26), now.strftime("%A").upper(),
           font=F_DATE, fill=SAGE, anchor="rm")
    d.text((WIDTH - PAD - 4, 46), now.strftime("%d %B %Y"),
           font=F_DATE, fill=INK_MUTED, anchor="rm")

    # Hairline under the header
    d.line([PAD, HEADER_H, WIDTH - PAD, HEADER_H], fill=INK_FAINT, width=1)

    # ---------------- Left card: indoor ----------------
    d.rounded_rectangle(
        [LEFT_X, CARD_TOP, LEFT_X + CARD_W, CARD_BOT],
        radius=18, fill=SURFACE,
    )
    # Accent tab along the top edge of the card
    d.rounded_rectangle(
        [LEFT_X + 16, CARD_TOP + 12, LEFT_X + 46, CARD_TOP + 16],
        radius=2, fill=PINK,
    )
    d.text((LEFT_X + 16, CARD_TOP + 24), "INDOOR",
           font=F_HEADING, fill=INK_MUTED)

    indoor = data.get("indoor")
    _big_temp(d, LEFT_X + 16, CARD_TOP + 44,
              indoor["temp"] if indoor else None, PINK)

    if indoor:
        _stat(d, LEFT_X + 16,  CARD_TOP + 112,
              "humidity", f"{indoor['humidity']:.0f}%")
        _stat(d, LEFT_X + 112, CARD_TOP + 112,
              "pressure", f"{indoor['pressure']:.0f}")

        label = indoor["air_quality"]
        d.text((LEFT_X + 16, CARD_TOP + 158), "AIR QUALITY",
               font=F_LABEL, fill=INK_MUTED)
        _pill(d, LEFT_X + 16, CARD_TOP + 174, label,
              AQ_COLOURS.get(label, INK_FAINT))
    else:
        d.text((LEFT_X + 16, CARD_TOP + 120), "waiting for sensor…",
               font=F_SMALL, fill=INK_FAINT)

    # ---------------- Right card: outdoor ----------------
    d.rounded_rectangle(
        [RIGHT_X, CARD_TOP, RIGHT_X + CARD_W, CARD_BOT],
        radius=18, fill=SURFACE,
    )
    d.rounded_rectangle(
        [RIGHT_X + 16, CARD_TOP + 12, RIGHT_X + 46, CARD_TOP + 16],
        radius=2, fill=SAGE,
    )
    d.text((RIGHT_X + 16, CARD_TOP + 24), "OUTDOOR",
           font=F_HEADING, fill=INK_MUTED)

    outdoor = data.get("outdoor")

    if outdoor:
        # Icon, top-right of the card. The 'd'/'n' suffix on OWM's
        # icon code tells us day or night.
        is_day = str(outdoor.get("icon_code", "01d")).endswith("d")
        icon = weather_icon(outdoor.get("condition_id"), is_day, 66)
        # The third argument is the alpha mask — passing the RGBA image
        # as its own mask makes transparent areas stay transparent
        # instead of pasting black.
        img.paste(icon, (RIGHT_X + CARD_W - 80, CARD_TOP + 16), icon)

        _big_temp(d, RIGHT_X + 16, CARD_TOP + 44, outdoor["temp"], SAGE)
        
        gap = outdoor["feels_like"] - outdoor["temp"]
        feels_colour = PINK if abs(gap) >= 3 else INK_MUTED

        d.text((RIGHT_X + 16, CARD_TOP + 100),
               f"feels like {outdoor['feels_like']:.1f}°",
               font=F_FEELS, fill=feels_colour)

        d.text((RIGHT_X + 16, CARD_TOP + 128), outdoor["description"],
               font=F_VALUE, fill=INK)

        _stat(d, RIGHT_X + 16,  CARD_TOP + 158,
              "humidity", f"{outdoor['humidity']:.0f}%")
        _stat(d, RIGHT_X + 112, CARD_TOP + 158,
              "wind", f"{outdoor['wind_speed']:.1f} m/s")
    else:
        d.text((RIGHT_X + 16, CARD_TOP + 120), "waiting for network…",
               font=F_SMALL, fill=INK_FAINT)

    # ---------------- Footer: freshness ----------------
    def stamp(t):
        return t.strftime("%H:%M") if t else "--:--"

    d.text((PAD + 4, CARD_BOT + 14),
           f"indoor {stamp(data.get('indoor_time'))}"
           f"   ·   outdoor {stamp(data.get('outdoor_time'))}",
           font=F_SMALL, fill=INK_FAINT)

    d.text((WIDTH - PAD - 4, CARD_BOT + 14), "openweather",
           font=F_SMALL, fill=INK_FAINT, anchor="ra")

    # ---------------- Overnight dimming ----------------
    # Software dimming: multiply every pixel toward black. Simple and
    # requires no extra hardware control.
    hour = now.hour
    if hour >= DIM_START_HOUR or hour < DIM_END_HOUR:
        img = ImageEnhance.Brightness(img).enhance(DIM_LEVEL)

    return img


# Preview without hardware: writes a PNG you can open in VS Code.
if __name__ == "__main__":
    sample = {
        "indoor": {
            "temp": 24.3, "humidity": 58, "pressure": 1006,
            "gas": 62000, "air_quality": "Excellent",
        },
        "outdoor": {
            "temp": 33.0, "feels_like": 37.2, "humidity": 53,
            "pressure": 1005, "description": "Clear Sky",
            "icon_code": "01d", "condition_id": 800,
            "wind_speed": 2.2, "city": "Hong Kong",
        },
        "indoor_time": datetime.now(),
        "outdoor_time": datetime.now(),
    }
    render(sample).save("preview.png")
    print("Wrote preview.png")