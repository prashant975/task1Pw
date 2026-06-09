from svgpathtools import svg2paths
import cv2
import numpy as np
import os

# Load SVG
paths, attributes = svg2paths("assets/test.svg")

# Output folder
os.makedirs("svg_frames", exist_ok=True)

# White canvas
width = 1280
height = 720

canvas = np.ones((height, width, 3), dtype=np.uint8) * 255

frame_id = 0

for path in paths:

    previous = None

    # sample 300 points along path
    for t in np.linspace(0, 1, 300):

        point = path.point(t)

        x = int(point.real)
        y = int(point.imag)

        if previous is not None:

            cv2.line(
                canvas,
                previous,
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

        previous = (x, y)

print("SVG handwriting frames generated!")