import json
import os
from typing import Dict, List, Tuple, Optional

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# ============================================================
# CLEAN PW-STYLE RENDERER
# - Uses the original question image as the canvas
# - No split screen
# - Marker-style highlights
# - Option-by-option highlighting
# - Progressive handwriting
# - Persistent visible solution
# - Progressive answer circle
# ============================================================

FPS = 30
WIDTH = 1280
HEIGHT = 720

QUESTION_IMAGE_PATH = "QuestionPPT.pptx.png"
TIMELINE_PATH = "timeline.json"
OCR_PATH = "ocr_results.json"
FONT_PATH = os.path.join("fonts", "Kalam-Regular.ttf")
FRAMES_DIR = "frames"

os.makedirs(FRAMES_DIR, exist_ok=True)

# ------------------------------------------------------------
# Layout
# ------------------------------------------------------------

QUESTION_BOX_DEFAULT = (28, 65, 896, 117)
OPTION_BOX_DEFAULTS = {
    "A": (24, 140, 198, 188),
    "B": (25, 195, 195, 239),
    "C": (24, 246, 196, 294),
    "D": (24, 300, 198, 348),
}

# Clean writing area on the right side of the slide
POSITIONS = {
    "write_heading_formula": (690, 120),
    "write_formula": (690, 175),
    "write_heading_substitution": (690, 265),
    "write_substitution": (690, 320),
    "write_simplification": (690, 425),
    "write_final_answer": (690, 555),
}

COLORS = {
    "write_heading_formula": "#0b3d91",
    "write_formula": "#1f5eff",
    "write_heading_substitution": "#0b3d91",
    "write_substitution": "#111111",
    "write_simplification": "#111111",
    "write_final_answer": "#118a31",
}

FONT_SIZES = {
    "write_heading_formula": 26,
    "write_formula": 30,
    "write_heading_substitution": 26,
    "write_substitution": 30,
    "write_simplification": 30,
    "write_final_answer": 38,
}

TEXT_ORDER = [
    "write_heading_formula",
    "write_formula",
    "write_heading_substitution",
    "write_substitution",
    "write_simplification",
    "write_final_answer",
]


# ------------------------------------------------------------
# Utilities
# ------------------------------------------------------------

def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def ensure_file_exists(path: str, label: str) -> None:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing {label}: {path}")


def load_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def make_font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_PATH, size)


def load_question_image() -> Image.Image:
    ensure_file_exists(QUESTION_IMAGE_PATH, "question image")
    img = cv2.imread(QUESTION_IMAGE_PATH)
    if img is None:
        raise RuntimeError(f"Could not read image: {QUESTION_IMAGE_PATH}")
    img = cv2.resize(img, (WIDTH, HEIGHT))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return Image.fromarray(img).convert("RGBA")


def load_timeline() -> List[dict]:
    ensure_file_exists(TIMELINE_PATH, "timeline file")
    timeline = load_json(TIMELINE_PATH)
    if not isinstance(timeline, list) or not timeline:
        raise ValueError("timeline.json must contain a non-empty list")
    return sorted(timeline, key=lambda x: float(x.get("start", 0.0)))


def bbox_bounds(bbox: List[List[float]], pad: int = 0) -> Tuple[int, int, int, int]:
    xs = [pt[0] for pt in bbox]
    ys = [pt[1] for pt in bbox]
    return (
        int(min(xs) - pad),
        int(min(ys) - pad),
        int(max(xs) + pad),
        int(max(ys) + pad),
    )


def union_bounds(
    boxes: List[Tuple[int, int, int, int]],
    pad: int = 0
) -> Tuple[int, int, int, int]:
    xs1 = [b[0] for b in boxes]
    ys1 = [b[1] for b in boxes]
    xs2 = [b[2] for b in boxes]
    ys2 = [b[3] for b in boxes]
    return (
        int(min(xs1) - pad),
        int(min(ys1) - pad),
        int(max(xs2) + pad),
        int(max(ys2) + pad),
    )


