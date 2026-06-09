from svgpathtools import svg2paths
import cv2
import numpy as np
import os

# Load SVG
svg_file = "assets/test.svg"

# Check file exists
if not os.path.exists(svg_file):
    print(f"Error: {svg_file} not found")
    exit()

# Read paths
paths, attributes = svg2paths(svg_file)

# Output folder
os.makedirs("svg_frames", exist_ok=True)

# White canvas
canvas = np.ones((720, 1280, 3), dtype=np.uint8) * 255

frame_id = 0

for path in paths:

    prev_point = None

    # Sample points along SVG path
    for t in np.linspace(0, 1, 300):

        point = path.point(t)

        x = int(point.real)
        y = int(point.imag)

        if prev_point is not None:

            cv2.line(
                canvas,
                prev_point,
                (x, y),
                (0, 0, 0),
                3,
                cv2.LINE_AA
            )

            cv2.imwrite(
                f"svg_frames/frame_{frame_id:04d}.png",
                canvas
            )

            frame_id += 1

        prev_point = (x, y)

print(f"Done! Generated {frame_id} frames.")