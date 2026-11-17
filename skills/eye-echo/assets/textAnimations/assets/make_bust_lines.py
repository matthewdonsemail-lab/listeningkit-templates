"""The cyberpunk outro's busts scene (matt, 2026-11-15): the six caricature busts (projects/cyberpunk/outro/portrait_0-5),
each on for its 30 frames ("outro portraits", make_cyberpunk_outro_comp.py), now with a cyberpsycho line:

- The line comes from in front: it enters from the bottom of the frame thick, as if right at the camera, and thins
  as it runs; it wipes along a path round the bust (his silhouette, measured from the image, squared off into hard
  right-angle corners and bends), the wipe accelerating exponentially, with a bright head and a blue glow.
- At the apex (the line closing round him) the opener's cyberpsycho starts on him (as make_opening_psycho_cut.py):
  the frame's quadrants cut to his other versions (realistic, low-poly, 1-bit dither: images/gen/make_bust_styles.py,
  same framing), rectangles of them over his face parts large into small, his eyes echoing outwards in different
  sizes, band slips, the cyberpsycho lines out of his eyes; and the whole frame flicks between his full versions.
- The slow pan each bust had (alternating right and left) is kept.

Writes textAnimations/assets/collage/bust_lines.mp4 (1920x1080, 30 fps, 180 frames), placed over "outro portraits" by
plugins/bustLines.jsx.  --frames 5,20 writes just those frames as PNGs (--png-dir)."""
import argparse
import math
import os
import random
import subprocess

import sys

import cv2
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "plugins", "cyberpsycho"))
import cyberpsycho  # noqa: E402

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUTRO = os.path.join(ROOT, "projects", "cyberpunk", "outro")
OUT = os.path.join(ROOT, "textAnimations", "assets", "collage", "bust_lines.mp4")
W, H, FPS, PF = 1920, 1080, 30, 30          # PF: frames per bust, as the outro (make_cyberpunk_outro.PORTRAIT)
APEX = 17                                   # the frame (of each bust's 30) the line closes on: the glitch starts
STYLES = ["realistic", "polygon", "dither"]
# each bust's eyes in the output frame (left, right; px, unpanned), read off a grid; his face parts come from them
EYES = [((590, 250), (680, 175)), ((940, 300), (1240, 370)), ((660, 390), (1030, 350)), ((990, 410), (1300, 500)),
        ((570, 270), (910, 240)), ((700, 540), (1160, 480))]
# each bust's face in the output frame (x, y, w, h), read off the stills
FACES = [(660, 340, 300, 380), (1020, 420, 380, 400), (880, 400, 320, 400), (1100, 520, 300, 320),
         (880, 640, 380, 360), (880, 520, 400, 400)]

ap = argparse.ArgumentParser()
ap.add_argument("--frames"); ap.add_argument("--png-dir", default=os.path.join(ROOT, "renders", "bust_lines_frames"))
ap.add_argument("--out", default=OUT)
a = ap.parse_args()
want = None if not a.frames else {int(v) for v in a.frames.split(",")}


def cover(path):
    """the still scaled to cover the frame at 108% (as the outro's cover_spec(.., 1.08)), centred"""
    im = cv2.imread(path)
    k = max(W / im.shape[1], H / im.shape[0]) * 1.08
    im = cv2.resize(im, (int(im.shape[1] * k), int(im.shape[0] * k)), interpolation=cv2.INTER_AREA)
    return im


