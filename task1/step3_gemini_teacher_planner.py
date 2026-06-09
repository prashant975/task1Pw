import json
import google.generativeai as genai

# ==========================
# GEMINI API KEY
# ==========================

GEMINI_API_KEY = "AQ.Ab8RN6KOX12F-kUkIr7WVh8O2Pm4gW7TsAqF4PqCDwNqafpaQg"

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel(
    "gemini-2.5-flash"
)

# ==========================
# LOAD OCR
# ==========================

with open(
    "ocr_results.json",
    "r",
    encoding="utf-8"
) as f:

    ocr_data = json.load(f)

# ==========================
# LOAD TRANSCRIPT
# ==========================

with open(
    "transcript.json",
    "r",
    encoding="utf-8"
) as f:

    transcript_data = json.load(f)

# ==========================
# PREPARE INPUT
# ==========================

ocr_text = "\n".join(
    item["text"]
    for item in ocr_data
)

transcript_text = json.dumps(
    transcript_data,
    indent=2
)

# ==========================
# PROMPT
# ==========================

prompt = f"""
You are an expert Physics Wallah teacher.

Your task is to create a teaching timeline.

QUESTION OCR:

{ocr_text}

TRANSCRIPT:

{transcript_text}

Generate JSON only.

Supported Actions:

highlight_question
highlight_options
write_formula_heading
write_formula
write_substitution
write_simplification
write_final_answer
circle_correct_option

Return format:

[
 {{
   "start":0,
   "end":5,
   "action":"highlight_question"
 }}
]

Do not explain.

Return JSON only.
"""

# ==========================
# GEMINI CALL
# ==========================

print("Generating Teaching Timeline...")

response = model.generate_content(
    prompt
)

timeline_text = response.text

# Remove markdown if Gemini adds it

timeline_text = timeline_text.replace(
    "```json",
    ""
)

timeline_text = timeline_text.replace(
    "```",
    ""
)

timeline_text = timeline_text.strip()

# ==========================
# SAVE
# ==========================

with open(
    "timeline.json",
    "w",
    encoding="utf-8"
) as f:

    f.write(timeline_text)

print("\nTimeline Generated")
print("Saved: timeline.json")