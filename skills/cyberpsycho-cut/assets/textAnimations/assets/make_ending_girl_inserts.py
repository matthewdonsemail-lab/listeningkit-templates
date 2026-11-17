"""The ending's flash cuts, made from the girl (matt, 2026-11-16): lots of different shots of her (projects/cyberpunk:
her close-ups, the anime / line-art versions, the style variants, the overhead hall shots cropped in on her), each
flash a few frames of one shot, pushing in, with the Edgerunners 2 red slashes (plugins/redlines) looping round her,
a new drawing every frame. And red cracks through the giant full-screen words.
Writes assets/collage/girlins/ins_NN/f_NN.jpg (the flash cuts, in the order endingCrazy.jsx places them) and
assets/collage/girlins/giant_NN/c_NN.png (RGBA cracks, 7 frames each).
  python textAnimations/assets/make_ending_girl_inserts.py"""
import os
import random
import shutil
import sys

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "plugins", "redlines"))
import redlines as RL  # noqa: E402

CP = os.path.normpath(os.path.join(HERE, "..", "..", "projects", "cyberpunk"))
OUT = os.path.join(HERE, "collage", "girlins")
W, H = 1920, 1080
N_INS, INS_LEN, N_GIANT, GIANT_LEN = 30, 4, 8, 7
# (file, crop centre x, y as a share of the image, zoom): close-ups whole, the overhead shots cropped in on her
SHOTS = [("eyes2.png", .5, .45, 1.0), ("eyes3.png", .5, .5, 1.0), ("eyes2_v1.png", .5, .5, 1.0),
         ("eyes3_v2_frontOn.png", .5, .5, 1.0), ("variants/eyes2/oil.png", .5, .45, 1.0), ("eyes3_v1.png", .5, .5, 1.0),
         ("eyes2_v2_upsideDown.png", .5, .5, 1.0), ("variants/eyes2/ukiyoe.png", .5, .45, 1.0),
         ("shot3.png", .55, .45, 2.2), ("eyes1_v1.png", .5, .5, 1.0), ("variants/eyes2/ps2.png", .5, .45, 1.0),
         ("styles/open_f_anime.png", .55, .5, 2.4), ("variants/eyes2/clay.png", .5, .45, 1.0),
         ("styles/open_c_anime.png", .5, .45, 2.2), ("variants/eyes2/magritte.png", .5, .45, 1.0),
         ("girl.png", .52, .42, 2.6)]


# her eyes in each framed shot (share of the frame, left then right), read off a grid of the framed shots
EYES = [((.44, .34), (.57, .35)), ((.44, .46), (.57, .45)), ((.26, .50), (.69, .50)), ((.32, .54), (.58, .54)),
        ((.46, .35), (.59, .34)), ((.27, .54), (.71, .54)), ((.52, .62), (.60, .66)), ((.39, .41), (.52, .43)),
        ((.40, .37), (.45, .37)), ((.17, .46), (.73, .46)), ((.42, .37), (.55, .37)), ((.38, .30), (.42, .30)),
        ((.45, .35), (.57, .35)), ((.45, .35), (.49, .35)), ((.47, .35), (.59, .35)), ((.40, .42), (.44, .42))]


def paste(img, patch, x, y):
    x0, y0 = max(x, 0), max(y, 0)
    x1, y1 = min(x + patch.shape[1], W), min(y + patch.shape[0], H)
    if x1 > x0 and y1 > y0:
        img[y0:y1, x0:x1] = patch[y0 - y:y1 - y, x0 - x:x1 - x]


