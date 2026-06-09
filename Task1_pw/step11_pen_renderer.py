from PIL import Image, ImageDraw
import json
import os

FPS = 30
DURATION = 70

BASE_IMAGE = "QuestionPPT.pptx.png"
OUTPUT_DIR = "frames_pen"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# -----------------------------
# Load Timeline
# -----------------------------

with open(
    "timeline.json",
    "r",
    encoding="utf-8"
) as f:
    timeline = json.load(f)

TOTAL_FRAMES = FPS * DURATION

# -----------------------------
# Frame Loop
# -----------------------------

for frame_no in range(TOTAL_FRAMES):

    current_time = frame_no / FPS

    img = Image.open(
        BASE_IMAGE
    ).convert("RGBA")

    draw = ImageDraw.Draw(img)

    for action in timeline:

        if current_time < action["start"]:
            continue

        action_type = action["action"]

        # =====================================
        # Highlight
        # =====================================

        if action_type == "highlight":

            overlay = Image.new(
                "RGBA",
                img.size,
                (255,255,255,0)
            )

            hdraw = ImageDraw.Draw(
                overlay
            )

            hdraw.rectangle(
                [
                    (action["x"], action["y"]),
                    (
                        action["x_end"],
                        action["y_end"]
                    )
                ],
                fill=(255,255,0,80)
            )

            img = Image.alpha_composite(
                img,
                overlay
            )

        # =====================================
        # Circle
        # =====================================

        elif action_type == "circle":

            draw = ImageDraw.Draw(img)

            draw.ellipse(
                [
                    (
                        action["x"]-8,
                        action["y"]-8
                    ),
                    (
                        action["x_end"]+8,
                        action["y_end"]+8
                    )
                ],
                outline=(0,70,255),
                width=5
            )

        # =====================================
        # Handwriting Reveal
        # =====================================

        elif action_type == "latex":

            formula = Image.open(
                action["handwriting_image"]
            ).convert("RGBA")

            x = action["x"]
            y = action["y"]

            # Completed formula

            if current_time >= action["end"]:

                img.alpha_composite(
                    formula,
                    (x, y)
                )

            else:

                progress = (
                    current_time
                    - action["start"]
                ) / (
                    action["end"]
                    - action["start"]
                )

                progress = max(
                    0,
                    min(progress, 1)
                )

                visible_width = int(
                    formula.width
                    * progress
                )

                if visible_width > 0:

                    partial = formula.crop(
                        (
                            0,
                            0,
                            visible_width,
                            formula.height
                        )
                    )

                    img.alpha_composite(
                        partial,
                        (x, y)
                    )

                    # ---------------------
                    # Pen Tip
                    # ---------------------

                    pen_x = (
                        x
                        + visible_width
                    )

                    pen_y = (
                        y
                        + formula.height // 2
                    )

                    draw = ImageDraw.Draw(img)

                    draw.ellipse(
                        [
                            (
                                pen_x-4,
                                pen_y-4
                            ),
                            (
                                pen_x+4,
                                pen_y+4
                            )
                        ],
                        fill=(0,70,255)
                    )

    img.convert("RGB").save(
        f"{OUTPUT_DIR}/frame_{frame_no:05d}.png"
    )

    if frame_no % 100 == 0:

        print(
            f"Generated "
            f"{frame_no}/"
            f"{TOTAL_FRAMES}"
        )

print("\n✅ Pen animation frames generated")