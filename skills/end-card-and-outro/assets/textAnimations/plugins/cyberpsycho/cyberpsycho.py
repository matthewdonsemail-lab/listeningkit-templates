"""cyberpsycho: procedural jagged "cyberpsychosis" lines, drawn with numpy + OpenCV.

Measured from the five reference frames in references/cyberpsycho (the red lines isolated by colour, ref<n>_iso.png):
at 1242 px wide the strokes are mostly thin (median ~7 px), swelling into long wedge blades up to 35-75 px that taper
to a point; the paths are hand-drawn jitters with sharp corners, stepped right angles, vertical drips and short ticks;
9-38 separate pieces cover 2.5-5% of the frame, and the drawing is new on every second frame (animated on twos).
Everything here is scaled from those numbers to the output width.

Use it as a library (the cyberpunk flow does) or from the command line:
    python cyberpsycho.py --matte girl.png --frames 60 --out lines.mov [--color 30,140,255] [--density 1]
which writes a transparent ProRes 4444 layer to put behind the subject. The lines start inside the subject's matte
(so they come out from behind it) and shoot outward.

    frame(seed, size, matte, color, density) -> RGBA uint8 array
"""
import argparse
import math
import random
import subprocess

import cv2
import numpy as np

REF_W = 1242.0


class Pen:
    def __init__(self, w, h, rnd):
        self.w, self.h, self.k, self.rnd = w, h, w / REF_W, rnd
        self.mask = np.zeros((h, w), np.uint8)

    def poly(self, pts, widths):
        """a variable-width stroke: the outline of the path offset by half its width on each side, jittered"""
        pts = np.asarray(pts, np.float32)
        if len(pts) < 2:
            return
        left, right = [], []
        for i in range(len(pts)):
            a, b = pts[max(i - 1, 0)], pts[min(i + 1, len(pts) - 1)]
            d = b - a
            n = np.array([-d[1], d[0]], np.float32) / (np.hypot(*d) + 1e-6)
            hw = max(0.5, widths[i] / 2) * self.k
            j = self.rnd.uniform(-0.6, 0.6) * self.k
            left.append(pts[i] + n * (hw + j))
            right.append(pts[i] - n * (hw - j))
        cv2.fillPoly(self.mask, [np.round(np.vstack([left, right[::-1]])).astype(np.int32)], 255, cv2.LINE_AA)

    def walk(self, start, heading, length, step, turn, snap=None):
        """a path of straight runs with sharp corners: each run 'step' long, turning up to 'turn' radians"""
        pts, p, a, d = [np.array(start, np.float32)], np.array(start, np.float32), heading, 0.0
        while d < length:
            run = self.rnd.uniform(0.4, 1.0) * step * self.k
            if snap and self.rnd.random() < 0.45:  # stepped right angles, like a circuit trace
                a = round(a / snap) * snap + self.rnd.choice([-snap, 0, snap])
            else:
                a += self.rnd.uniform(-turn, turn)
            p = p + run * np.array([math.cos(a), math.sin(a)], np.float32)
            pts.append(p.copy())
            d += run
        return pts


def blade(pen, origin, heading):
    """a long straight slash that swells into a wedge and tapers to a point, with a barb or two"""
    k, rnd = pen.k, pen.rnd
    length = rnd.uniform(140, 420) * k
    n = 14
    pts = [origin + (i / n) * length * np.array([math.cos(heading), math.sin(heading)]) for i in range(n + 1)]
    pts = [p + np.array([rnd.uniform(-1.5, 1.5), rnd.uniform(-1.5, 1.5)]) * k for p in pts]
    peak, top = rnd.uniform(0.2, 0.7), rnd.choice([10, 18, 30, 45, 70])
    widths = [max(1.5, top * (t / peak if t < peak else (1 - t) / (1 - peak)) ** rnd.choice([0.8, 1.4])) for t in
              (i / n for i in range(n + 1))]
    pen.poly(pts, widths)
    for _ in range(rnd.randint(0, 2)):  # barbs: short spikes off the side
        i = rnd.randint(2, n - 2)
        a = heading + rnd.choice([-1, 1]) * rnd.uniform(0.4, 1.1)
        tip = pts[i] + rnd.uniform(20, 60) * k * np.array([math.cos(a), math.sin(a)])
        pen.poly([pts[i], tip], [widths[i] * 0.6, 1])