def load_ocr_boxes() -> Dict[str, Tuple[int, int, int, int]]:
    """
    Best-effort OCR box loader. Falls back to known sample coordinates.
    """
    default_boxes = {
        "question": QUESTION_BOX_DEFAULT,
        "A": OPTION_BOX_DEFAULTS["A"],
        "B": OPTION_BOX_DEFAULTS["B"],
        "C": OPTION_BOX_DEFAULTS["C"],
        "D": OPTION_BOX_DEFAULTS["D"],
    }

    if not os.path.exists(OCR_PATH):
        return default_boxes

    try:
        data = load_json(OCR_PATH)
    except Exception:
        return default_boxes

    if not isinstance(data, list):
        return default_boxes

    found: Dict[str, Tuple[int, int, int, int]] = {}

    for item in data:
        try:
            text = str(item.get("text", "")).strip()
            bbox = item.get("bbox")
            if not bbox:
                continue

            bounds = bbox_bounds(bbox, pad=4)
            low = text.lower()

            if "find the distance between the points" in low or low.startswith("find distance"):
                found["question"] = bounds
            elif low.startswith("(a)") or low.startswith("a)"):
                found["A"] = bounds
            elif low.startswith("(b)") or low.startswith("b)"):
                found["B"] = bounds
            elif low.startswith("(c)") or low.startswith("c)"):
                found["C"] = bounds
            elif low.startswith("(d)") or low.startswith("d)"):
                found["D"] = bounds
        except Exception:
            continue

    for key, value in default_boxes.items():
        found.setdefault(key, value)

    return found


def draw_marker_highlight(
    base: Image.Image,
    box: Tuple[int, int, int, int],
    progress: float,
    fill_rgba: Tuple[int, int, int, int] = (255, 245, 0, 100),
) -> Image.Image:
    """
    Marker/highlighter sweep. No outline box.
    """
    x1, y1, x2, y2 = box
    progress = clamp(progress, 0.0, 1.0)
    current_x = int(x1 + (x2 - x1) * progress)

    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    pad_y = 8
    if current_x > x1:
        draw.rounded_rectangle(
            [x1 - 6, y1 - pad_y, current_x + 4, y2 + pad_y],
            radius=10,
            fill=fill_rgba,
        )

    draw.ellipse(
        [current_x - 16, y1 - 2, current_x + 10, y2 + 2],
        fill=(255, 235, 59, 120),
    )

    return Image.alpha_composite(base, overlay)


def draw_progressive_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    x: int,
    y: int,
    progress: float,
    font: ImageFont.FreeTypeFont,
    fill: str,
) -> int:
    """
    Draw text progressively and return visible text width.
    """
    progress = clamp(progress, 0.0, 1.0)
    visible_chars = int(len(text) * (progress ** 0.65))
    partial = text[:visible_chars]

    draw.text((x, y), partial, font=font, fill=fill)

    if partial:
        bbox = draw.textbbox((x, y), partial, font=font)
        return bbox[2] - bbox[0]
    return 0


def draw_pen_cursor(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    text_width: int,
    font: ImageFont.FreeTypeFont,
    fill: str = "black",
) -> None:
    cursor_x = x + text_width + 8
    cursor_y = y + int(font.size * 0.75)

    # small pen-tip style cursor
    draw.line(
        [(cursor_x - 7, cursor_y - 7), (cursor_x + 3, cursor_y + 3)],
        fill=fill,
        width=3,
    )
    draw.ellipse(
        [cursor_x + 2, cursor_y + 2, cursor_x + 6, cursor_y + 6],
        fill=fill,
    )


def draw_full_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    x: int,
    y: int,
    font: ImageFont.FreeTypeFont,
    fill: str,
) -> None:
    draw.text((x, y), text, font=font, fill=fill)


def draw_progressive_circle(
    draw: ImageDraw.ImageDraw,
    box: Tuple[int, int, int, int],
    progress: float,
    fill: str = "red",
    width: int = 6,
) -> None:
    progress = clamp(progress, 0.0, 1.0)
    if progress >= 1.0:
        draw.ellipse(box, outline=fill, width=width)
    else:
        draw.arc(box, start=0, end=int(360 * progress), fill=fill, width=width)


def draw_static_circle(
    draw: ImageDraw.ImageDraw,
    box: Tuple[int, int, int, int],
    fill: str = "red",
    width: int = 6,
) -> None:
    draw.ellipse(box, outline=fill, width=width)


def option_circle_box(
    boxes: Dict[str, Tuple[int, int, int, int]],
    option: str
) -> Tuple[int, int, int, int]:
    b = boxes.get(option.upper(), OPTION_BOX_DEFAULTS.get(option.upper(), OPTION_BOX_DEFAULTS["C"]))
    return (b[0] - 12, b[1] - 8, b[2] + 12, b[3] + 10)


