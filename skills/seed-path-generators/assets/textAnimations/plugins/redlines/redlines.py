"""redlines: the two red line forms of the Cyberpunk: Edgerunners 2 trailer (urV5GzXcXsQ, frames 1020-1139; matt
picked them, 2026-11-15), as generators that follow a path or wrap a matte. Seeds come from the trailer's own frames
with numpy (projects/opening/ref/cyberpunk_edits/urV5GzXcXsQ/lines_1029/).

Measured (1280 px wide source, scaled to the output):
  cracks  the title cards (near-black, value ~28): thin glowing lines running top to bottom through the words, long
          straight runs with sharp angle changes, a fork or two, cover 2-5% of the frame; core red (236, 37, 58) RGB,
          3-6 px with thick slabs up to ~35 px, a wide soft glow; a new shape every frame
  slashes over the shots: flat hard-edged ribbons (231, 0, 58) RGB, no glow, swooping and looping, crossing each
          other, tapering to points, thorny spurs; 5-24% of the frame, widths from hairlines to 100+ px slabs,
          wrapping round a hand / face; a new drawing every frame

extract: red mask per frame -> thinned to a skeleton -> traced into polylines; each polyline stored as its shape
(offsets from its own chord, along its length 0..1) and its width profile (distance transform), in seeds/*.json, split
into cracks (dark frames) and slashes (shot frames).
cracks(variation, path, size): a seed crack's shape laid along the path (path normal offsets), its widths, a fork,
          jittered new each variation; glow; RGBA
slashes(variation, size, matte=None, path=None, n=None): ribbons whose routes loop round the matte (its outline pushed
          out, arcs taken, swooping off past it) or run along the path; each carries a seed's wobble and width profile;
          flat colour, hard edges, thorns; RGBA
sheet out.jpg: reference frames, seed skeletons, generated cracks (through a stand-in word), generated slashes (round
          a face)."""
import glob
import json
import math
import os
import random
import sys

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
SRC = os.path.join(REPO, "projects", "opening", "ref", "cyberpunk_edits", "urV5GzXcXsQ", "lines_1029")
SEEDS = os.path.join(HERE, "seeds")
CRACK_RGB = (236, 37, 58)
SLASH_RGB = (231, 0, 58)


