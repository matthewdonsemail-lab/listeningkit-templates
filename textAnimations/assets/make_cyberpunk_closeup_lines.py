"""Cyberpunk close-ups: thin cyberpsycho lines in three depth layers over her face, kept clear of the face itself.
Each layer is its own transparent ProRes 4444 (assets/collage/cyberpunk_lines_<far|mid|near>.mov, 3.2 s, new drawing
every 2 frames), focused for its depth: far small and a touch soft, mid sharp with a fine black edge, near big and
out of focus. The comp pushes each at its own rate, so the camera moving in on her gives them parallax."""
import os
import subprocess
import sys

import cv2
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "plugins", "cyberpsycho"))
import cyberpsycho  # noqa: E402

OUT = "C:/Users/0/.buzz/REPOS/listeningkit-templates/textAnimations/assets/collage/cyberpunk_lines_%s.mov"
W, H, FPS, FRAMES = 1920, 1080, 30, 183  # as make_cyberpunk_closeups.py
FACE = (960, 540, 560, 400)  # the oval her eyes, nose and mouth sit in, kept clear
LAYERS = {  # width scale, density, blur sigma, outline px, opacity
    "far": (0.55, 0.55, 1.4, 1, 0.7),
    "mid": (0.9, 0.45, 0.0, 1, 0.95),
    "near": (2.4, 0.3, 9.0, 0, 0.8),
}
COLOR = (225, 240, 255)  # near-white, so under the CRT they read as its own highlights


def soften(rgba, sigma):
    """depth of field: blur premultiplied colour and alpha together so the edges stay clean"""
    if sigma <= 0:
        return rgba
    a = rgba[:, :, 3:4].astype(np.float32) / 255.0
    pre = rgba[:, :, :3].astype(np.float32) * a
    k = int(sigma * 3) * 2 + 1
    pre, a = cv2.GaussianBlur(pre, (k, k), sigma), cv2.GaussianBlur(a, (k, k), sigma)[:, :, None]
    out = np.zeros_like(rgba)
    out[:, :, :3] = np.clip(pre / np.maximum(a, 1e-4), 0, 255).astype(np.uint8)
    out[:, :, 3] = np.clip(a[:, :, 0] * 255, 0, 255).astype(np.uint8)
    return out


for name, (ws, dens, sigma, ol, op) in LAYERS.items():
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", "%dx%d" % (W, H),
                          "-r", str(FPS), "-i", "-", "-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", "yuva444p10le",
                          OUT % name], stdin=subprocess.PIPE)
    held = None
    for f in range(FRAMES):
        if f % 2 == 0:
            fr = cyberpsycho.frame("closeup %s %d" % (name, f // 2), (W, H), None, COLOR, dens, outline=(0, 0, 0),
                                   outline_px=ol, thin=True, width_scale=ws, avoid=FACE)
            fr = cyberpsycho.glitch(fr, "closeup %s %d" % (name, f), 0.8)
            fr = soften(fr, sigma)
            fr[:, :, 3] = (fr[:, :, 3].astype(np.float32) * op).astype(np.uint8)
            held = fr
        p.stdin.write(held.tobytes())
    p.stdin.close()
    p.wait()
    print(name, "->", OUT % name)
