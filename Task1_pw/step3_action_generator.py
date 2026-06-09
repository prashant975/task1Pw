import json

print("Loading transcript...")

with open("transcript.json", "r", encoding="utf-8") as f:
    transcript = json.load(f)

segments = transcript["segments"]

actions = []

for seg in segments:

    text = seg["text"].lower()
    start_time = round(seg["start"])

    # Question reading
    if "question reads" in text or "find the distance" in text:
        actions.append({
            "time": start_time,
            "action": "highlight_question"
        })

    # Options
    elif "options are" in text:
        actions.append({
            "time": start_time,
            "action": "highlight_options"
        })

    # Formula
    elif "under root of x 2 minus x 1" in text:
        actions.append({
            "time": start_time,
            "action": "write",
            "text": "d = sqrt((x2-x1)^2 + (y2-y1)^2)"
        })

    # Substitution
    elif "x 2 as 4" in text:
        actions.append({
            "time": start_time,
            "action": "write",
            "text": "= sqrt((4-1)^2 + (6-2)^2)"
        })

    # 3² + 4²
    elif "3 square" in text:
        actions.append({
            "time": start_time,
            "action": "write",
            "text": "= sqrt(3^2 + 4^2)"
        })

    # 9 + 16
    elif "9 plus 16" in text:
        actions.append({
            "time": start_time,
            "action": "write",
            "text": "= sqrt(9 + 16)"
        })

    # Final Answer
    elif "5 units" in text:
        actions.append({
            "time": start_time,
            "action": "write",
            "text": "= 5 units"
        })

    # Option C
    elif "option number c" in text:
        actions.append({
            "time": start_time,
            "action": "circle_option_c"
        })

with open(
    "teacher_actions.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        actions,
        f,
        indent=4
    )

print("teacher_actions.json created!")
print("\nGenerated Actions:\n")

for action in actions:
    print(action)