# ---------------------------------------------------------------- extraction
def red_mask(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = hsv[:, :, 0].astype(int), hsv[:, :, 1], hsv[:, :, 2]
    return ((((h < 10) | (h > 165)) & (s > 140) & (v > 110)).astype(np.uint8))


def thin(m):
    """Zhang-Suen thinning, numpy"""
    img = (m > 0).astype(np.uint8)
    while True:
        changed = False
        for step in (0, 1):
            p = np.pad(img, 1)
            n = [p[:-2, 1:-1], p[:-2, 2:], p[1:-1, 2:], p[2:, 2:], p[2:, 1:-1], p[2:, :-2], p[1:-1, :-2], p[:-2, :-2]]
            B = sum(x.astype(int) for x in n)
            A = sum(((n[i] == 0) & (n[(i + 1) % 8] == 1)).astype(int) for i in range(8))
            if step == 0:
                c = (n[0] * n[2] * n[4] == 0) & (n[2] * n[4] * n[6] == 0)
            else:
                c = (n[0] * n[2] * n[6] == 0) & (n[0] * n[4] * n[6] == 0)
            rm = (img == 1) & (B >= 2) & (B <= 6) & (A == 1) & c
            if rm.any():
                img[rm] = 0; changed = True
        if not changed:
            return img


def trace(sk, min_px=30):
    """skeleton -> polylines: walk from endpoints (and leftover loops), stopping at junctions"""
    sk = sk.copy()
    H, W = sk.shape
    nb = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    def neigh(y, x):
        return [(y + dy, x + dx) for dy, dx in nb if 0 <= y + dy < H and 0 <= x + dx < W and sk[y + dy, x + dx]]

    out = []
    ys, xs = np.nonzero(sk)
    pts = list(zip(ys, xs))
    ends = [p for p in pts if len(neigh(*p)) == 1]
    for start in ends + pts:
        if not sk[start]:
            continue
        line = [start]; sk[start] = 0; cur = start
        while True:
            nx = neigh(*cur)
            if len(nx) != 1:
                if not nx:
                    break
                nx = [min(nx, key=lambda q: abs(q[0] - cur[0]) + abs(q[1] - cur[1]))]
            cur = nx[0]; sk[cur] = 0; line.append(cur)
        if len(line) >= min_px:
            out.append(np.array([(x, y) for y, x in line], np.float32))
    return out


def describe(poly, dist):
    """a polyline as a shape: offsets from its chord over arc 0..1, its width profile, its length and angle"""
    poly = poly[::2] if len(poly) > 80 else poly
    a, b = poly[0], poly[-1]
    d = b - a
    L = float(np.hypot(*d)) or 1.0
    u, n = d / L, np.array([-d[1], d[0]], np.float32) / L
    rel = poly - a
    t = rel @ u / L
    off = rel @ n / L
    iy = np.clip(poly[:, 1].astype(int), 0, dist.shape[0] - 1); ix = np.clip(poly[:, 0].astype(int), 0, dist.shape[1] - 1)
    w = 2 * dist[iy, ix] / L
    return {"t": t.round(4).tolist(), "off": off.round(4).tolist(), "w": w.round(4).tolist(), "len": round(L, 1),
            "angle": round(math.degrees(math.atan2(d[1], d[0])), 1)}


def extract():
    os.makedirs(SEEDS, exist_ok=True)
    cracks, slashes = [], []
    for f in sorted(glob.glob(os.path.join(SRC, "f_*.png"))):
        im = cv2.imread(f)
        im = cv2.resize(im, (640, 360), interpolation=cv2.INTER_AREA)
        m = red_mask(im)
        if m.mean() < 0.005:
            continue
        dark = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)[:, :, 2].mean() < 40
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
        dist = cv2.distanceTransform(m, cv2.DIST_L2, 3)
        for poly in trace(thin(m), 25 if dark else 30):
            s = describe(poly, dist)
            s["frame"] = int(os.path.basename(f)[2:6])
            (cracks if dark else slashes).append(s)
        cv2.imwrite(os.path.join(SEEDS, "mask_%s.png" % os.path.basename(f)[2:6]), m * 255)
    json.dump(cracks, open(os.path.join(SEEDS, "cracks.json"), "w"))
    json.dump(slashes, open(os.path.join(SEEDS, "slashes.json"), "w"))
    print(len(cracks), "crack seeds,", len(slashes), "slash seeds")


def _load(kind):
    return json.load(open(os.path.join(SEEDS, kind + ".json")))


# ---------------------------------------------------------------- drawing
def _ribbon(mask, pts, widths):
    """a filled variable-width ribbon (hard edged), drawn as overlapping quads so it can bend sharply"""
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        d = b - a
        L = float(np.hypot(*d))
        if L < 0.5:
            continue
        n = np.array([-d[1], d[0]], np.float32) / L
        wa, wb = max(0.8, widths[i] / 2), max(0.8, widths[i + 1] / 2)
        q = np.array([a + n * wa, b + n * wb, b - n * wb, a - n * wa], np.float32)
        cv2.fillPoly(mask, [np.round(q * 4).astype(np.int32)], 255, cv2.LINE_AA, shift=2)
        cv2.circle(mask, (int(b[0]), int(b[1])), int(max(0, wb - 0.5)), 255, -1, cv2.LINE_AA)


