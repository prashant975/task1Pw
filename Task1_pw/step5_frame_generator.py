from PIL import Image, ImageDraw, ImageFont
import json

CURRENT_TIME = 20

img = Image.open("QuestionPPT.pptx.png").convert("RGB")
draw = ImageDraw.Draw(img)

# OCR
with open("ocr_results.json", "r", encoding="utf-8") as f:
    ocr = json.load(f)

# Timeline
with open("timeline.json", "r", encoding="utf-8") as f:
    timeline = json.load(f)

try:
    font = ImageFont.truetype("arial.ttf", 32)
except:
    font = ImageFont.load_default()

# ------------------
# Highlight Question
# ------------------

for action in timeline:

    start = action["start"]
    end = action["end"]

    if start <= CURRENT_TIME:

        if action["action"] == "highlight":

            target = action["content"]

            for item in ocr:

                if target.lower() in item["text"].lower():

                    box = item["bbox"]

                    draw.rectangle(
                        [
                            tuple(box[0]),
                            tuple(box[2])
                        ],
                        outline="red",
                        width=4
                    )

# ------------------
# Writing Area
# ------------------

write_x = 500
write_y = 150

for action in timeline:

    if action["action"] != "write":
        continue

    start = action["start"]
    end = action["end"]

    text = action["content"]

    if CURRENT_TIME < start:
        continue

    # fully visible
    if CURRENT_TIME >= end:

        draw.text(
            (write_x, write_y),
            text,
            fill="black",
            font=font
        )

        write_y += 60

    else:

        progress = (
            CURRENT_TIME - start
        ) / (
            end - start
        )

        chars = int(
            len(text) * progress
        )

        partial = text[:chars]

        draw.text(
            (write_x, write_y),
            partial,
            fill="black",
            font=font
        )

        write_y += 60

img.save("frame_preview.png")

print("frame_preview.png generated")