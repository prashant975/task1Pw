from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import os

WIDTH = 1280
HEIGHT = 720

os.makedirs("frames", exist_ok=True)

font = ImageFont.truetype(
    "fonts/Kalam-Regular.ttf",
    42
)

text = "D = √((x2-x1)^2 + (y2-y1)^2)"

for i in range(1, len(text)+1):

    img = Image.new(
        "RGB",
        (WIDTH, HEIGHT),
        "white"
    )

    draw = ImageDraw.Draw(img)

    draw.text(
        (50, 200),
        text[:i],
        fill="black",
        font=font
    )

    filename = f"frames/frame_{i:04d}.png"

    img.save(filename)

print("Writing Animation Generated")