def _along(path, s, n=200):
    """the path resampled to n points over arc 0..1, with tangent normals"""
    p = np.asarray(path, np.float32)
    seg = np.hypot(*np.diff(p, axis=0).T)
    arc = np.concatenate([[0], np.cumsum(seg)]); arc /= arc[-1] or 1
    tt = np.clip(np.asarray(s, np.float32), 0, 1)
    x = np.interp(tt, arc, p[:, 0]); y = np.interp(tt, arc, p[:, 1])
    pts = np.stack([x, y], 1)
    tan = np.gradient(pts, axis=0); tan /= np.hypot(*tan.T)[:, None] + 1e-6
    return pts, np.stack([-tan[:, 1], tan[:, 0]], 1), float(arc[-1] and np.sum(seg))


def _lay(seed, path, rnd, amp=1.0, wscale=1.0):
    """a seed's shape laid along a path: its chord offsets applied along the path's normals"""
    t = np.asarray(seed["t"], np.float32); off = np.asarray(seed["off"], np.float32); w = np.asarray(seed["w"], np.float32)
    o = np.argsort(t); t, off, w = t[o], off[o], w[o]
    t = (t - t.min()) / max(1e-6, t.max() - t.min())
    if rnd.random() < 0.5:
        off = -off
    pts, nrm, L = _along(path, t)
    return pts + nrm * (off * L * amp)[:, None], w * L * wscale


# crack geometry measured off the title cards (contours simplified to corners, 640 px wide): runs of 13 / 25 / 58 /
# 142 px (quartiles, 95th), angle from vertical 10 / 27 / 51 / 73 deg (quartiles, 90th): long near-vertical runs,
# short sharp kinks, now and then a long diagonal fold back across (the "Z")
RUN_Q = [13.3, 25.1, 57.8, 141.9]
ANG_Q = [10.2, 26.6, 51.1, 72.8]


def _q(rnd, qs):
    """a draw from the measured quartiles (piecewise uniform between them)"""
    i = rnd.randrange(len(qs) - 1)
    return rnd.uniform(qs[i], qs[i + 1])


def crack_route(rnd, path, size):
    """a crack following the path down the frame: straight runs at the measured lengths and angles, kinks, a fold"""
    W, H = size
    k = W / 640.0
    p = np.asarray(path, np.float32)
    pts, guide, _ = _along(p, np.linspace(0, 1, 60))
    cur = pts[0].copy(); out = [cur.copy()]
    i = 0
    folded = False
    while cur[1] < H + 20 and len(out) < 80:
        g = guide[min(len(guide) - 1, i)]
        tgt = pts[min(len(pts) - 1, i + 6)]
        L = _q(rnd, RUN_Q + [200]) * k * (1.4 if rnd.random() < 0.3 else 1)
        a = math.radians(_q(rnd, [0] + ANG_Q)) * rnd.choice([-1, 1])
        pull = (tgt[0] - cur[0]) / max(40 * k, abs(tgt[1] - cur[1]) + 1)       # back towards the path
        a = 0.6 * a + 0.4 * math.atan(pull)
        if not folded and rnd.random() < 0.12:                                # the Z: a long fold back up across
            folded = True
            d = rnd.choice([-1, 1])
            cur = cur + np.array([d * rnd.uniform(60, 140) * k, -rnd.uniform(30, 90) * k], np.float32); out.append(cur.copy())
            cur = cur + np.array([-d * rnd.uniform(80, 160) * k, rnd.uniform(60, 120) * k], np.float32); out.append(cur.copy())
            continue
        cur = cur + np.array([math.sin(a), math.cos(a)], np.float32) * L
        out.append(cur.copy())
        i = int(np.argmin(np.abs(pts[:, 1] - cur[1])))
    return np.array(out, np.float32)


