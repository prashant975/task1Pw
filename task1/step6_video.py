import cv2
import os

frame_folder = "frames"

frames = sorted(os.listdir(frame_folder))

first = cv2.imread(
    os.path.join(
        frame_folder,
        frames[0]
    )
)

height, width, _ = first.shape

video = cv2.VideoWriter(
    "output.mp4",
    cv2.VideoWriter_fourcc(*'mp4v'),
    10,
    (width, height)
)

for frame in frames:

    img = cv2.imread(
        os.path.join(
            frame_folder,
            frame
        )
    )

    video.write(img)

video.release()

print("Video Created")