def eye_glitch(img, eyes, others, rnd, j):
    """the opener's cyberpsycho on her, different every time: her eyes echoing outwards (count, size, reach and
    direction drawn new), rectangles of her face cut in from her other shots, a quadrant cut to another shot,
    band slips; which of these happen, and how hard, is drawn per insert"""
    (lx, ly), (rx, ry) = [(x * W, y * H) for x, y in eyes]
    d = max(60.0, float(np.hypot(rx - lx, ry - ly)))
    out = img.copy()
    if rnd.random() < 0.5:                                     # a quadrant to another shot of her
        qx, qy = rnd.randint(0, 1), rnd.randint(0, 1)
        o = rnd.choice(others)
        out[qy * H // 2:(qy + 1) * H // 2, qx * W // 2:(qx + 1) * W // 2] = o[qy * H // 2:(qy + 1) * H // 2, qx * W // 2:(qx + 1) * W // 2]
    for _ in range(rnd.randint(1, 5)):                         # face cut-ins from her other shots, round her eyes
        cx = rnd.uniform(lx - d * .3, rx + d * .3); cy = rnd.uniform(ly - d * .5, ly + d * 1.2)
        w_, h_ = int(d * rnd.uniform(.3, 1.4)), int(d * rnd.uniform(.15, .6))
        x, y = int(min(max(cx - w_ / 2, 0), W - w_)), int(min(max(cy - h_ / 2, 0), H - h_))
        paste(out, rnd.choice(others + [img])[y:y + h_, x:x + w_], x + rnd.randint(-int(d * .2), int(d * .2)), y)
    vert = rnd.random() < 0.25                                 # echoes stepping out sideways, or up and down
    for (ex, ey), side in (((lx, ly), -1), ((rx, ry), 1)):
        ew, eh = d * rnd.uniform(.35, .6), d * rnd.uniform(.22, .4)
        crop = img[int(max(ey - eh / 2, 0)):int(ey + eh / 2), int(max(ex - ew / 2, 0)):int(ex + ew / 2)]
        if crop.size == 0:
            continue
        reach = 0.0
        for _ in range(rnd.randint(2, 6)):
            k = rnd.uniform(.6, 1.9)
            patch = cv2.resize(crop, (max(4, int(crop.shape[1] * k)), max(4, int(crop.shape[0] * k))))
            reach += d * rnd.uniform(.25, .55)
            px = ex + (0 if vert else side * reach); py = ey + (side * reach * .6 if vert else rnd.uniform(-.1, .1) * d)
            paste(out, patch, int(px - patch.shape[1] / 2), int(py - patch.shape[0] / 2))
    for _ in range(rnd.randint(0, 4)):                         # band slips
        y0, bh = rnd.randrange(H), rnd.randint(6, 70)
        out[y0:y0 + bh] = np.roll(out[y0:y0 + bh], rnd.randint(-160, 160), axis=1)
    return out


def frame_of(path, cx, cy, z):
    im = cv2.imread(os.path.join(CP, path))
    h, w = im.shape[:2]
    k = max(W / w, H / h) * z
    im = cv2.resize(im, (int(w * k), int(h * k)), interpolation=cv2.INTER_AREA if k < 1 else cv2.INTER_CUBIC)
    h, w = im.shape[:2]
    x0 = int(min(max(cx * w - W / 2, 0), w - W)); y0 = int(min(max(cy * h - H / 2, 0), h - H))
    return im[y0:y0 + H, x0:x0 + W]


def matte_of(img):
    """her, roughly: GrabCut seeded with the middle of the frame"""
    small = cv2.resize(img, (480, 270))
    m = np.zeros(small.shape[:2], np.uint8)
    bg, fg = np.zeros((1, 65), np.float64), np.zeros((1, 65), np.float64)
    cv2.grabCut(small, m, (90, 20, 300, 245), bg, fg, 4, cv2.GC_INIT_WITH_RECT)
    m = np.where((m == 1) | (m == 3), 255, 0).astype(np.uint8)
    return cv2.resize(m, (W, H), interpolation=cv2.INTER_NEAREST)


def push(img, s):
    M = cv2.getRotationMatrix2D((W / 2, H / 2), 0, s)
    return cv2.warpAffine(img, M, (W, H), borderMode=cv2.BORDER_REFLECT)


if os.path.isdir(OUT):
    shutil.rmtree(OUT)
cache = {}
framed = [frame_of(*sh) for sh in SHOTS]
for i in range(N_INS):
    sh = SHOTS[i % len(SHOTS)]
    if sh not in cache:
        img = frame_of(*sh)
        cache[sh] = (img, matte_of(img))
    img, m = cache[sh]
    d = os.path.join(OUT, "ins_%02d" % (i + 1)); os.makedirs(d)
    for j in range(INS_LEN):
        s = 1.0 + 0.025 * j
        rnd = random.Random("eyes %d %d" % (i, j))
        g = eye_glitch(img, EYES[i % len(EYES)], [framed[q] for q in range(len(framed)) if q != i % len(SHOTS)], rnd, j)
        base = push(g, s).astype(np.float32)
        sl = RL.slashes("girl %d %d" % (i, j), matte=push(m, s), n=random.Random(i * 7 + j).randint(2, 4))
        a = sl[:, :, 3:4].astype(np.float32) / 255
        out = base * (1 - a) + sl[:, :, :3][:, :, ::-1].astype(np.float32) * a
        cv2.imwrite(os.path.join(d, "f_%02d.jpg" % (j + 1)), out.astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 92])
    print("insert", i + 1, sh[0])
for g in range(N_GIANT):
    d = os.path.join(OUT, "giant_%02d" % (g + 1)); os.makedirs(d)
    x = random.Random("giant %d" % g).uniform(0.35, 0.65) * W
    for j in range(GIANT_LEN):
        im = RL.cracks("giant %d %d" % (g, j), [(x + 60, -20), (x, H / 2), (x - 50, H + 20)])
        cv2.imwrite(os.path.join(d, "c_%02d.png" % (j + 1)), cv2.cvtColor(im, cv2.COLOR_RGBA2BGRA))
    print("giant cracks", g + 1)
