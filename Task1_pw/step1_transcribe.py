import whisper
import json

print("Loading Whisper...")

model = whisper.load_model("base")

print("Transcribing...")

result = model.transcribe(
    "Audio.mpeg",
    word_timestamps=True
)

# Save full transcript
with open(
    "transcript.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        result,
        f,
        indent=4,
        ensure_ascii=False
    )

print("Transcript saved.")