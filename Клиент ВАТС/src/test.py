from datetime import datetime
import os
import cv2


def capture_photo(save_dir="./Photos"):

    os.makedirs(save_dir, exist_ok=True)

    cap = cv2.VideoCapture("/dev/video0")
    if not cap.isOpened():
        return None, None

    ret, frame = cap.read()
    cap.release()

    if not ret:
        return None, None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
    filepath = os.path.join(save_dir, f"frame_{timestamp}.jpg")
    cv2.imwrite(filepath, frame)

    print(ret, frame)
    return filepath, frame


capture_photo()
