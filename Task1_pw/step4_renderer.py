from PIL import Image, ImageDraw, ImageFont
import json

# Load image
img = Image.open("QuestionPPT.pptx.png")
draw = ImageDraw.Draw(img)

# Load OCR
with open("ocr_results.json", "r", encoding="utf-8") as f:
    ocr = json.load(f)

# Load actions
with open("teacher_actions.json", "r", encoding="utf-8") as f:
    actions = json.load(f)

# Font
font = ImageFont.load_default()

# Drawing area
x = 500
y = 150

for action in actions:

    if action["action"] == "highlight_question":

        qbox = ocr[0]["bbox"]

        draw.rectangle(
            [
                tuple(qbox[0]),
                tuple(qbox[2])
            ],
            outline="red",
            width=4
        )

    elif action["action"] == "highlight_options":

        for i in range(1, 5):

            box = ocr[i]["bbox"]

            draw.rectangle(
                [
                    tuple(box[0]),
                    tuple(box[2])
                ],
                outline="blue",
                width=3
            )

    elif action["action"] == "write":

        draw.text(
            (x, y),
            action["text"],
            fill="black",
            font=font
        )

        y += 40

img.save("annotated_frame.png")

print("annotated_frame.png generated")