def hug(route, avoid, pad=10, step=6.0):
    """the route bent round a mask (the letters): densified, and every point inside the mask (grown by pad) pushed out
    to its edge along the shortest way, so the line runs round each letter's outline instead of through it"""
    if avoid is None:
        return route
    m = cv2.dilate((avoid > 128).astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * pad + 1, 2 * pad + 1)))
    if not m.any():
        return route
    dist = cv2.distanceTransform(m, cv2.DIST_L2, 5)
    gy, gx = np.gradient(cv2.GaussianBlur(dist, (0, 0), 3))
    pts = [route[0]]
    for a, b in zip(route[:-1], route[1:]):
        n = max(1, int(np.hypot(*(b - a)) / step))
        pts += [a + (b - a) * t for t in np.linspace(0, 1, n + 1)[1:]]
    H, W = m.shape
    out = []
    for p in pts:
        q = p.astype(np.float32).copy()
        for _ in range(60):
            x, y = int(q[0]), int(q[1])
            if not (0 <= x < W and 0 <= y < H) or not m[y, x]:
                break
            g = np.array([-gx[y, x], -gy[y, x]], np.float32)
            g /= (np.hypot(*g) + 1e-6)
            q += g * 3
        out.append(q)
    return np.array(out, np.float32)


def cracks(variation, path, size=(1920, 1080), avoid=None):
    W, H = size
    rnd = random.Random("cracks %s" % variation)
    mask = np.zeros((H, W), np.uint8)
    k = W / 640.0
    for li in range(rnd.choice([1, 1, 2])):
        route = hug(crack_route(rnd, np.asarray(path, np.float32) + (li * rnd.uniform(-40, 40) * k, 0), size), avoid)
        # thin core with a thick slab here and there (2-6 px core, slabs to ~30 px at 1920)
        w = np.array([rnd.choice([1.6, 2.0, 2.6]) * k for _ in route], np.float32)
        for _ in range(rnd.randint(0, 2)):
            j = rnd.randrange(len(w)); w[j:j + 2] = rnd.uniform(4, 10) * k
        _ribbon(mask, route, w)
        for _ in range(rnd.randint(0, 2)):      # a fork: a short stepped spur off a corner
            j = rnd.randrange(1, max(2, len(route) - 1))
            ang = rnd.uniform(0.6, 1.4) * rnd.choice([-1, 1])
            ln = _q(rnd, RUN_Q) * k * 1.5
            q = [route[j], route[j] + ln * np.array([math.sin(ang), -math.cos(ang) * rnd.choice([-1, 1])], np.float32)]
            q.append(q[-1] + _q(rnd, RUN_Q) * k * np.array([math.sin(-ang), math.cos(ang)], np.float32))
            _ribbon(mask, np.array(q, np.float32), [1.5 * k, 1.2 * k, 0.8 * k])
    # the scan tear: rows of the line smeared sideways, as on the trailer's lines
    for _ in range(rnd.randint(6, 16)):
        y, bh = rnd.randrange(H), rnd.randint(1, 3)
        row = mask[y:y + bh].astype(np.float32)
        sm = cv2.blur(row, (int(rnd.uniform(10, 40) * k) | 1, 1))
        mask[y:y + bh] = np.maximum(mask[y:y + bh], (sm * 1.5).clip(0, 255).astype(np.uint8))
    a = mask.astype(np.float32) / 255
    glow = cv2.GaussianBlur(a, (0, 0), 3 * k) * 0.8 + cv2.GaussianBlur(a, (0, 0), 12 * k) * 0.5
    alpha = np.clip(a + glow, 0, 1)
    rgb = np.zeros((H, W, 3), np.float32); rgb[:] = CRACK_RGB
    hot = a[:, :, None]
    rgb = rgb * (1 - 0.3 * hot) + np.array([255, 150, 160], np.float32) * 0.3 * hot
    return np.dstack([rgb, alpha * 255]).astype(np.uint8)


