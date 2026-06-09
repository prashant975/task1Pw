from PIL import Image, ImageDraw, ImageFont
import json
import os

FONT_PATH = "fonts/Kalam-Regular.ttf"

CACHE_DIR = "handwriting_cache"

os.makedirs(
    CACHE_DIR,
    exist_ok=True
)

# --------------------
# Convert latex
# --------------------

def latex_to_text(latex):

    latex = latex.replace(
        "\\sqrt",
        "sqrt"
    )

    latex = latex.replace(
        "_1",
        "1"
    )

    latex = latex.replace(
        "_2",
        "2"
    )

    latex = latex.replace(
        "{",
        "("
    )

    latex = latex.replace(
        "}",
        ")"
    )

    latex = latex.replace(
        "\\ ",
        " "
    )

    return latex


# --------------------
# Load timeline
# --------------------

with open(
    "timeline.json",
    "r",
    encoding="utf-8"
) as f:

    timeline = json.load(f)

font = ImageFont.truetype(
    FONT_PATH,
    36
)

formula_index = 0

for action in timeline:

    if action["action"] != "latex":
        continue

    text = latex_to_text(
        action["latex"]
    )

    # create transparent image

    img = Image.new(
        "RGBA",
        (900,120),
        (255,255,255,0)
    )

    draw = ImageDraw.Draw(img)

    draw.text(
        (10,10),
        text,
        fill=(20,20,20),
        font=font
    )

    output = (
        f"{CACHE_DIR}/"
        f"formula_{formula_index}.png"
    )

    img.save(output)

    action["handwriting_image"] = output

    formula_index += 1

# update timeline

with open(
    "timeline.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        timeline,
        f,
        indent=4,
        ensure_ascii=False
    )

print(
    f"Generated "
    f"{formula_index} "
    f"handwriting images"
)