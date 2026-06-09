import easyocr
import json

print("Loading OCR model...")

reader = easyocr.Reader(['en'])

print("Reading image...")

results = reader.readtext("QuestionPPT.pptx.png")

ocr_data = []

for item in results:

    bbox, text, confidence = item

    ocr_data.append({
        "text": str(text),
        "bbox": [[int(x), int(y)] for x, y in bbox],
        "confidence": float(confidence)
    })

    print(f"Text: {text}")
    print(f"Confidence: {confidence}")
    print("-" * 50)

with open(
    "ocr_results.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        ocr_data,
        f,
        indent=4,
        ensure_ascii=False
    )

print("OCR results saved to ocr_results.json")