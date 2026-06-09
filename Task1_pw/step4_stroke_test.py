import cv2
import numpy as np
import os

# Create output folder
os.makedirs("frames", exist_ok=True)

# White canvas
canvas = np.ones((720, 1280, 3), dtype=np.uint8) * 255

# Simulated pen path
points = [
    (100, 100),
    (130, 120),
    (160, 140),
    (190, 160),
    (220, 180),
    (250, 200),
    (280, 220),
    (310, 240)
]

for i in range(1, len(points)):

    cv2.line(
        canvas,
        points[i-1],
        points[i],
        (0, 0, 0),
        4,
        cv2.LINE_AA
    )

    cv2.imwrite(
        f"frames/frame_{i:03d}.png",
        canvas
    )

print("Stroke animation frames generated!")