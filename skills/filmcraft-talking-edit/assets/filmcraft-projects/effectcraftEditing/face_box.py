"""Where matt's face sits in the raw Cap camera (1280x720), median over the recording, for the bust-shot zoom."""
import subprocess, sys
import cv2, numpy as np
CAM = r"C:\Users\0\AppData\Roaming\so.cap.desktop\recordings\Generic PnP Monitor (Display) 2026-11-16 03.27 PM.cap\content\segments\segment-0\camera.mp4"
det = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
boxes = []
for t in range(60, 4000, 120):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", CAM, "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "gray", "-"], capture_output=True).stdout
    if len(raw) != 1280 * 720: continue
    g = np.frombuffer(raw, np.uint8).reshape(720, 1280)
    f = det.detectMultiScale(g, 1.1, 6, minSize=(80, 80))
    if len(f): boxes.append(max(f, key=lambda b: b[2] * b[3]))
b = np.median(np.array(boxes), axis=0)
x, y, w, h = b
print(f"faces found {len(boxes)}; median box x={x:.0f} y={y:.0f} w={w:.0f} h={h:.0f}; centre ({(x + w / 2) / 1280:.3f}, {(y + h / 2) / 720:.3f}) of frame, height {h / 720:.3f}")
