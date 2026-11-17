"""redflash: a generator for the flash in-between frames of Cyberpunk: Edgerunners 2 Teaser #2 (1:24, frames 23-29;
projects/opening/ref/cyberpunk_edits/QBlPg818lGI/at124_tear.jpg), matt 2026-11-15. Built like cyberpsycho.py (the
lines round the eyes): every shape is a stroke of the cyberpsycho Pen (plugins/cyberpsycho) along a path, and the
strokes grow out of a map (a matte: a face, a word, the eyes) the way the cyberpsycho lines shoot out of the eyes.

The path is a looping one: a base direction with loop-de-loops along it (a prolate trochoid: the pen runs forward
while circling, so it crosses itself in loops), its loops tightening, the stroke width swelling into fat slabs and
tapering to blades. Two flat tones only (red (235, 30, 75) on near-black), as measured off the teaser.

Frame kinds (flash() runs them in the teaser's order):
  bar      the path pulled straight: one thick stroke across, barely looping
  slab     the loops opening: a fat stroke looping along the path, crossing itself into torn slabs, blades at its ends,
           more strokes out of the map
  eye      the loops tight round a point of the map: the stroke fills in red and the loop lines inside it are drawn
           dark, like the teaser's eye
  rings    the path spiralling in on the map's centre: alternating red and dark rings
  fill     the frame flooded red, the path's last loops drawn dark through it, glitch rows

    frame(kind, seed, size=(1920, 1080), matte=None, path=None) -> BGR uint8
    flash(seed, size, matte, path) -> 7 frames
matte: a uint8 mask (255 = the subject) the strokes start inside and loop out of; path: [(x, y), (x, y)] the base
direction (default: across the frame through the matte's centre).
CLI: python redflash.py --sheet out.jpg [--matte mask.png]"""
import argparse
import math
import os
import random
import sys

import cv2
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "cyberpsycho"))
import cyberpsycho as CP  # noqa: E402

RED = np.array([75, 30, 235], np.float32)     # BGR
DARK = np.array([10, 3, 18], np.float32)


def loop_path(a, b, rnd, loops, radius, tight=0.0, n=420):
    """from a to b, looping: forward along a->b while circling radius r, `loops` times; tight > 0 pulls the loops in
    towards the middle (a spiral); a little wobble so it's hand-drawn"""
    a, b = np.asarray(a, np.float32), np.asarray(b, np.float32)
    d = b - a
    L = float(np.hypot(*d)) or 1.0
    u, nrm = d / L, np.array([-d[1], d[0]], np.float32) / L
    ph = rnd.uniform(0, 2 * math.pi)
    sq = rnd.uniform(0.45, 0.9)                    # loops squashed across the direction
    pts = []
    for i in range(n):
        t = i / (n - 1)
        r = radius * (1 - tight * (1 - abs(2 * t - 1))) * (1 + 0.18 * math.sin(7 * t + ph))
        ang = 2 * math.pi * loops * t + ph
        p = a + d * t + u * r * math.cos(ang) + nrm * r * sq * math.sin(ang)
        p += np.array([rnd.uniform(-1, 1), rnd.uniform(-1, 1)], np.float32) * radius * 0.015
        pts.append(p)
    return np.array(pts, np.float32)


def widths(n, rnd, fat, thin=3.0):
    """thin at the ends (blades), swelling into fat slabs in a few places"""
    w = np.full(n, thin, np.float32)
    for _ in range(rnd.randint(2, 4)):
        c, s = rnd.uniform(0.15, 0.85), rnd.uniform(0.08, 0.22)
        t = np.linspace(0, 1, n)
        w = np.maximum(w, fat * rnd.uniform(0.6, 1.0) * np.clip(1 - np.abs(t - c) / s, 0, 1) ** 0.7)
    return w


def stroke(pen, pts, w):
    """a variable-width stroke, drawn in short overlapping pieces so it can cross itself"""
    step = 24
    for i in range(0, len(pts) - 1, step):
        j = min(len(pts), i + step + 2)
        pen.poly(pts[i:j], list(w[i:j]))


def origins(matte, rnd, n, size):
    w, h = size
    if matte is None:
        return [np.array([rnd.uniform(0.2, 0.8) * w, rnd.uniform(0.3, 0.7) * h], np.float32) for _ in range(n)]
    ys, xs = np.where(matte > 128)
    return [np.array([xs[i], ys[i]], np.float32) for i in (rnd.randrange(len(xs)) for _ in range(n))]


def centre(matte, size):
    if matte is None:
        return np.array([size[0] / 2, size[1] / 2], np.float32)
    ys, xs = np.where(matte > 128)
    return np.array([xs.mean(), ys.mean()], np.float32)


def _paint(mask_red, mask_dark, size, seed):
    w, h = size
    img = np.empty((h, w, 3), np.float32); img[:] = DARK
    r = mask_red.astype(np.float32)[:, :, None] / 255
    img = img * (1 - r) + RED * r
    if mask_dark is not None:
        dk = mask_dark.astype(np.float32)[:, :, None] / 255
        img = img * (1 - dk) + DARK * dk
    stripe = 0.86 + 0.14 * (np.arange(w) % 3 != 0)
    img *= stripe[None, :, None]
    img += cv2.GaussianBlur(img, (0, 0), 14) * 0.35
    img += np.random.default_rng(abs(hash(seed)) % (2 ** 32)).normal(0, 4, (h, w, 1))
    return np.clip(img, 0, 255).astype(np.uint8)