def crop_at(im, dx):
    """the frame of a covered still, panned dx px"""
    y0 = (im.shape[0] - H) // 2
    x0 = int((im.shape[1] - W) // 2 - dx)
    x0 = max(0, min(im.shape[1] - W, x0))
    return im[y0:y0 + H, x0:x0 + W].copy()


def ortho_path(img, side):
    """the line's path: in from the front (a bottom corner of the frame), up the frame's side, then over him along his
    skyline (the top of his head and shoulders), just above it, in hard right-angle steps, to the other side.
    It never crosses him: the busts fill the frame, so 'around him' is over him."""
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    m = (cv2.GaussianBlur(g, (0, 0), 6) > 12).astype(np.uint8)  # low: his dark hair counts
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (41, 41)))
    top = np.array([np.argmax(m[:, x] > 0) if m[:, x].any() else H for x in range(W)], np.float64)
    top = np.minimum.accumulate(top[::-1])[::-1] * 0 + top  # (as measured)
    top = cv2.erode(top.astype(np.float32)[None, :], np.ones((1, 201), np.uint8))[0]  # widen peaks: clear the hair
    sky = np.clip(top - 75, 24, H - 24)
    xs = list(range(0, W + 1, 80))
    if side < 0:
        xs = xs[::-1]
    pts = [np.array([float(np.clip(xs[0], 16, W - 16)), H + 80.0])]  # in from the front: below the frame
    for x in xs:
        xc = float(np.clip(x, 16, W - 16))
        y = float(np.round(sky[int(np.clip(x, 0, W - 1)) if x < W else W - 1] / 40) * 40)
        y = max(24.0, min(H - 24.0, y))
        q = pts[-1]
        if len(pts) == 1:
            pts.append(np.array([xc, y]))
            continue
        if abs(y - q[1]) > 1:   # a hard step: across, then up or down
            pts.append(np.array([xc, q[1]])); pts.append(np.array([xc, y]))
        else:
            pts.append(np.array([xc, y]))
    pts.append(np.array([pts[-1][0], H + 80.0]))  # and down the far side, out of the frame
    return np.array(pts, np.float64)


def draw_line(frame, pts, p, flick):
    """the path drawn to fraction p of its length: thick where it enters (the front), thin after; head bright"""
    seg = np.hypot(*np.diff(pts, axis=0).T)
    cum = np.concatenate([[0], np.cumsum(seg)])
    L = cum[-1] * p
    glow = np.zeros_like(frame, np.float32)
    core = np.zeros(frame.shape[:2], np.uint8)
    head = None
    for i in range(len(seg)):
        if cum[i] >= L:
            break
        a_, b_ = pts[i], pts[i + 1]
        t = min(1.0, (L - cum[i]) / max(seg[i], 1e-6))
        e = a_ + (b_ - a_) * t
        along = cum[i] / cum[-1]
        th = int(round(34 * math.exp(-5 * along) + 5))  # from in front: thick at the start, thin round him
        cv2.line(core, tuple(int(v) for v in a_), tuple(int(v) for v in e), 255, th, cv2.LINE_AA)
        head = e
    blur = cv2.GaussianBlur(core, (0, 0), 14).astype(np.float32) / 255
    glow[:, :, 0] += blur * 255; glow[:, :, 1] += blur * 120; glow[:, :, 2] += blur * 40   # blue glow (BGR)
    out = frame.astype(np.float32) + glow * (1.4 if flick else 1.0)
    cm = core.astype(np.float32)[:, :, None] / 255
    out = out * (1 - cm) + np.array([255, 245, 235], np.float32) * cm
    if head is not None:
        cv2.circle(out, tuple(int(v) for v in head), 14, (255, 255, 255), -1, cv2.LINE_AA)
    return np.clip(out, 0, 255).astype(np.uint8)


def split(img, k):
    o = img.copy()
    o[:, :, 2] = np.roll(img[:, :, 2], k, axis=1)
    o[:, :, 0] = np.roll(img[:, :, 0], -k, axis=1)
    return o


