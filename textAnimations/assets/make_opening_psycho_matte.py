"""The opening's two cyberpsycho shots with the men cut off their backgrounds (matt, 2026-11-15), so the backgrounds can
be glitch-cut behind them (make_opening_psycho_cut.py). OpenCV GrabCut, as make_cyberpunk_matte.py does it: seeded
from a head-and-shoulders shape drawn round him: its middle sure foreground, the shape probable foreground, a band
round it probable background, everything else sure background; then the biggest piece kept, holes filled and the edge softened.
Writes projects/opening/psycho/<shot>_matte.png (8-bit alpha at the shot's own 1672x941)."""
import os

import cv2
import numpy as np

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OP = os.path.join(ROOT, "projects", "opening")
SHOTS = {
    # the shot; his head (centre, axes) and shoulders (polygon), in image pixels, read off the frame
    "blinds": ("mattgen/Through the Blinds, Wired In Silence.png", ((825, 325), (305, 345)),
               [(470, 610), (1180, 610), (1520, 941), (130, 941)]),
    "chalk": ("mattgen/Intense Gaze Before the Chalkboard.png", ((820, 380), (300, 400)),
              [(480, 590), (1160, 590), (1672, 840), (1672, 941), (170, 941), (250, 760)]),
}

for s, (path, (hc, ha), body) in SHOTS.items():
    im = cv2.imread(os.path.join(OP, path))
    H, W = im.shape[:2]
    shape = np.zeros((H, W), np.uint8)
    cv2.ellipse(shape, hc, ha, 0, 0, 360, 255, -1)
    cv2.fillPoly(shape, [np.array(body, np.int32)], 255)
    near = cv2.dilate(shape, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (81, 81)))
    core = cv2.erode(shape, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (121, 121)))
    mask = np.full((H, W), cv2.GC_BGD, np.uint8)  # outside the head and shoulders: sure background
    mask[near > 0] = cv2.GC_PR_BGD
    mask[shape > 0] = cv2.GC_PR_FGD
    mask[core > 0] = cv2.GC_FGD
    bgd, fgd = np.zeros((1, 65), np.float64), np.zeros((1, 65), np.float64)
    cv2.grabCut(im, mask, None, bgd, fgd, 8, cv2.GC_INIT_WITH_MASK)
    alpha = np.where((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 255, 0).astype(np.uint8)
    n, labels, stats, _ = cv2.connectedComponentsWithStats(alpha)
    if n > 1:
        alpha = np.where(labels == 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA])), 255, 0).astype(np.uint8)
    alpha = cv2.morphologyEx(alpha, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25)))
    # fill holes: flood the background in from a 1 px border round the frame, so background on either side of him
    # (he touches the top and bottom) counts as outside, and only what it can't reach is a hole
    holes = cv2.copyMakeBorder(alpha, 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=0)
    ff = np.zeros((H + 4, W + 4), np.uint8)
    cv2.floodFill(holes, ff, (0, 0), 255)
    alpha = alpha | cv2.bitwise_not(holes[1:-1, 1:-1])
    alpha = cv2.GaussianBlur(alpha, (7, 7), 0)
    dest = os.path.join(OP, "psycho", "%s_matte.png" % s)
    cv2.imwrite(dest, alpha)
    print("wrote", dest)
