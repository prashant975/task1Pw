from PIL import Image, ImageDraw
import json
import os

FPS = 30
DURATION = 70

TOTAL_FRAMES = FPS * DURATION

BASE_IMAGE = "QuestionPPT.pptx.png"

OUTPUT_DIR = "frames_v3"

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)

# -------------------------
# Load Timeline
# -------------------------

with open(
    "timeline.json",
    "r",
    encoding="utf-8"
) as f:
    timeline = json.load(f)

# -------------------------
# Generate Frames
# -------------------------

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

        # ==================================
        # HIGHLIGHT
        # ==================================

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
                    (
                        action["x"],
                        action["y"]
                    ),
                    (
                        action["x_end"],
                        action["y_end"]
                    )
                ],
                fill=(255,255,0,90)
            )

            img = Image.alpha_composite(
                img,
                overlay
            )

        # ==================================
        # CIRCLE
        # ==================================

        elif action_type == "circle":

            draw = ImageDraw.Draw(img)

            draw.ellipse(
                [
                    (
                        action["x"] - 10,
                        action["y"] - 10
                    ),
                    (
                        action["x_end"] + 10,
                        action["y_end"] + 10
                    )
                ],
                outline=(0,70,255),
                width=6
            )

        # ==================================
        # LATEX
        # ==================================

        elif action_type == "latex":

            formula_img = Image.open(
                action["image"]
            ).convert("RGBA")

            # Completed formula

            if current_time >= action["end"]:

                img.alpha_composite(
                    formula_img,
                    (
                        action["x"],
                        action["y"]
                    )
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
                    formula_img.width
                    * progress
                )

                if visible_width > 0:

                    partial = formula_img.crop(
                        (
                            0,
                            0,
                            visible_width,
                            formula_img.height
                        )
                    )

                    img.alpha_composite(
                        partial,
                        (
                            action["x"],
                            action["y"]
                        )
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

print("\n✅ All frames generated")