def face_parts(eyes):
    """his face parts from his eyes, as the opener's cut does it (make_opening_psycho_cut.py out_parts)"""
    (lx, ly), (rx, ry) = eyes
    x, y, d = (lx + rx) / 2, (ly + ry) / 2, max(120.0, float(np.hypot(rx - lx, ry - ly)))
    return {"face": (x, y + 0.35 * d, 1.9 * d, 2.3 * d), "left half": (x - 0.45 * d, y + 0.35 * d, 0.95 * d, 2.2 * d),
            "right half": (x + 0.45 * d, y + 0.35 * d, 0.95 * d, 2.2 * d), "eye band": (x, y, 1.75 * d, 0.42 * d),
            "eye left": (lx, ly, 0.5 * d, 0.3 * d), "eye right": (rx, ry, 0.5 * d, 0.3 * d),
            "brows": (x, y - 0.27 * d, 1.6 * d, 0.26 * d), "forehead": (x, y - 0.6 * d, 1.3 * d, 0.4 * d),
            "nose": (x, y + 0.42 * d, 0.48 * d, 0.55 * d), "mouth": (x, y + 0.9 * d, 0.95 * d, 0.45 * d),
            "cheek left": (x - 0.6 * d, y + 0.55 * d, 0.5 * d, 0.6 * d),
            "cheek right": (x + 0.6 * d, y + 0.55 * d, 0.5 * d, 0.6 * d), "jaw": (x, y + 1.25 * d, 1.4 * d, 0.4 * d)}, d


BIG = ["face", "left half", "right half", "eye band", "mouth", "forehead"]
SMALL = ["eye left", "eye right", "brows", "nose", "mouth", "cheek left", "cheek right", "jaw", "eye band"]


def paste(img, patch, x, y):
    x0, y0 = max(x, 0), max(y, 0)
    x1, y1 = min(x + patch.shape[1], W), min(y + patch.shape[0], H)
    if x1 > x0 and y1 > y0:
        img[y0:y1, x0:x1] = patch[y0 - y:y1 - y, x0 - x:x1 - x]