def jag(pen, origin, heading):
    """a thin jittery line with sharp corners and stepped right angles, thickening here and there"""
    rnd = pen.rnd
    pts = pen.walk(origin, heading, rnd.uniform(120, 480), rnd.uniform(18, 70), rnd.uniform(0.5, 1.6), snap=math.pi / 2)
    widths = [rnd.choice([2, 3, 4, 5, 7]) for _ in pts]
    for _ in range(rnd.randint(0, 2)):  # a short thick slab somewhere along it
        i = rnd.randrange(len(widths))
        for j in range(i, min(i + 2, len(widths))):
            widths[j] = rnd.uniform(12, 26)
    pen.poly(pts, widths)


def drip(pen, origin, _heading):
    """a vertical run with a kink and little ticks off it"""
    rnd, k = pen.rnd, pen.k
    x, y = origin
    pts, length = [], rnd.uniform(80, 300) * k
    for i in range(8):
        pts.append(np.array([x + rnd.uniform(-3, 3) * k + (12 * k if i == 4 else 0), y + length * i / 7]))
    pen.poly(pts, [rnd.choice([2, 3, 4]) for _ in pts])
    for _ in range(rnd.randint(1, 3)):
        p = pts[rnd.randrange(len(pts))]
        a = rnd.choice([0, math.pi]) + rnd.uniform(-0.4, 0.4)
        pen.poly([p, p + rnd.uniform(10, 35) * k * np.array([math.cos(a), math.sin(a)])], [2, 1])


def trace(pen, matte, inflate):
    """part of the subject's own outline, pushed out a little and drawn shaky, like the outline round a figure"""
    rnd = pen.rnd
    m = cv2.dilate((matte > 128).astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (inflate, inflate)))
    cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if not cs:
        return
    c = max(cs, key=len)[:, 0, :].astype(np.float32)
    seg = int(len(c) * rnd.uniform(0.15, 0.45))
    s = rnd.randrange(len(c))
    run = np.roll(c, -s, axis=0)[:seg:max(1, int(14 * pen.k))]
    run = run + np.array([[rnd.uniform(-4, 4) * pen.k, rnd.uniform(-4, 4) * pen.k] for _ in run])
    pen.poly(run, [rnd.choice([2, 3, 4, 6]) for _ in run])


def frame(seed, size, matte=None, color=(30, 140, 255), density=1.0, outline=None, outline_px=0, thin=False,
          width_scale=1.0, avoid=None):
    """one drawing of the lines as RGBA; color is RGB. With a matte, the lines start inside it and shoot outward.
    outline (RGB) and outline_px draw a dark edge round every stroke, so the lines read on any background.
    thin: only fine jags, drips and small blades (for layering in depth); width_scale scales every stroke.
    avoid=(cx, cy, rx, ry): an oval the lines fade out of (a face to keep clear); with no matte, they start outside it."""
    w, h = size
    rnd = random.Random(seed)
    pen = Pen(w, h, rnd)
    pen.k *= width_scale if thin else 1.0
    if thin:
        return _thin(pen, rnd, w, h, color, density, outline, outline_px, avoid, width_scale)
    if matte is not None:
        ys, xs = np.where(matte > 128)
        cx, cy = xs.mean(), ys.mean()
    else:
        xs = ys = None
        cx, cy = w / 2, h / 2
    pieces = int(round(rnd.uniform(9, 22) * density))
    for _ in range(pieces):
        if xs is not None and len(xs):
            i = rnd.randrange(len(xs))
            origin = np.array([xs[i], ys[i]], np.float32)
        else:
            origin = np.array([rnd.uniform(0, w), rnd.uniform(0, h)], np.float32)
        out = math.atan2(origin[1] - cy, origin[0] - cx) + rnd.uniform(-0.9, 0.9)  # away from the subject
        kind = rnd.random()
        if kind < 0.30:
            blade(pen, origin, out)
        elif kind < 0.75:
            jag(pen, origin, out)
        elif kind < 0.88:
            drip(pen, origin + np.array([rnd.uniform(-250, 250), rnd.uniform(-200, 0)]) * pen.k, out)
        elif matte is not None:
            trace(pen, matte, int(rnd.uniform(20, 60) * pen.k) | 1)
    rgba = np.zeros((h, w, 4), np.uint8)
    rgba[:, :, 0], rgba[:, :, 1], rgba[:, :, 2] = color
    rgba[:, :, 3] = pen.mask
    if outline is not None and outline_px > 0:
        ring = cv2.dilate(pen.mask, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * outline_px + 1, 2 * outline_px + 1)))
        core = pen.mask.astype(np.float32)[:, :, None] / 255.0
        col = np.array(color, np.float32) * core + np.array(outline, np.float32) * (1 - core)
        rgba[:, :, :3] = col.astype(np.uint8)
        rgba[:, :, 3] = ring
    return rgba


