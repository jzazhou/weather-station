import struct
import time
from PIL import Image, ImageDraw, ImageFont

# ─────────────────────────────────────────────────────────────
# FRAMEBUFFER SETUP
# ─────────────────────────────────────────────────────────────
# The LCD appears as /dev/fb0. To write pixels to it, we need
# to know its resolution and color format.
#
# The ILI9486 driver uses RGB565 — that means each pixel is
# stored in 2 bytes (16 bits), with 5 bits for red, 6 for
# green, and 5 for blue. This is different from the usual
# RGB888 (3 bytes per pixel) that most image software uses.
#
# We'll compose our image in normal RGB using Pillow, then
# convert each pixel to RGB565 before writing.

FB_DEVICE  = "/dev/fb0"
SCREEN_W   = 480
SCREEN_H   = 320

def rgb888_to_rgb565(image):
    """
    Convert a Pillow RGB image to raw RGB565 bytes.
    
    For each pixel (r, g, b) where each value is 0-255:
      - Take the top 5 bits of red     (r >> 3)
      - Take the top 6 bits of green   (g >> 2)
      - Take the top 5 bits of blue    (b >> 3)
      - Pack them into one 16-bit number: RRRRRGGGGGGBBBBB
      - Store as 2 bytes in little-endian order
    """
    pixels = image.tobytes()    # flat bytes: R, G, B, R, G, B, ...
    result = bytearray(SCREEN_W * SCREEN_H * 2)  # 2 bytes per pixel
    
    for i in range(SCREEN_W * SCREEN_H):
        r = pixels[i * 3]
        g = pixels[i * 3 + 1]
        b = pixels[i * 3 + 2]
        # Pack into 16-bit RGB565
        rgb565 = ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)
        # Store as little-endian unsigned short
        struct.pack_into('<H', result, i * 2, rgb565)
    
    return bytes(result)

# ─────────────────────────────────────────────────────────────
# COMPOSE THE TEST IMAGE
# ─────────────────────────────────────────────────────────────
# Create a 480x320 image with a pastel blue background,
# a white rounded rectangle, and text — same test as before

img = Image.new("RGB", (SCREEN_W, SCREEN_H), (174, 214, 241))
draw = ImageDraw.Draw(img)

# White rounded rectangle in the center
draw.rounded_rectangle(
    [(140, 110), (340, 210)],
    radius=12,
    fill=(255, 255, 255)
)

# Text label — use default font (custom fonts come in Part 4)
font = ImageFont.load_default(size=24)
text = "LCD working!"
# Get text bounding box to center it
bbox = draw.textbbox((0, 0), text, font=font)
text_w = bbox[2] - bbox[0]
text_h = bbox[3] - bbox[1]
text_x = 140 + (200 - text_w) // 2
text_y = 110 + (100 - text_h) // 2
draw.text((text_x, text_y), text, fill=(80, 80, 80), font=font)

# ─────────────────────────────────────────────────────────────
# WRITE TO THE FRAMEBUFFER
# ─────────────────────────────────────────────────────────────
# Convert to RGB565 and write the raw bytes to /dev/fb0

frame_data = rgb888_to_rgb565(img)

with open(FB_DEVICE, 'wb') as fb:
    fb.write(frame_data)

print("Image sent to LCD! Displaying for 5 seconds...")
time.sleep(5)

# Clear screen to black
black = b'\x00\x00' * SCREEN_W * SCREEN_H
with open(FB_DEVICE, 'wb') as fb:
    fb.write(black)

print("Done!")