def frame(kind, seed, size=(1920, 1080), matte=None, path=None):
    w, h = size
    rnd = random.Random("redflash %s %s" % (kind, seed))
    c = centre(matte, size)
    if path is None:
        tilt = rnd.uniform(-0.35, 0.35)
        path = [c - np.array([math.cos(tilt), math.sin(tilt)]) * w * 0.6, c + np.array([math.cos(tilt), math.sin(tilt)]) * w * 0.6]
    a, b = np.asarray(path[0], np.float32), np.asarray(path[-1], np.float32)
    red = CP.Pen(w, h, rnd); red.k = w / CP.REF_W
    dark = CP.Pen(w, h, rnd); dark.k = red.k
    if kind == "bar":
        pts = loop_path(a, b, rnd, 1.2, h * 0.02)
        stroke(red, pts, np.full(len(pts), h * 0.05 / red.k, np.float32))
    elif kind == "slab":
        pts = loop_path(a, b, rnd, rnd.uniform(2.0, 3.5), h * rnd.uniform(0.14, 0.24))
        stroke(red, pts, widths(len(pts), rnd, h * 0.24 / red.k))
        for o in origins(matte, rnd, rnd.randint(2, 4), size):           # out of the map, looping away
            ang = math.atan2(o[1] - c[1], o[0] - c[0]) + rnd.uniform(-0.7, 0.7)
            e = o + np.array([math.cos(ang), math.sin(ang)]) * rnd.uniform(0.3, 0.6) * w
            p2 = loop_path(o, e, rnd, rnd.uniform(1, 2.2), h * rnd.uniform(0.04, 0.1))
            stroke(red, p2, widths(len(p2), rnd, rnd.uniform(20, 60)))
        CP.drip(red, c + np.array([rnd.uniform(-0.2, 0.2) * w, h * 0.15], np.float32), 0)
        # the dark line work traced through it: the same path, offset, thin
        p3 = loop_path(a + (0, h * 0.03), b + (0, h * 0.03), rnd, rnd.uniform(1.5, 3), h * 0.1)
        stroke(dark, p3[int(len(p3) * 0.2):int(len(p3) * 0.75)], np.full(len(p3), 4.0))
    elif kind == "eye":
        pts = loop_path(a, b, rnd, rnd.uniform(1.5, 2.5), h * 0.3)
        stroke(red, pts, widths(len(pts), rnd, h * 0.4 / red.k))
        eye = c + np.array([rnd.uniform(-0.15, 0.15) * w, rnd.uniform(-0.12, 0.05) * h], np.float32)
        er = h * rnd.uniform(0.16, 0.24)
        cv2.ellipse(red.mask, (int(eye[0]), int(eye[1])), (int(er * 1.6), int(er)), rnd.uniform(-15, 15), 0, 360, 255, -1, cv2.LINE_AA)
        # the eye: a loop path spiralling in on it, drawn dark
        sp = loop_path(eye - (er * 1.3, 0), eye + (er * 0.1, 0), rnd, rnd.uniform(3, 4.5), er, tight=0.8)
        stroke(dark, sp, np.full(len(sp), rnd.choice([4, 5, 6]), np.float32))
        cv2.ellipse(dark.mask, (int(eye[0]), int(eye[1])), (int(er * 0.12), int(er * 0.14)), 0, 0, 360, 255, -1, cv2.LINE_AA)
        p3 = loop_path(eye + (er * 1.8, er * 0.3), eye + (er * 3.5, er * 0.1), rnd, 1.5, er * 0.3)
        stroke(dark, p3, np.full(len(p3), 4.0))
    elif kind == "rings":
        R = h * rnd.uniform(0.5, 0.8)
        sp = loop_path(c - (R, 0), c + (R * 0.05, 0), rnd, rnd.uniform(4, 6), R, tight=0.95, n=700)
        stroke(red, sp, np.full(len(sp), R * 0.11 / red.k, np.float32) * np.linspace(1, 0.5, len(sp)))
        cv2.ellipse(red.mask, (int(c[0]), int(c[1])), (int(R * 0.05), int(R * 0.07)), 0, 0, 360, 255, -1, cv2.LINE_AA)
    elif kind == "fill":
        red.mask[:] = 255
        pts = loop_path(a, b, rnd, rnd.uniform(2, 3.5), h * 0.2)
        stroke(dark, pts[int(len(pts) * 0.3):int(len(pts) * 0.6)], np.full(len(pts), 3.0))
        for _ in range(rnd.randint(18, 40)):
            y, bh = rnd.randrange(h), rnd.randint(2, 14)
            x0, x1 = sorted([rnd.randrange(w), rnd.randrange(w)])
            dark.mask[y:y + bh, x0:x1] = rnd.choice([0, 90, 160])
    return _paint(red.mask, dark.mask, size, "%s %s" % (kind, seed))


SEQ = ["bar", "slab", "slab", "eye", "eye", "rings", "fill"]


def flash(seed, size=(1920, 1080), matte=None, path=None):
    return [frame(k, "%s %d" % (seed, i), size, matte, path) for i, k in enumerate(SEQ)]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet")
    ap.add_argument("--matte")
    ap.add_argument("--seed", default="1")
    ap.add_argument("--out")
    a = ap.parse_args()
    m = None
    if a.matte:
        m = cv2.resize(cv2.imread(a.matte, cv2.IMREAD_GRAYSCALE), (1920, 1080))
    if a.sheet:
        rows = [np.hstack([cv2.resize(f, (320, 180)) for f in flash(sd, matte=m)]) for sd in ("a", "b", "c")]
        cv2.imwrite(a.sheet, np.vstack(rows))
    if a.out:
        os.makedirs(a.out, exist_ok=True)
        for i, f in enumerate(flash(a.seed, matte=m)):
            cv2.imwrite(os.path.join(a.out, "flash_%02d.png" % (i + 1)), f)
