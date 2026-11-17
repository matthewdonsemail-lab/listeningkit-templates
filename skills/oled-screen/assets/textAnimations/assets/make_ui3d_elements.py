"""The UI elements for the ending's 3D scene (matt, 2026-11-16), recreated from the Cyberpunk 2077 main-menu UI
reference (projects/opening/ref/zdepth_ref/video.mp4, youtube QiCYtUZkZVw). Each element is its own sprite so it can
be its own 3D layer at its own depth in EffectCraft (plugins/endingUi3d.jsx); the glow, depth of field and camera are
done there. Colours measured off the frames: yellow (222, 238, 14), magenta (225, 0, 226), red (188, 20, 54), cyan
(19, 151, 219), background navy (7, 14, 26).
Writes assets/ui3d/<element>.png (RGBA):
  dots_grid      a field of round yellow dots
  plus_grid      yellow plus signs in a grid with corner ticks
  dashed_bar     a long run of yellow dashes of mixed lengths in a thin red frame
  chevron_bars   the two long yellow bars with stepped arrow ends, ruled inside
  grid_panel     a dark navy panel ruled with a fine cyan grid, cyan edge lines
  graph_box      a yellow frame with yellow / magenta signal lines and three ring icons
  red_stack      a small stack of red bars
  python textAnimations/assets/make_ui3d_elements.py"""
import math
import os
import random

import cv2
import numpy as np

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui3d")
Y, M, R, C = (14, 238, 222), (226, 0, 225), (54, 20, 188), (219, 151, 19)    # BGR
NAVY = (26, 14, 7)
rnd = random.Random("ui3d")
os.makedirs(OUT, exist_ok=True)


def canvas(w, h):
    return np.zeros((h, w, 4), np.uint8)


def ink(img, col):
    """draw on a 3-channel view, then set alpha from what was drawn"""
    return img


def save(name, bgr, alpha):
    cv2.imwrite(os.path.join(OUT, name + ".png"), np.dstack([bgr, alpha]))
    print(name, bgr.shape[1], "x", bgr.shape[0])


def layer(w, h):
    return np.zeros((h, w, 3), np.uint8), np.zeros((h, w), np.uint8)


# dots
b, a = layer(1400, 600)
for y in range(20, 600, 30):
    for x in range(20, 1400, 30):
        r = 6 if rnd.random() > 0.15 else 4
        cv2.circle(b, (x, y), r, Y, -1, cv2.LINE_AA); cv2.circle(a, (x, y), r, 255, -1, cv2.LINE_AA)
save("dots_grid", b, a)

# plus grid with ticks
b, a = layer(1200, 520)
for y in range(50, 470, 68):
    for x in range(60, 1150, 88):
        s = 18 if rnd.random() > 0.2 else 12
        for img, col in ((b, Y), (a, 255)):
            cv2.line(img, (x - s, y), (x + s, y), col, 5, cv2.LINE_AA); cv2.line(img, (x, y - s), (x, y + s), col, 5, cv2.LINE_AA)
for img, col in ((b, Y), (a, 255)):
    for x in range(60, 1150, 88):
        cv2.line(img, (x - 10, 500), (x + 10, 500), col, 3); cv2.line(img, (x, 490), (x, 500), col, 3)
    cv2.line(img, (10, 10), (10, 510), col, 3); cv2.line(img, (1190, 10), (1190, 510), col, 3)
save("plus_grid", b, a)

# dashed bar in a red frame
b, a = layer(2600, 48)
for img, col in ((b, R), (a, 200)):
    cv2.rectangle(img, (2, 4), (2597, 43), col, 2)
x = 14
while x < 2580:
    ln = rnd.choice([20, 34, 60, 90, 140, 200])
    if rnd.random() < 0.85:
        for img, col in ((b, Y), (a, 255)):
            cv2.rectangle(img, (x, 14), (min(2585, x + ln), 33), col, -1)
    x += ln + rnd.choice([8, 12, 24, 40])
save("dashed_bar", b, a)

# chevron bars: two long bars, stepped arrow ends, ruled
b, a = layer(1500, 220)
for (y0, y1) in ((20, 70), (150, 200)):
    pts = np.array([(40, y0), (1380, y0), (1440, (y0 + y1) // 2), (1380, y1), (40, y1)], np.int32)
    for img, col in ((b, Y), (a, 255)):
        cv2.fillPoly(img, [pts], col, cv2.LINE_AA)
    for xx in range(60, 1380, 26):                 # the ruling inside
        cv2.line(b, (xx, y0 + 4), (xx, y1 - 4), (10, 190, 180), 1)
for img, col in ((b, Y), (a, 255)):
    cv2.line(img, (900, 70), (1200, 150), col, 6, cv2.LINE_AA)
    for k in range(4):
        cv2.line(img, (1180 + k * 14, 80 + k * 18), (1440, 80 + k * 18), col, 4)
save("chevron_bars", b, a)

# grid panel
b, a = layer(1600, 760)
b[:] = NAVY; a[:] = 215
for xx in range(0, 1600, 24):
    cv2.line(b, (xx, 0), (xx, 760), (90, 60, 20), 1)
for yy in range(0, 760, 24):
    cv2.line(b, (0, yy), (1600, yy), (90, 60, 20), 1)
for img, col in ((b, C), (a, 255)):
    cv2.line(img, (0, 2), (520, 2), col, 3); cv2.line(img, (900, 757), (1600, 757), col, 3)
save("grid_panel", b, a)

# graph box
b, a = layer(440, 640)
for img, col in ((b, Y), (a, 255)):
    cv2.rectangle(img, (4, 4), (435, 635), col, 6)
for k, col in enumerate([Y, M, Y]):
    pts = [(20 + i * 8, 90 + k * 70 + int(18 * math.sin(i * 0.5 + k) + rnd.uniform(-10, 10))) for i in range(50)]
    for img, cc in ((b, col), (a, 255)):
        cv2.polylines(img, [np.array(pts, np.int32)], False, cc, 3, cv2.LINE_AA)
for k, col in enumerate([C, M, C]):
    for rr in (34, 22, 10):
        for img, cc in ((b, col if rr != 22 else Y), (a, 255)):
            cv2.circle(img, (90 + k * 130, 420), rr, cc, 3, cv2.LINE_AA)
save("graph_box", b, a)

# red stack
b, a = layer(140, 200)
for k in range(6):
    for img, col in ((b, R), (a, 255)):
        cv2.rectangle(img, (6, 6 + k * 32), (134, 26 + k * 32), col, -1)
save("red_stack", b, a)