def _finish(pen, color, outline, outline_px, keep=None):
    h, w = pen.mask.shape
    mask = pen.mask if keep is None else (pen.mask.astype(np.float32) * keep).astype(np.uint8)
    rgba = np.zeros((h, w, 4), np.uint8)
    rgba[:, :, 0], rgba[:, :, 1], rgba[:, :, 2] = color
    rgba[:, :, 3] = mask
    if outline is not None and outline_px > 0:
        ring = cv2.dilate(mask, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * outline_px + 1, 2 * outline_px + 1)))
        core = mask.astype(np.float32)[:, :, None] / 255.0
        rgba[:, :, :3] = (np.array(color, np.float32) * core + np.array(outline, np.float32) * (1 - core)).astype(np.uint8)
        rgba[:, :, 3] = ring
    return rgba


def _thin(pen, rnd, w, h, color, density, outline, outline_px, avoid, width_scale):
    """fine lines only, starting outside the oval to keep clear and running round it, faded out of it"""
    keep = None
    if avoid is not None:
        cx, cy, rx, ry = avoid
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        d = np.sqrt(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2)
        keep = np.clip((d - 0.85) / 0.35, 0, 1)  # 0 inside the oval, rising to 1 just outside it
    else:
        cx, cy = w / 2, h / 2
    for _ in range(int(round(rnd.uniform(8, 16) * density))):
        for _try in range(20):
            o = np.array([rnd.uniform(0, w), rnd.uniform(0, h)], np.float32)
            if keep is None or keep[int(o[1]), int(o[0])] > 0.9:
                break
        around = math.atan2(o[1] - cy, o[0] - cx) + rnd.choice([-1, 1]) * math.pi / 2 + rnd.uniform(-0.6, 0.6)
        kind = rnd.random()
        if kind < 0.6:
            pts = pen.walk(o, around, rnd.uniform(100, 380), rnd.uniform(16, 60), rnd.uniform(0.5, 1.4), snap=math.pi / 2)
            pen.poly(pts, [rnd.choice([1.5, 2, 2.5, 3]) for _ in pts])
        elif kind < 0.8:
            drip(pen, o, around)
        else:  # a small blade, never a big wedge
            n, length = 10, rnd.uniform(80, 220) * pen.k
            pts = [o + (i / n) * length * np.array([math.cos(around), math.sin(around)]) for i in range(n + 1)]
            peak, top = rnd.uniform(0.2, 0.6), rnd.choice([5, 7, 9])
            pen.poly(pts, [max(1.2, top * (t / peak if t < peak else (1 - t) / (1 - peak))) for t in (i / n for i in range(n + 1))])
    return _finish(pen, color, outline, outline_px, keep)


