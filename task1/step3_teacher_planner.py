import json

with open("transcript.json", "r", encoding="utf-8") as f:
    transcript = json.load(f)

timeline = []

for segment in transcript:

    text = segment["text"].lower()

    start = segment["start"]
    end = segment["end"]

    if "question reads" in text:

        timeline.append({
            "start": start,
            "end": end,
            "action": "highlight_question"
        })

    elif "options are" in text:

        timeline.append({
            "start": start,
            "end": end,
            "action": "highlight_options"
        })

    elif "distance between 2 points" in text:

        timeline.append({
            "start": start,
            "end": end,
            "action": "write_formula_heading"
        })

        timeline.append({
            "start": start,
            "end": end,
            "action": "write_formula"
        })

    elif "4 minus 1" in text:

        timeline.append({
            "start": start,
            "end": end,
            "action": "substitute_values"
        })

    elif "3 square plus 4 square" in text:

        timeline.append({
            "start": start,
            "end": end,
            "action": "simplify"
        })

    elif "5 units" in text:

        timeline.append({
            "start": start,
            "end": end,
            "action": "write_final_answer"
        })

    elif "option number" in text:

        timeline.append({
            "start": start,
            "end": end,
            "action": "circle_answer"
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

print("Timeline Generated")