from PIL import Image, ImageDraw, ImageFont
import json
import os
import random

# -------------------------
# CONFIG
# -------------------------

FPS = 30
DURATION = 70

TOTAL_FRAMES = FPS * DURATION

IMAGE_PATH = "QuestionPPT.pptx.png"

FONT_PATH = "fonts/Kalam-Regular.ttf"

os.makedirs("frames", exist_ok=True)

# -------------------------
# LOAD TIMELINE
# -------------------------

with open(
    "timeline.json",
    "r",
    encoding="utf-8"
) as f:

    timeline = json.load(f)

# -------------------------
# FONT
# -------------------------

try:

    font = ImageFont.truetype(
        FONT_PATH,
        34
    )

except:

    font = ImageFont.load_default()

# -------------------------
# GENERATE FRAMES
# -------------------------

for frame_no in range(TOTAL_FRAMES):

    current_time = frame_no / FPS

    # Base Image
    img = Image.open(
        IMAGE_PATH
    ).convert("RGBA")

    draw = ImageDraw.Draw(img)

    # -------------------------
    # Process Timeline
    # -------------------------

    for action in timeline:

        start = action["start"]
        end = action["end"]

        if current_time < start:
            continue

        action_type = action["action"]

        # =================================
        # HIGHLIGHT
        # =================================

        if action_type == "highlight":

            highlight = Image.new(
                "RGBA",
                img.size,
                (255, 255, 255, 0)
            )

            hdraw = ImageDraw.Draw(
                highlight
            )

            hdraw.rectangle(
                [
                    (
                        action["x"],
                        action["y"]
                    ),
                    (
                        action["x_end"],
                        action["y_end"]
                    )
                ],
                fill=(255, 255, 0, 90)
            )

            img = Image.alpha_composite(
                img,
                highlight
            )

            draw = ImageDraw.Draw(img)

        # =================================
        # CIRCLE
        # =================================

        elif action_type == "circle":

            draw.ellipse(
                [
                    (
                        action["x"],
                        action["y"]
                    ),
                    (
                        action["x_end"],
                        action["y_end"]
                    )
                ],
                outline=(0, 70, 255),
                width=6
            )

        # =================================
        # WRITE
        # =================================

        elif action_type == "write":

            text = action["content"]

            # completed step

            if current_time >= end:

                visible_text = text

            else:

                progress = (
                    current_time - start
                ) / (
                    end - start
                )

                progress = max(
                    0,
                    min(progress, 1)
                )

                chars = int(
                    len(text) * progress
                )

                visible_text = text[:chars]

            # handwriting feel

            random.seed(
                action["x"] +
                action["y"]
            )

            jx = random.randint(-2, 2)
            jy = random.randint(-1, 1)

            draw.multiline_text(
                (
                    action["x"] + jx,
                    action["y"] + jy
                ),
                visible_text,
                fill=(20, 20, 20),
                font=font,
                spacing=10
            )

    # -------------------------
    # SAVE FRAME
    # -------------------------

    img.convert("RGB").save(
        f"frames/frame_{frame_no:05d}.png"
    )

    if frame_no % 100 == 0:

        print(
            f"Generated "
            f"{frame_no}/"
            f"{TOTAL_FRAMES}"
        )

print("\n✅ All frames generated!")