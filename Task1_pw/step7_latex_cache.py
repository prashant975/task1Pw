import json
import os
import matplotlib.pyplot as plt

# Create cache folder
os.makedirs("latex_cache", exist_ok=True)

# Load timeline
with open(
    "timeline.json",
    "r",
    encoding="utf-8"
) as f:
    timeline = json.load(f)

formula_index = 0

for action in timeline:

    if action["action"] != "latex":
        continue

    latex = action["latex"]

    fig = plt.figure(
        figsize=(8, 1)
    )

    plt.text(
        0.02,
        0.5,
        f"${latex}$",
        fontsize=30
    )

    plt.axis("off")

    output_path = (
        f"latex_cache/"
        f"formula_{formula_index}.png"
    )

    plt.savefig(
        output_path,
        bbox_inches="tight",
        transparent=True,
        dpi=300
    )

    plt.close()

    action["image"] = output_path

    formula_index += 1

# Save updated timeline

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
    f"Generated {formula_index} formula images"
)