def glitch(rgba, seed, amount=1.0):
    """break a drawing up so it sits inside a CRT / video-glitch look rather than on top of it:
    - pixel-sorted smears: on some rows each run of line pixels is dragged sideways into a streak that fades out;
    - band shifts: a few horizontal bands of the drawing slip left or right;
    - colour split: red and blue pulled a few pixels apart, so the strokes fringe like a mis-converged tube;
    - dropouts: blocks of the drawing missing for this frame."""
    rnd = random.Random("glitch %s" % seed)
    h, w = rgba.shape[:2]
    out = rgba.astype(np.float32)
    a = out[:, :, 3]
    rows = np.where(a.max(axis=1) > 0)[0]
    for y in rows:
        if rnd.random() > 0.22 * amount:
            continue
        line = out[y]
        on = np.where(line[:, 3] > 40)[0]
        if len(on) == 0:
            continue
        direction = rnd.choice([-1, 1])
        length = int(rnd.uniform(20, 160) * amount)
        start = on[-1] if direction > 0 else on[0]
        src = line[start].copy()
        for i in range(1, length):
            x = start + direction * i
            if x < 0 or x >= w:
                break
            fade = (1 - i / length) ** 1.6
            if line[x, 3] < src[3] * fade:
                line[x, :3] = src[:3]
                line[x, 3] = src[3] * fade
    for _ in range(rnd.randint(2, 5)):
        y0 = rnd.randrange(h)
        bh = rnd.randint(4, 34)
        out[y0:y0 + bh] = np.roll(out[y0:y0 + bh], int(rnd.uniform(-70, 70) * amount), axis=1)
    k = max(1, int(3 * amount))
    split = out.copy()
    split[:, :, 0] = np.roll(out[:, :, 0], k, axis=1)
    split[:, :, 2] = np.roll(out[:, :, 2], -k, axis=1)
    split[:, :, 3] = np.maximum(out[:, :, 3], np.maximum(np.roll(out[:, :, 3], k, axis=1), np.roll(out[:, :, 3], -k, axis=1)) * 0.7)
    out = split
    for _ in range(rnd.randint(1, 4)):
        x0, y0 = rnd.randrange(w), rnd.randrange(h)
        out[y0:y0 + rnd.randint(20, 160), x0:x0 + rnd.randint(40, 300), 3] = 0
    return np.clip(out, 0, 255).astype(np.uint8)


def sequence(n, size, matte=None, color=(30, 140, 255), density=1.0, seed="cyberpsycho", on=2):
    """n frames, a new drawing every 'on' frames (the references animate on twos)"""
    held = None
    for f in range(n):
        if f % on == 0:
            held = frame("%s %d" % (seed, f // on), size, matte, color, density)
        yield held


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--matte", help="the subject's matte or RGBA cut-out; lines start inside it")
    ap.add_argument("--size", default="1920x1080")
    ap.add_argument("--frames", type=int, default=60)
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--color", default="30,140,255", help="R,G,B")
    ap.add_argument("--density", type=float, default=1.0)
    ap.add_argument("--seed", default="cyberpsycho")
    ap.add_argument("--out", required=True, help="a .mov (ProRes 4444 with alpha)")
    a = ap.parse_args()
    W, H = map(int, a.size.split("x"))
    matte = None
    if a.matte:
        m = cv2.imread(a.matte, cv2.IMREAD_UNCHANGED)
        matte = m[:, :, 3] if m.ndim == 3 and m.shape[2] == 4 else (m if m.ndim == 2 else cv2.cvtColor(m, cv2.COLOR_BGR2GRAY))
        matte = cv2.resize(matte, (W, H))
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", "%dx%d" % (W, H),
                          "-r", str(a.fps), "-i", "-", "-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt",
                          "yuva444p10le", a.out], stdin=subprocess.PIPE)
    for fr in sequence(a.frames, (W, H), matte, tuple(int(v) for v in a.color.split(",")), a.density, a.seed):
        p.stdin.write(fr.tobytes())
    p.stdin.close()
    p.wait()
    print("wrote", a.out)
