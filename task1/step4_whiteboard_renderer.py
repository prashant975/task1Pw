from PIL import Image, ImageDraw, ImageFont
import os

WIDTH = 1280
HEIGHT = 720

os.makedirs("frames", exist_ok=True)

# Whiteboard
img = Image.new("RGB", (WIDTH, HEIGHT), "white")

draw = ImageDraw.Draw(img)

# Use your font
font_path = "fonts/Kalam-Regular.ttf"

font = ImageFont.truetype(font_path, 42)

# Question
question = "Find distance between A(1,2) and B(4,6)"

draw.text(
    (50, 50),
    question,
    fill="black",
    font=font
)

# Formula
formula = "D = √((x2-x1)^2 + (y2-y1)^2)"

draw.text(
    (50, 200),
    formula,
    fill="blue",
    font=font
)

img.save("frames/frame_0001.png")

print("Frame Generated")