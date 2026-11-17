"""Pulls the glitch effects out of a reference edit's frames as transparent layers (matt, 2026-11-15), so they can go
over our own shots. Each frame is split by what the effect is made of, with numpy / OpenCV:
  chroma   the saturated glitch colour (the red / green / yellow / magenta blocks and smears): alpha from saturation
  streaks  horizontal smears and pixel-sort runs: strong vertical edges with almost no horizontal change, dilated
           along the rows
  noise    the fine noise, scanlines and tearing: the frame minus its median blur (high frequency), its colour kept
  lines    thin bright strokes (lightning, light streaks): a white top-hat of the brightness
  fx       all four together (the strongest alpha wins)
Each layer is written as an RGBA PNG sequence and a ProRes 4444 .mov with alpha, next to the source frames.
  python textAnimations/assets/extract_fx.py <dir of f_NN.png> [<dir> ...]"""
import glob
import os
import subprocess
import sys

import cv2
import numpy as np


def smooth(x, a, b):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def layers(img):
    f = img.astype(np.float32) / 255
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
    s, v = hsv[:, :, 1] / 255, hsv[:, :, 2] / 255
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255
    out = {}
    out["chroma"] = smooth(s, 0.45, 0.8) * smooth(v, 0.3, 0.6)
    dx = np.abs(cv2.Sobel(g, cv2.CV_32F, 1, 0, ksize=3)); dy = np.abs(cv2.Sobel(g, cv2.CV_32F, 0, 1, ksize=3))
    hor = cv2.blur(dy, (31, 1)) - 1.5 * cv2.blur(dx, (31, 1))
    st = cv2.dilate(smooth(hor, 0.05, 0.25), np.ones((3, 41), np.uint8))
    out["streaks"] = cv2.GaussianBlur(st, (0, 0), 1.0)
    hp = np.abs(g - cv2.medianBlur((g * 255).astype(np.uint8), 5).astype(np.float32) / 255)
    out["noise"] = smooth(hp, 0.04, 0.18)
    th = cv2.morphologyEx(g, cv2.MORPH_TOPHAT, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15)))
    out["lines"] = smooth(th, 0.12, 0.35) * smooth(v, 0.5, 0.8)
    out["fx"] = np.maximum.reduce([out["chroma"], out["streaks"], out["noise"], out["lines"]])
    return {k: np.dstack([img, (np.clip(a, 0, 1) * 255).astype(np.uint8)]) for k, a in out.items()}


for d in sys.argv[1:]:
    files = sorted(glob.glob(os.path.join(d, "f_*.png")))
    name = os.path.basename(os.path.normpath(d))
    base = os.path.join(os.path.dirname(os.path.normpath(d)), "fx", name)
    for k in ("chroma", "streaks", "noise", "lines", "fx"):
        os.makedirs(os.path.join(base, k), exist_ok=True)
    for i, f in enumerate(files):
        for k, rgba in layers(cv2.imread(f)).items():
            cv2.imwrite(os.path.join(base, k, "f_%02d.png" % (i + 1)), rgba)
    for k in ("chroma", "streaks", "noise", "lines", "fx"):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", "24", "-i", os.path.join(base, k, "f_%02d.png"),
                        "-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", "yuva444p10le", os.path.join(base, "%s_%s.mov" % (name, k))], check=True)
    print(name, len(files), "frames ->", base)
