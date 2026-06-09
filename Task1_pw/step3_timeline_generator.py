import json

print("Loading transcript...")

with open("transcript.json", "r", encoding="utf-8") as f:
    data = json.load(f)

segments = data["segments"]

timeline = []

for seg in segments:

    text = seg["text"].lower()

    start = seg["start"]
    end = seg["end"]

    # Question
    if "find the distance" in text:
        timeline.append({
            "start": start,
            "end": end,
            "action": "highlight_question"
        })

    # Options
    elif "options are" in text:
        timeline.append({
            "start": start,
            "end": end,
            "action": "highlight_options"
        })

    # Formula
    elif "under root of x 2 minus x 1" in text:
        timeline.append({
            "start": start,
            "end": end,
            "action": "write",
            "text": "d = sqrt((x2-x1)^2 + (y2-y1)^2)"
        })

    # Substitution
    elif "x 2 as 4" in text:
        timeline.append({
            "start": start,
            "end": end,
            "action": "write",
            "text": "= sqrt((4-1)^2 + (6-2)^2)"
        })

    # 3² + 4²
    elif "3 square" in text:
        timeline.append({
            "start": start,
            "end": end,
            "action": "write",
            "text": "= sqrt(3^2 + 4^2)"
        })

    # 9 + 16
    elif "9 plus 16" in text:
        timeline.append({
            "start": start,
            "end": end,
            "action": "write",
            "text": "= sqrt(9 + 16)"
        })

    # Final answer
    elif "5 units" in text:
        timeline.append({
            "start": start,
            "end": end,
            "action": "write",
            "text": "= 5 units"
        })

    # Option C
    elif "option number c" in text:
        timeline.append({
            "start": start,
            "end": end,
            "action": "circle_option_c"
        })

with open(
    "timeline.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        timeline,
        f,
        indent=4
    )

print("timeline.json generated!")