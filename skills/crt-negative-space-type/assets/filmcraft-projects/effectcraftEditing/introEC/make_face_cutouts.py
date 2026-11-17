"""matt cut out of his webcam background for the cold open's face shots (matt, 2026-11-16: "the full background video is
behind me, then me cut out onto a layer above the gradient"). For each face cut (face_cuts.json: comp start, comp end,
camera source in, all seconds), the camera frames at 30 fps, a person matte from rembg (u2net_human_seg, CPU), lightly
tightened and feathered. Writes cutouts/beat_NN/c_NNN.png (RGBA, 1280x720, the camera's own size).
  uv run --no-project --with "rembg[cpu]" --with "opencv-python-headless<5" --with "numpy<3" python make_face_cutouts.py"""
import glob
import json
import os
import shutil
import subprocess

import cv2
import numpy as np
from PIL import Image
from rembg import new_session, remove

HERE = os.path.dirname(os.path.abspath(__file__))
CAM = r"C:\Users\0\AppData\Roaming\so.cap.desktop\recordings\Generic PnP Monitor (Display) 2026-11-16 03.27 PM.cap\content\segments\segment-0\camera.mp4"
CUTS = [[b["p0"], b["p1"], b["src"]] for b in json.load(open(os.path.join(HERE, "beats.json")))]  # every intro line (matt: "me inside the frame" the whole time)
OUT = os.path.join(HERE, "cutouts")
if os.path.isdir(OUT):
    shutil.rmtree(OUT)
sess = new_session("u2net_human_seg")
for j, (a, b, src) in enumerate(CUTS):
    d = os.path.join(OUT, "beat_%02d" % (j + 1)); os.makedirs(d)
    n = int(round((b - a) * 30)) + 1
    subprocess.run(["ffmpeg", "-v", "error", "-ss", "%.4f" % src, "-i", CAM, "-frames:v", str(n), "-r", "30",
                    os.path.join(d, "src_%03d.png")], check=True)
    for k, f in enumerate(sorted(glob.glob(os.path.join(d, "src_*.png")))):
        img = Image.open(f).convert("RGB")
        m = np.array(remove(img, session=sess, only_mask=True)).astype(np.float32) / 255
        m = cv2.erode(m, np.ones((3, 3), np.uint8))                 # pull the edge in off the wall
        m = cv2.GaussianBlur(m, (0, 0), 1.2)                         # soft edge
        rgba = np.dstack([np.array(img), (np.clip(m, 0, 1) * 255).astype(np.uint8)])
        cv2.imwrite(os.path.join(d, "c_%03d.png" % k), cv2.cvtColor(rgba, cv2.COLOR_RGBA2BGRA))
        os.remove(f)
    print("beat", j + 1, n, "frames", flush=True)
