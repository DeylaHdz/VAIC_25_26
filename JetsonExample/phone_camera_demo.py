"""Standalone demo: run the trained Override detection model on a phone's IP
camera stream (e.g. DroidCam) instead of the RealSense camera. No V5 Brain,
GPS, or depth data involved - just live detection + on-screen boxes/labels.

Usage:
    python3 phone_camera_demo.py <camera_url>

Example (DroidCam on Android, phone IP 10.50.15.92, default port 4747):
    python3 phone_camera_demo.py http://10.50.15.92:4747/video
"""
import sys
import time

import cv2
import numpy as np

from model import Model
from data_processing import ALL_CATEGORIES


def class_color(class_id, num_classes):
    hue = int(179 * class_id / max(num_classes, 1))
    hsv_pixel = np.uint8([[[hue, 255, 255]]])
    bgr_pixel = cv2.cvtColor(hsv_pixel, cv2.COLOR_HSV2BGR)[0][0]
    return tuple(int(c) for c in bgr_pixel)


def draw_detections(frame_bgr, detections):
    for det in detections:
        x1, y1 = det.x, det.y
        x2, y2 = det.x + det.Width, det.y + det.Height
        color = class_color(det.ClassID, len(ALL_CATEGORIES))
        label = f"{ALL_CATEGORIES[det.ClassID]} {det.Prob:.2f}"
        cv2.rectangle(frame_bgr, (x1, y1), (x2, y2), color, 2)
        cv2.putText(frame_bgr, label, (x1, max(0, y1 - 8)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    return frame_bgr


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 phone_camera_demo.py <camera_url>")
        print("Example (DroidCam): python3 phone_camera_demo.py http://<phone-ip>:4747/video")
        sys.exit(1)

    url = sys.argv[1]
    cap = cv2.VideoCapture(url)
    if not cap.isOpened():
        print(f"Could not open camera stream at {url}")
        print("Check that DroidCam is running on the phone and both devices share the same Wi-Fi network.")
        sys.exit(1)

    print("Loading model (first run builds the TensorRT engine, this can take a few minutes)...")
    model = Model()
    print("Model ready. Press 'q' or ESC in the video window to quit.")

    try:
        while True:
            ok, frame_bgr = cap.read()
            if not ok:
                print("Lost connection to camera stream, reconnecting...")
                cap.release()
                time.sleep(1)
                cap = cv2.VideoCapture(url)
                continue

            frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
            _, detections = model.inference(frame_rgb)

            for det in detections:
                print(f"{ALL_CATEGORIES[det.ClassID]}: {det.Prob:.2f} "
                      f"at ({det.x}, {det.y}) {det.Width}x{det.Height}")

            output = draw_detections(frame_bgr, detections)
            cv2.imshow("VEX Override - Phone Camera", output)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q") or key == 27:
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
