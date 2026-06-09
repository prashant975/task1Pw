from PIL import Image, ImageDraw, ImageFont
import json
import os
import random

# ==========================
# CONFIG
# ==========================

FPS = 30
DURATION = 70

IMAGE_PATH = "QuestionPPT.pptx.png"
FONT_PATH = "fonts/Kalam-Regular.ttf"

TOTAL_FRAMES = FPS * DURATION

os.makedirs("frames_v2", exist_ok=True)

# ==========================
# LOAD FILES
# ==========================

with open("timeline.json", "r", encoding="utf-8") as f:
    timeline = json.load(f)

with open("ocr_results.json", "r", encoding="utf-8") as f:
    ocr_data = json.load(f)

# ==========================
# FONT
# ==========================

try:
    font = ImageFont.truetype(
        FONT_PATH,
        34
    )
except:
    font = ImageFont.load_default()

# ==========================
# OCR LOOKUP
# ==========================

def find_bbox(text):

    for item in ocr_data:

        ocr_text = item["text"]

        if text.lower() in ocr_text.lower():
            return item["bbox"]

        if ocr_text.lower() in text.lower():
            return item["bbox"]

    return None


# ==========================
# FRAME LOOP
# ==========================

for frame_no in range(TOTAL_FRAMES):

    current_time = frame_no / FPS

    img = Image.open(
        IMAGE_PATH
    ).convert("RGBA")

    draw = ImageDraw.Draw(img)

    for action in timeline:

        if current_time < action["start"]:
            continue

        action_type = action["action"]

        # ====================================
        # HIGHLIGHT
        # ====================================

        if action_type == "highlight":

            bbox = find_bbox(
                action["content"]
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

                hdraw = ImageDraw.Draw(
                    overlay
                )

                hdraw.rectangle(
                    [(x1, y1), (x2, y2)],
                    fill=(255, 255, 0, 90)
                )

                img = Image.alpha_composite(
                    img,
                    overlay
                )

                draw = ImageDraw.Draw(img)

        # ====================================
        # CIRCLE
        # ====================================

        elif action_type == "circle":

            bbox = find_bbox(
                action["content"]
            )

            if bbox:

                x1 = bbox[0][0]
                y1 = bbox[0][1]

                x2 = bbox[2][0]
                y2 = bbox[2][1]

                draw.ellipse(
                    [
                        (x1 - 10, y1 - 10),
                        (x2 + 10, y2 + 10)
                    ],
                    outline=(0, 70, 255),
                    width=6
                )

        # ====================================
        # WRITE
        # ====================================

        elif action_type == "write":

            text = action["content"]

            if current_time >= action["end"]:

                visible_text = text

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

                chars = int(
                    len(text) * progress
                )

                visible_text = text[:chars]

            random.seed(
                action["x"]
                + action["y"]
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

    img.convert("RGB").save(
        f"frames_v2/frame_{frame_no:05d}.png"
    )

    if frame_no % 100 == 0:

        print(
            f"Generated "
            f"{frame_no}/"
            f"{TOTAL_FRAMES}"
        )

print("\n✅ All frames generated!")