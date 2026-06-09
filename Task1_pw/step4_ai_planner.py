import json
import os
import re
from dotenv import load_dotenv
import google.generativeai as genai

# -----------------------------------
# Load Gemini
# -----------------------------------

load_dotenv()

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

model = genai.GenerativeModel(
    "gemini-2.5-flash"
)

# -----------------------------------
# Load Transcript
# -----------------------------------

with open(
    "transcript.json",
    "r",
    encoding="utf-8"
) as f:
    transcript = json.load(f)

# -----------------------------------
# Load OCR
# -----------------------------------

with open(
    "ocr_results.json",
    "r",
    encoding="utf-8"
) as f:
    ocr = json.load(f)

# -----------------------------------
# Prompt
# -----------------------------------

prompt = f"""
You are an expert educational video planner.

Your job is to convert:

1. Transcript with timestamps
2. OCR output

into a teaching timeline.

Video resolution:
1280x720

Question Area:
x = 0 to 420

Solution Area:
x = 450 to 1200

Generate actions that mimic a real teacher.

Allowed actions:

1. highlight
2. circle
3. latex
4. underline
5. arrow

IMPORTANT:

Whenever a mathematical expression,
formula,
equation,
substitution,
simplification,
or final answer appears,

DO NOT use "write".

Instead use:

"action": "latex"

and generate valid LaTeX.

Examples:

Distance Formula:

{{
    "action":"latex",
    "latex":"D=\\\\sqrt{{(x_2-x_1)^2+(y_2-y_1)^2}}"
}}

Substitution:

{{
    "action":"latex",
    "latex":"D=\\\\sqrt{{(4-1)^2+(6-2)^2}}"
}}

Simplification:

{{
    "action":"latex",
    "latex":"D=\\\\sqrt{{3^2+4^2}}"
}}

Next:

{{
    "action":"latex",
    "latex":"D=\\\\sqrt{{9+16}}"
}}

Final:

{{
    "action":"latex",
    "latex":"D=5\\ units"
}}

Rules:

1. Highlight question when teacher reads it.
2. Highlight options when teacher reads them.
3. Circle correct option when answer is confirmed.
4. Keep annotations persistent.
5. Generate coordinates for every action.
6. Solution steps should appear one below another.
7. Return ONLY JSON.
8. No markdown.
9. No explanation.

Output Format:

[
  {{
    "start": 0,
    "end": 5,
    "action": "highlight",
    "content": "question",
    "x": 20,
    "y": 50,
    "x_end": 800,
    "y_end": 120
  }},

  {{
    "start": 15,
    "end": 25,
    "action": "latex",
    "latex": "D=\\\\sqrt{{(x_2-x_1)^2+(y_2-y_1)^2}}",
    "x": 470,
    "y": 120
  }}
]

Transcript:

{json.dumps(transcript["segments"], indent=2)}

OCR:

{json.dumps(ocr, indent=2)}
"""

# -----------------------------------
# Gemini Call
# -----------------------------------

response = model.generate_content(
    prompt
)

raw_text = response.text

print("\nGemini Output:\n")
print(raw_text)

# -----------------------------------
# Clean JSON
# -----------------------------------

cleaned = re.sub(
    r"^```json|```$",
    "",
    raw_text.strip(),
    flags=re.MULTILINE
).strip()

# -----------------------------------
# Save Timeline
# -----------------------------------

with open(
    "timeline.json",
    "w",
    encoding="utf-8"
) as f:
    f.write(cleaned)

print("\n✅ timeline.json saved")