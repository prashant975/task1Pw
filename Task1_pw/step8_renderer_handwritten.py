from PIL import Image, ImageDraw, ImageFont
import json
import os
import random

# ==================================
# CONFIG
# ==================================

FPS = 30
DURATION = 70

BASE_IMAGE = "QuestionPPT.pptx.png"
FONT_PATH = "fonts/Kalam-Regular.ttf"

OUTPUT_DIR = "frames_final"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ==================================
# LOAD DATA
# ==================================

with open("timeline.json", "r", encoding="utf-8") as f:
    timeline = json.load(f)

with open("ocr_results.json", "r", encoding="utf-8") as f:
    ocr_data = json.load(f)

# ==================================
# FONT
# ==================================

try:
    font = ImageFont.truetype(
        FONT_PATH,
        32
    )
except:
    font = ImageFont.load_default()

# ==================================
# OCR LOOKUP
# ==================================

def find_bbox(text):

    for item in ocr_data:

        ocr_text = item["text"]

        if text.lower() in ocr_text.lower():
            return item["bbox"]

        if ocr_text.lower() in text.lower():
            return item["bbox"]

    return None

# ==================================
# LATEX -> HANDWRITTEN TEXT
# ==================================

def latex_to_text(latex):

    replacements = {
        "\\sqrt": "sqrt",
        "_1": "1",
        "_2": "2",
        "{": "",
        "}": "",
        "\\ ": " ",
    }

    for old, new in replacements.items():
        latex = latex.replace(old, new)

    return latex

# ==================================
# FRAME LOOP
# ==================================

TOTAL_FRAMES = FPS * DURATION

for frame_no in range(TOTAL_FRAMES):

    current_time = frame_no / FPS

    img = Image.open(BASE_IMAGE).convert("RGBA")

    draw = ImageDraw.Draw(img)

    # ----------------------------------
    # Render Actions
    # ----------------------------------

    for action in timeline:

        if current_time < action["start"]:
            continue

        action_type = action["action"]

        # ==================================
        # HIGHLIGHT
        # ==================================

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
                    (255,255,255,0)
                )

                hdraw = ImageDraw.Draw(
                    overlay
                )

                hdraw.rectangle(
                    [(x1,y1),(x2,y2)],
                    fill=(255,255,0,90)
                )

                img = Image.alpha_composite(
                    img,
                    overlay
                )

                draw = ImageDraw.Draw(img)

        # ==================================
        # CIRCLE
        # ==================================

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
                        (x1-8, y1-8),
                        (x2+8, y2+8)
                    ],
                    outline=(0,70,255),
                    width=5
                )

        # ==================================
        # LATEX (render as handwriting)
        # ==================================

        elif action_type == "latex":

            text = latex_to_text(
                action["latex"]
            )

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

            jx = random.randint(-2,2)
            jy = random.randint(-1,1)

            draw.text(
                (
                    action["x"] + jx,
                    action["y"] + jy
                ),
                visible_text,
                fill=(20,20,20),
                font=font
            )

    # ==================================
    # SAVE
    # ==================================

    img.convert("RGB").save(
        f"{OUTPUT_DIR}/frame_{frame_no:05d}.png"
    )

    if frame_no % 100 == 0:

        print(
            f"Generated "
            f"{frame_no}/"
            f"{TOTAL_FRAMES}"
        )

print("\n✅ All frames generated!")