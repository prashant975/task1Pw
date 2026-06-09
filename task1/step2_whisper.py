import whisper
import json

print("===================================")
print("LOADING WHISPER MODEL")
print("===================================")

model = whisper.load_model("base")

print("\nModel Loaded Successfully")

audio_file = "Audio.mpeg"

print("\nStarting Transcription...")

result = model.transcribe(audio_file)

segments = []

print("\n========== TRANSCRIPT ==========\n")

for segment in result["segments"]:

    start = float(segment["start"])
    end = float(segment["end"])
    text = segment["text"].strip()

    print(
        f"[{start:.2f}s -> {end:.2f}s] {text}"
    )

    segments.append({
        "start": start,
        "end": end,
        "text": text
    })

with open(
    "transcript.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        segments,
        f,
        indent=4,
        ensure_ascii=False
    )

print("\n===================================")
print("TRANSCRIPT SAVED")
print("File: transcript.json")
print("===================================")