def _loop_route(rnd, matte, size):
    """a route round the matte: its outline pushed out, an arc of it, swooping off past it at both ends"""
    W, H = size
    k = W / 640.0
    m = cv2.dilate((matte > 128).astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (int(rnd.uniform(5, 60) * k) | 1,) * 2))
    cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    c = max(cs, key=len)[:, 0, :].astype(np.float32)
    s = rnd.randrange(len(c)); seg = int(len(c) * rnd.uniform(0.25, 0.6))
    arc = np.roll(c, -s, axis=0)[:seg:max(1, seg // 40)]
    out = []
    for end, sign in ((arc[0], -1), (arc[-1], 1)):                # swoop off along the tangent, past the frame
        j = 1 if sign < 0 else -2
        t = (end - arc[j]); t /= np.hypot(*t) + 1e-6
        bend = rnd.uniform(-0.6, 0.6)
        R = np.array([[math.cos(bend), -math.sin(bend)], [math.sin(bend), math.cos(bend)]], np.float32)
        far = end + (R @ t) * rnd.uniform(0.3, 0.9) * W
        out.append([end + (far - end) * q for q in (0.33, 0.66, 1.0)])
    return np.vstack([out[0][::-1], arc, out[1]])


def _smooth(route, n=160):
    """a smooth curve through the route's points (Catmull-Rom), so the ribbons sweep"""
    p = np.asarray(route, np.float32)
    if len(p) > 12:
        p = p[np.linspace(0, len(p) - 1, 12).astype(int)]
    p = np.vstack([p[0], p, p[-1]])
    out = []
    for i in range(1, len(p) - 2):
        for t in np.linspace(0, 1, max(2, n // (len(p) - 3)), endpoint=False):
            a, b, c, d = p[i - 1], p[i], p[i + 1], p[i + 2]
            out.append(0.5 * ((2 * b) + (-a + c) * t + (2 * a - 5 * b + 4 * c - d) * t * t + (-a + 3 * b - 3 * c + d) * t ** 3))
    out.append(p[-2])
    return np.array(out, np.float32)


def slashes(variation, size=(1920, 1080), matte=None, path=None, n=None):
    W, H = size
    rnd = random.Random("slashes %s" % variation)
    seeds = [s for s in _load("slashes") if s["len"] > 60]
    mask = np.zeros((H, W), np.uint8)
    k = W / 640.0
    for _ in range(n or rnd.randint(2, 5)):
        if matte is not None and rnd.random() < 0.6:
            route = _loop_route(rnd, matte, size)
        elif path is not None:
            route = np.asarray(path, np.float32) + np.array([rnd.uniform(-0.1, 0.1) * W, rnd.uniform(-0.1, 0.1) * H], np.float32)
        else:
            a = rnd.uniform(0, math.pi)
            c = np.array([rnd.uniform(0.2, 0.8) * W, rnd.uniform(0.2, 0.8) * H])
            route = np.array([c - 0.8 * W * np.array([math.cos(a), math.sin(a)]), c + 0.8 * W * np.array([math.cos(a), math.sin(a)])], np.float32)
        sd = rnd.choice(seeds)
        route = _smooth(route)
        pts, w = _lay(sd, route, rnd, amp=rnd.uniform(0.01, 0.04))
        pts = cv2.GaussianBlur(pts.reshape(-1, 1, 2), (1, 9), 0).reshape(-1, 2) if len(pts) > 9 else pts
        # width: the seed's profile, scaled to a hairline, a stroke, or a slab; tapered ends
        big = rnd.choice([2, 6, 10, 14, 20, 30])
        prof = np.asarray(w, np.float32); prof = prof / (prof.max() or 1)
        tt = np.linspace(0, 1, len(prof))
        taper = np.clip(np.minimum(tt, 1 - tt) / rnd.uniform(0.08, 0.25), 0, 1) ** 0.8
        ww = np.maximum(0.6, big * k * (0.35 + 0.65 * prof) * taper)
        _ribbon(mask, pts, ww)
        for _ in range(rnd.randint(0, 3)):                      # thorns off the edge
            i = rnd.randrange(len(pts))
            d = pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]
            nn = np.array([-d[1], d[0]], np.float32) / (np.hypot(*d) + 1e-6) * rnd.choice([-1, 1])
            tip = pts[i] + nn * rnd.uniform(10, 40) * k + d / (np.hypot(*d) + 1e-6) * rnd.uniform(-10, 25) * k
            _ribbon(mask, np.array([pts[i], tip], np.float32), [ww[i] * 0.8 + 2, 0.5])
    if rnd.random() < 0.2:                                      # a corner cut solid red
        cx, cy = rnd.choice([(0, 0), (W, 0), (0, H), (W, H)])
        cv2.fillPoly(mask, [np.array([(cx, cy), (abs(cx - rnd.uniform(0.2, 0.45) * W), cy), (cx, abs(cy - rnd.uniform(0.3, 0.7) * H))], np.int32)], 255, cv2.LINE_AA)
    rgba = np.zeros((H, W, 4), np.uint8)
    rgba[:, :, :3] = SLASH_RGB
    rgba[:, :, 3] = mask
    return rgba


# ---------------------------------------------------------------- sheet
def _over(bg, rgba):
    a = rgba[:, :, 3:4].astype(np.float32) / 255
    return (bg.astype(np.float32) * (1 - a) + rgba[:, :, :3][:, :, ::-1].astype(np.float32) * a).astype(np.uint8)


def sheet(out):
    T = (320, 180)
    W, H = 1920, 1080
    ref = [cv2.resize(cv2.imread(os.path.join(SRC, "f_%04d.png" % f)), T) for f in (1030, 1048, 1068, 1105, 1040, 1061, 1078, 1117)]
    sk = []
    for f in (1030, 1048, 1068, 1105, 1040, 1061, 1078, 1117):
        m = cv2.imread(os.path.join(SEEDS, "mask_%04d.png" % f), cv2.IMREAD_GRAYSCALE)
        s = thin(m) * 255 if m is not None else np.zeros((360, 640), np.uint8)
        sk.append(cv2.resize(cv2.cvtColor(np.maximum(s, (m // 3) if m is not None else s).astype(np.uint8), cv2.COLOR_GRAY2BGR), T))
    rows = [np.hstack(ref), np.hstack(sk)]
    # cracks through a stand-in title card
    card = np.full((H, W, 3), (14, 6, 20), np.uint8)
    cv2.putText(card, "T H E   A N I M E", (720, 520), cv2.FONT_HERSHEY_SIMPLEX, 1.6, (90, 200, 255), 3, cv2.LINE_AA)
    cr = []
    for v in range(8):
        x = 700 + 60 * (v % 4)
        path = [(x + (v - 4) * 30, -20), (x + 40, 540), (x - 30 + 10 * v, H + 20)]
        cr.append(cv2.resize(_over(card, cracks("v%d" % v, path)), T))
    rows.append(np.hstack(cr))
    # slashes round a face
    face = cv2.imread(os.path.join(REPO, "projects", "cyberpunk", "outro", "portrait_0.png"))
    face = cv2.resize(face, (W, H))
    g = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
    matte = cv2.morphologyEx((g > 40).astype(np.uint8) * 255, cv2.MORPH_OPEN, np.ones((9, 9), np.uint8))
    sl = [cv2.resize(_over(face, slashes("v%d" % v, matte=matte)), T) for v in range(8)]
    rows.append(np.hstack(sl))
    shot = np.vstack(rows)
    for r, lab in enumerate(["trailer 1020-1139", "seeds (numpy skeletons)", "cracks, generated", "slashes, generated round a face"]):
        cv2.putText(shot, lab, (6, r * 180 + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 2)
    cv2.imwrite(out, shot)


if __name__ == "__main__":
    if sys.argv[1] == "extract":
        extract()
    elif sys.argv[1] == "sheet":
        sheet(sys.argv[2])
