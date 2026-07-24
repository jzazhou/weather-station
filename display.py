import numpy as np
from PIL import Image


FB_DEVICE = "/dev/fb0"

WIDTH = 480
HEIGHT = 320

def rgb888_to_rgb565(image):
    arr = np.array(image, dtype=np.uint8)
    r = (arr[:, :, 0] >> 3).astype(np.uint16)
    g = (arr[:, :, 1] >> 2).astype(np.uint16)
    b = (arr[:, :, 2] >> 3).astype(np.uint16)
    rgb565 = (r << 11) | (g << 5) | b 
    return rgb565.astype("<u2").tobytes()

def show(image):
    if image.size != (WIDTH, HEIGHT):
        raise ValueError(
            f"Image is {image.size}, but display is {WIDTH, HEIGHT}"
        )
    
    if image.mode != "RGB":
        image = image.convert("RGB")
        
    raw = rgb888_to_rgb565(image)
    
    with open(FB_DEVICE, "wb") as fb:
        fb.write(raw)
        
if __name__ == "__main__":
    import time
    
    print("Drawing test pattern. Watch the LCD.")
    
    for name, colour in [
        ("red", (255, 0, 0)),
        ("green", (0, 255, 0)),
        ("blue", (0, 0, 255)),
        ("white", (255, 255, 255)),
    ]:
        print(f"  {name}")
        img = Image.new("RGB", (WIDTH, HEIGHT), colour)
        show(img)
        time.sleep(1)
        
    print("  gradient")
    img = Image.new("RGB", (WIDTH, HEIGHT))
    pixels= img.load()
    for x in range(WIDTH):
        for y in range(HEIGHT):
            pixels[x, y] = (
                int(255 * x / WIDTH),
                int(255 * y / HEIGHT),
                128
            )
    show(img)
    print("Done.")