def glitch(frame, versions, eyes, rnd, heat, j, apex_frames):
    """at the apex, the opener's cyberpsycho on his face: the frame's quadrants cut to his other versions, rectangles
    of them over his face parts (large into small), his eyes echoing outwards in different sizes, band slips, and the
    cyberpsycho lines shooting out of his eyes"""
    pp, d = face_parts(eyes)
    out = frame.copy()
    # the quadrants: one or two quarters of the frame cut to another version, every couple of frames
    qr = random.Random("quad %d %d" % (id(versions) % 997, j // 2))
    for _ in range(qr.randint(1, 2)):
        qx, qy = qr.randint(0, 1), qr.randint(0, 1)
        src = qr.choice(versions[1:] or versions)
        out[qy * H // 2:(qy + 1) * H // 2, qx * W // 2:(qx + 1) * W // 2] = src[qy * H // 2:(qy + 1) * H // 2, qx * W // 2:(qx + 1) * W // 2]
    # his face cut up: rectangles from his other versions over his face parts, large into small
    within = min(1.0, j / max(1, apex_frames - 1))
    for _ in range(4 + int(10 * heat)):
        name = rnd.choice(BIG if rnd.random() > within * 0.8 + heat * 0.3 else SMALL)
        cx, cy, pw, ph = pp[name]
        f = rnd.uniform(0.75, 1.25) * (1.0 - 0.5 * within)
        w_, h_ = max(12, min(W, int(pw * f))), max(10, min(H, int(ph * f)))
        cx += rnd.uniform(-0.5, 0.5) * max(pw - w_, pw * 0.2); cy += rnd.uniform(-0.5, 0.5) * max(ph - h_, ph * 0.2)
        x, y = int(min(max(cx - w_ / 2, 0), W - w_)), int(min(max(cy - h_ / 2, 0), H - h_))
        patch = rnd.choice(versions)[y:y + h_, x:x + w_]
        if rnd.random() < 0.35 + 0.5 * heat:
            patch = split(patch, rnd.randint(4, 8 + int(20 * heat)))
        paste(out, patch, x + int(rnd.choice([0, 0, 1]) * rnd.uniform(-1, 1) * d * (0.05 + 0.3 * heat)), y)
    # his eyes echoing outwards: copies from his versions, different sizes, stepping out left and right
    for eye, side in (("eye left", -1), ("eye right", 1)):
        cx, cy, ew, eh = pp[eye]
        ew, eh, reach = ew * 1.25, eh * 1.35, 0.0
        for _ in range(rnd.randint(2, 4)):
            src = rnd.choice(versions)
            crop = src[int(max(cy - eh / 2, 0)):int(max(cy + eh / 2, 1)), int(max(cx - ew / 2, 0)):int(max(cx + ew / 2, 1))]
            if crop.size == 0:
                continue
            kk = rnd.uniform(0.7, 1.7)
            patch = cv2.resize(crop, (max(4, int(crop.shape[1] * kk)), max(4, int(crop.shape[0] * kk))))
            reach += rnd.uniform(0.22, 0.42) * d * (0.6 + 0.4 * kk)
            paste(out, patch, int(cx + side * reach - patch.shape[1] / 2), int(cy - patch.shape[0] / 2))
    for _ in range(rnd.randint(1, 3 + int(3 * heat))):  # band slips
        y0, bh = rnd.randrange(H), rnd.randint(6, 60)
        out[y0:y0 + bh] = np.roll(out[y0:y0 + bh], int(rnd.uniform(-140, 140) * (0.3 + heat)), axis=1)
    # the cyberpsycho lines, out of his eyes, on twos
    m = np.zeros((H, W), np.uint8)
    for eye in ("eye left", "eye right"):
        cx, cy, ew, eh = pp[eye]
        cv2.ellipse(m, (int(cx), int(cy)), (max(1, int(ew / 2)), max(1, int(eh / 2))), 0, 0, 360, 255, -1)
    lines = cyberpsycho.frame("bust %d %d" % (int(eyes[0][0]), j // 2), (W, H), m, (245, 245, 245), 0.7 + 0.8 * heat,
                              outline=(20, 0, 0), outline_px=2)
    if heat > 0.4:
        lines = cyberpsycho.glitch(lines, j // 2, heat)
    al = lines[:, :, 3:4].astype(np.float32) / 255
    rgb = lines[:, :, :3][:, :, ::-1].astype(np.float32)  # RGB -> BGR
    return (out * (1 - al) + rgb * al).astype(np.uint8)


busts = []
for i in range(6):
    base = cover(os.path.join(OUTRO, "portrait_%d.png" % i))
    vers = [base]
    for s in STYLES:
        p = os.path.join(OUTRO, "styles", "portrait_%d_%s.png" % (i, s))
        vers.append(cover(p) if os.path.exists(p) else base)
    busts.append(vers)

if want is None:
    proc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", "%dx%d" % (W, H),
                             "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "14", "-pix_fmt", "yuv420p", a.out], stdin=subprocess.PIPE)
else:
    os.makedirs(a.png_dir, exist_ok=True)
rnd = random.Random("bust lines")
for i, vers in enumerate(busts):
    side = 1 if i % 2 == 0 else -1
    path = ortho_path(crop_at(vers[0], 0), 1 if i % 2 == 0 else -1)
    for j in range(PF):
        f = i * PF + j
        if want is not None and f not in want:
            continue
        dx = side * (-45 + 90 * j / (PF - 1))  # the pan the bust always had
        frames = [crop_at(v, dx) for v in vers]
        if j < APEX:
            u = j / (APEX - 1)
            p = (math.exp(4.5 * u) - 1) / (math.exp(4.5) - 1)  # exponential: slow from the front, whipping round him
            out = draw_line(frames[0], path + np.array([dx, 0]), p, False)
        else:
            heat = (j - APEX) / max(1, PF - 1 - APEX)
            base = frames[(j // 2 + rnd.randint(0, 1)) % len(frames)]  # flicking between his full versions
            eyes = tuple((ex + dx, ey) for ex, ey in EYES[i])
            out = glitch(base, frames, eyes, rnd, heat, j - APEX, PF - APEX)
            out = draw_line(out, path + np.array([dx, 0]), 1.0, j % 2 == 0)
        if want is None:
            proc.stdin.write(np.ascontiguousarray(out).tobytes())
        else:
            cv2.imwrite(os.path.join(a.png_dir, "frame_%03d.png" % f), out)
if want is None:
    proc.stdin.close(); proc.wait()
print("busts: %d frames -> %s" % (6 * PF, a.out if want is None else a.png_dir))
