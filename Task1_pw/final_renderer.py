from PIL import Image, ImageDraw, ImageFont
import json
import os
import random

# =====================================
# CONFIG
# =====================================

FPS = 30
DURATION = 70

BASE_IMAGE = "QuestionPPT.pptx.png"
FONT_PATH = "fonts/Kalam-Regular.ttf"

OUTPUT_DIR = "frames_final"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# =====================================
# LOAD FILES
# =====================================

with open("timeline.json", "r", encoding="utf-8") as f:
    timeline = json.load(f)

with open("ocr_results.json", "r", encoding="utf-8") as f:
    ocr_data = json.load(f)

# =====================================
# FONT
# =====================================

try:
    font = ImageFont.truetype(FONT_PATH, 38)
except:
    font = ImageFont.load_default()

# =====================================
# HELPERS
# =====================================

def find_bbox(text):

    if not text:
        return None

    for item in ocr_data:

        ocr_text = item.get("text", "")

        if text.lower() in ocr_text.lower():
            return item.get("bbox")

        if ocr_text.lower() in text.lower():
            return item.get("bbox")

    return None


def latex_to_text(text):

    if not text:
        return ""

    text = text.replace("\\sqrt", "sqrt")

    text = text.replace("_1", "1")
    text = text.replace("_2", "2")

    text = text.replace("{", "(")
    text = text.replace("}", ")")

    text = text.replace("\\ ", " ")

    text = text.replace("D=", "D = ")

    return text


# =====================================
# FRAME GENERATION
# =====================================

TOTAL_FRAMES = FPS * DURATION

for frame_no in range(TOTAL_FRAMES):

    current_time = frame_no / FPS

    img = Image.open(BASE_IMAGE).convert("RGBA")

    draw = ImageDraw.Draw(img)

    for action in timeline:

        start = action.get("start", 0)

        if current_time < start:
            continue

        action_type = action.get("action", "")

        # =====================================
        # HIGHLIGHT
        # =====================================

        if action_type == "highlight":

            bbox = find_bbox(
                action.get("content", "")
            )

            if bbox:

                x1 = bbox[0][0]
                y1 = bbox[0][1]

                x2 = bbox[2][0]
                y2 = bbox[2][1]

                overlay = Image.new(
                    "RGBA",
                    img.size,
                    (255, 255, 255, 0)
                )

                hdraw = ImageDraw.Draw(overlay)

                for yy in range(y1, y2, 6):

                    hdraw.rectangle(
                        [
                            (x1, yy),
                            (x2, yy + 5)
                        ],
                        fill=(255, 255, 0, 70)
                    )

                img = Image.alpha_composite(
                    img,
                    overlay
                )

                draw = ImageDraw.Draw(img)

        # =====================================
        # FORMULA WRITING
        # =====================================

        elif action_type == "latex":

            text = latex_to_text(
                action.get("latex", "")
            )

            end = action.get(
                "end",
                start + 1
            )

            if current_time >= end:

                visible_text = text

            else:

                duration = max(
                    0.1,
                    end - start
                )

                progress = (
                    current_time - start
                ) / duration

                progress = max(
                    0,
                    min(progress, 1)
                )

                chars = int(
                    len(text) * progress
                )

                visible_text = text[:chars]

            x = action.get("x", 470)
            y = action.get("y", 120)

            random.seed(
                frame_no + x + y
            )

            jx = 0
            jy = 0

            draw.text(
                (x + jx, y + jy),
                visible_text,
                fill=(20, 20, 20),
                font=font
            )

            # Pen Cursor

            if current_time < end:

                try:

                    tb = draw.textbbox(
                        (x, y),
                        visible_text,
                        font=font
                    )

                    pen_x = tb[2]
                    pen_y = (
                        tb[1] + tb[3]
                    ) // 2

                    draw.ellipse(
                        [
                            (
                                pen_x - 5,
                                pen_y - 5
                            ),
                            (
                                pen_x + 5,
                                pen_y + 5
                            )
                        ],
                        fill=(0, 70, 255)
                    )

                except:
                    pass

        # =====================================
        # ANSWER CIRCLE
        # =====================================

        elif action_type == "circle":

            bbox = find_bbox(
                action.get("content", "")
            )

            if bbox:

                x1 = bbox[0][0]
                y1 = bbox[0][1]

                x2 = bbox[2][0]
                y2 = bbox[2][1]

                draw.ellipse(
                    [
                        (
                            x1 - 10,
                            y1 - 10
                        ),
                        (
                            x2 + 10,
                            y2 + 10
                        )
                    ],
                    outline=(0, 70, 255),
                    width=5
                )

    img.convert("RGB").save(
        f"{OUTPUT_DIR}/frame_{frame_no:05d}.png"
    )

    if frame_no % 100 == 0:

        print(
            f"Generated {frame_no}/{TOTAL_FRAMES}"
        )

print("\n✅ All frames generated!")