import easyocr
import json

print("Loading OCR Model...")

# Initialize OCR Reader
reader = easyocr.Reader(['en'])

# Image Path
image_path = "QuestionPPT.pptx.png"

print("Reading Question Image...")

# Perform OCR
results = reader.readtext(image_path)

ocr_output = []

for bbox, text, confidence in results:

    if confidence < 0.5:
        continue

    bbox_clean = []

    for point in bbox:
        bbox_clean.append([
            int(point[0]),
            int(point[1])
        ])

    item = {
        "text": text,
        "confidence": float(confidence),
        "bbox": bbox_clean
    }

    ocr_output.append(item)

print("\n===== EXTRACTED TEXT =====\n")

for item in ocr_output:
    print(item["text"])

# Save OCR Output
with open(
    "ocr_results.json",
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        ocr_output,
        file,
        indent=4,
        ensure_ascii=False
    )

print("\nOCR Completed Successfully")
print("Saved File: ocr_results.json")