def highlight_box_for_action(
    action_name: str,
    ocr_boxes: Dict[str, Tuple[int, int, int, int]],
) -> Optional[Tuple[int, int, int, int]]:
    if action_name == "highlight_question":
        return ocr_boxes.get("question", QUESTION_BOX_DEFAULT)

    if action_name == "highlight_options":
        option_boxes = [ocr_boxes.get(k) for k in ("A", "B", "C", "D")]
        option_boxes = [b for b in option_boxes if b is not None]
        return union_bounds(option_boxes, pad=8) if option_boxes else None

    if action_name == "highlight_option_a":
        return ocr_boxes.get("A", OPTION_BOX_DEFAULTS["A"])

    if action_name == "highlight_option_b":
        return ocr_boxes.get("B", OPTION_BOX_DEFAULTS["B"])

    if action_name == "highlight_option_c":
        return ocr_boxes.get("C", OPTION_BOX_DEFAULTS["C"])

    if action_name == "highlight_option_d":
        return ocr_boxes.get("D", OPTION_BOX_DEFAULTS["D"])

    return None


# ------------------------------------------------------------
# Main rendering
# ------------------------------------------------------------

def main() -> None:
    ensure_file_exists(FONT_PATH, "font file")

    timeline = load_timeline()
    ocr_boxes = load_ocr_boxes()
    base_question = load_question_image()

    duration = float(timeline[-1]["end"])
    total_frames = int(duration * FPS) + 1

    print(f"Generating {total_frames} frames...")
    print("Using clean slide annotation layout...")

    fonts: Dict[int, ImageFont.FreeTypeFont] = {
        size: make_font(size)
        for size in sorted(set(FONT_SIZES.values()) | {24, 26, 30, 38})
    }

    # Make sure optional actions are supported
    highlight_actions = {
        "highlight_question",
        "highlight_options",
        "highlight_option_a",
        "highlight_option_b",
        "highlight_option_c",
        "highlight_option_d",
    }

    for frame_idx in range(total_frames):
        current_time = frame_idx / FPS

        frame = base_question.copy()

        # ----------------------------------------------------
        # Highlights first
        # ----------------------------------------------------
        for action in timeline:
            name = action.get("action")

            if name not in highlight_actions:
                continue

            start = float(action.get("start", 0.0))
            end = float(action.get("end", start + 1.0))

            if current_time < start:
                continue

            progress = 1.0 if current_time >= end else (current_time - start) / max(1e-6, end - start)
            box = highlight_box_for_action(name, ocr_boxes)

            if box is None:
                continue

            frame = draw_marker_highlight(
                frame,
                box,
                progress,
                fill_rgba=(255, 245, 0, 100),
            )

        draw = ImageDraw.Draw(frame)

        # ----------------------------------------------------
        # Solution text
        # ----------------------------------------------------
        for action in timeline:
            name = action.get("action")

            if name not in TEXT_ORDER:
                continue

            if "content" not in action:
                continue

            text = str(action["content"])
            start = float(action.get("start", 0.0))
            end = float(action.get("end", start + 1.0))
            x, y = POSITIONS[name]
            color = COLORS[name]
            font = fonts[FONT_SIZES[name]]

            # Keep completed text visible
            if current_time > end:
                draw_full_text(draw, text, x, y, font, color)
                continue

            # Animate only during the active interval
            if start <= current_time <= end:
                progress = (current_time - start) / max(1e-6, end - start)
                text_width = draw_progressive_text(draw, text, x, y, progress, font, color)

                # No cursor for headings; cleaner
                if name not in ("write_heading_formula", "write_heading_substitution"):
                    draw_pen_cursor(draw, x, y, text_width, font, fill=color)

        # ----------------------------------------------------
        # Answer circle
        # ----------------------------------------------------
        for action in timeline:
            if action.get("action") != "circle_correct_option":
                continue

            start = float(action.get("start", 0.0))
            end = float(action.get("end", start + 1.0))
            option = str(action.get("option", "C")).upper()
            circ_box = option_circle_box(ocr_boxes, option)

            if current_time < start:
                continue
            elif current_time > end:
                draw_static_circle(draw, circ_box, fill="red", width=6)
            else:
                progress = (current_time - start) / max(1e-6, end - start)
                draw_progressive_circle(draw, circ_box, progress, fill="red", width=6)

        # Save frame
        out = cv2.cvtColor(np.array(frame.convert("RGB")), cv2.COLOR_RGB2BGR)
        out_path = os.path.join(FRAMES_DIR, f"frame_{frame_idx:05d}.png")
        cv2.imwrite(out_path, out)

        if frame_idx % 100 == 0:
            print(f"{frame_idx}/{total_frames}")

    print("Frames Generated Successfully")


if __name__ == "__main__":
    main()