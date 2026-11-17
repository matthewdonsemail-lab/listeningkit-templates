"""Cyberpunk outro (assets/collage/cyberpunk_outro.mp4), after the close-ups:
  flash cut          white, white, black, white
  the logo           the Nous logo in white on black (assets/endcard/nous_logo_white.png), cyberpsycho lines round it
  the push           the 12 frames of the push into the girl in the logo, each redrawn in a random style in its own
                     scene from that frame's composition (projects/cyberpunk/outro/front_*.png), match cuts, 2 frames each
  the back of her    the same 12 framings with her turned round (back_*.png), 2 frames each, the last one (blue
                     chiaroscuro on black, facing away) held with a slow push
  the busts          the six caricatures superimposed (outro/ensemble.png), a slow zoom in
  the portraits      the six caricature portraits (portrait_*.png), each panning slowly, alternating right and left
Glitched cyberpsycho lines run over the logo and the styled frames. The CRT goes over all of it in the comp."""
import os
import subprocess
import sys

import cv2
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "plugins", "cyberpsycho"))
import cyberpsycho  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
CP = os.path.join(HERE, "..", "..", "projects", "cyberpunk", "outro")
OUT = os.path.join(HERE, "collage", "cyberpunk_outro.mp4")
W, H, FPS = 1920, 1080, 30
LOGO_H = 640
FLASH, LOGO, STYLED, BG_FADE, REVEAL, BUSTS, PORTRAIT = 4, 24, 2, 14, 22, 36, 30

logo = cv2.imread(os.path.join(HERE, "endcard", "nous_logo_white.png"), cv2.IMREAD_UNCHANGED)
s = LOGO_H / logo.shape[0]
logo = cv2.resize(logo, (int(logo.shape[1] * s), LOGO_H), interpolation=cv2.INTER_AREA)
lh, lw = logo.shape[:2]
LX, LY = (W - lw) // 2, (H - lh) // 2
logo_a = np.zeros((H, W), np.float32)
logo_a[LY:LY + lh, LX:LX + lw] = logo[:, :, 3] / 255.0


def cover(name):
    im = cv2.imread(os.path.join(CP, name))
    k = max(W / im.shape[1], H / im.shape[0])
    im = cv2.resize(im, (int(im.shape[1] * k + 0.5), int(im.shape[0] * k + 0.5)), interpolation=cv2.INTER_AREA)
    y, x = (im.shape[0] - H) // 2, (im.shape[1] - W) // 2
    return im[y:y + H, x:x + W].astype(np.float32)


fronts = [cover("front_%02d.png" % i) for i in range(12)]
zoomrefs = [cover("zoomref/zoom_%02d.png" % i) for i in range(12)]  # the logo itself at each step of the push

# the push each front frame was drawn from: frame i is the logo frame scaled by K[i] about her face, the face sliding
# to the middle as it grows (as the earlier zoom did), so p_i = K[i] * p_logo + B[i]
FACE = np.array([LX + 0.39 * lw, LY + 0.63 * lh], np.float32)
K, B = [], []
for i in range(12):
    t = i / 12.0
    k = 1 + 4.5 * (2 ** (6 * t) - 1) / 63
    u = min(1.0, (k - 1) / 1.5)
    c = FACE * (1 - u) + np.array([W / 2, H / 2], np.float32) * u
    K.append(k)
    B.append(c - k * FACE)


def into(j, i, pool=None):
    """front frame j re-framed to frame i's zoom, so anything cut from it lands in place on frame i"""
    a = K[i] / K[j]
    b = B[i] - a * B[j]
    return cv2.warpAffine((fronts if pool is None else pool)[j], np.float32([[a, 0, b[0]], [0, a, b[1]]]), (W, H), flags=cv2.INTER_LINEAR,
                          borderMode=cv2.BORDER_REFLECT)


# the collage on her face, as the close-ups do it: rectangles around her face and her features (eyes, nose, mouth),
# cut from the other styles, some blown up, piling up from frame to frame. Positions are kept in the logo's own
# coordinates, so they ride the push. Feature boxes are fractions of the logo (centre x, centre y, w, h).
FEATURES = {"eye": (0.44, 0.63, 0.20, 0.07), "eye2": (0.31, 0.62, 0.12, 0.07), "nose": (0.33, 0.70, 0.10, 0.08),
            "mouth": (0.34, 0.76, 0.14, 0.06), "brow": (0.40, 0.57, 0.30, 0.06)}
crng = np.random.default_rng(23)
patches = []  # (source style, centre x, centre y, w, h in logo-frame pixels, zoom, brightness, offset x, offset y)


def new_patch(kind):
    j = int(crng.integers(0, 12))
    if kind == "strip":
        return ("screen", float(crng.uniform(0.0, 1.0)), float(crng.uniform(0.0, 1.0)),
                float(crng.uniform(0.18, 0.55)), float(crng.uniform(0.10, 0.45)), int(crng.integers(0, 12)),
                float(crng.choice([0.85, 1.0, 1.0, 1.15])))
    else:
        fx, fy, fw, fh = FEATURES[str(crng.choice(list(FEATURES)))]
        cx, cy, w, h = LX + fx * lw, LY + fy * lh, fw * lw * 1.6, fh * lh * 1.8  # bigger boxes round each feature
        z = float(crng.uniform(1.3, 2.0))  # blown up, like the close-ups
    return (j, cx, cy, w, h, z, float(crng.choice([0.85, 1.0, 1.15])), crng.uniform(-0.04, 0.04) * lw,
            crng.uniform(-0.03, 0.03) * lh)


def collage(i, pool=None):
    pool = fronts if pool is None else pool
    frame = pool[i].copy()
    warped = {}
    for patch_ in patches:
        if patch_[0] == "screen":
            # a large rectangle anywhere across the whole scene, taken from another style at the same zoom, in place
            _, fx, fy, fw, fh, j, br = patch_
            if j == i:
                continue
            if j not in warped:
                warped[j] = into(j, i, pool)
            pw, ph = int(fw * W), int(fh * H)
            px, py = int(fx * (W - pw)), int(fy * (H - ph))
            frame[py:py + ph, px:px + pw] = warped[j][py:py + ph, px:px + pw] * br
            continue
        j, cx, cy, w, h, z, br, ox, oy = patch_
        if j == i:
            continue
        if j not in warped:
            warped[j] = into(j, i, pool)
        src = warped[j]
        k = K[i]
        X, Y = k * (cx + ox) + B[i][0], k * (cy + oy) + B[i][1]
        pw, ph = int(k * w), int(k * h)
        if pw < 8 or ph < 8 or pw >= W or ph >= H:
            continue
        sx, sy = k * cx + B[i][0], k * cy + B[i][1]
        sw, sh = pw / z, ph / z
        x0, y0 = int(np.clip(sx - sw / 2, 0, W - sw)), int(np.clip(sy - sh / 2, 0, H - sh))
        crop = src[y0:y0 + int(sh), x0:x0 + int(sw)]
        if crop.size == 0:
            continue
        patch = cv2.resize(crop, (pw, ph)) * br
        px, py = int(np.clip(X - pw / 2, 0, W - pw)), int(np.clip(Y - ph / 2, 0, H - ph))
        frame[py:py + ph, px:px + pw] = patch
    return frame
backs = [cover("back_%02d.png" % i) for i in range(12)]
busts = cover("ensemble.png")
_g = cv2.imread(os.path.join(CP, "back_11_girl.png"), cv2.IMREAD_UNCHANGED)  # make_outro_girl_matte.py
_k = max(W / _g.shape[1], H / _g.shape[0])
_g = cv2.resize(_g, (int(_g.shape[1] * _k + 0.5), int(_g.shape[0] * _k + 0.5)), interpolation=cv2.INTER_AREA)
_y, _x = (_g.shape[0] - H) // 2, (_g.shape[1] - W) // 2
_g = _g[_y:_y + H, _x:_x + W].astype(np.float32)
girl_rgb, girl_a = _g[:, :, :3], _g[:, :, 3:4] / 255.0
BUSTS_IN = 1.0  # the busts' zoom when they first fade in; it carries on through the busts shot
portraits = [cover("portrait_%d.png" % i) for i in range(6)]


def scale_about(img, k, dx=0.0):
    m = np.float32([[k, 0, W / 2 * (1 - k) + dx], [0, k, H / 2 * (1 - k)]])
    return cv2.warpAffine(img, m, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)


def lines_over(frame, seed, matte=None):
    lines = cyberpsycho.frame(seed, (W, H), matte, (225, 240, 255), 0.5, outline=(0, 0, 0), outline_px=2)
    lines = cyberpsycho.glitch(lines, seed, 1.0)
    la = lines[:, :, 3:4].astype(np.float32) / 255.0
    return frame * (1 - la) + lines[:, :, 2::-1].astype(np.float32) * la


seq = []  # (kind, index, t within its shot)
seq += [("flash", i, 0) for i in range(FLASH)]
seq += [("logo", i, 0) for i in range(LOGO)]
for i in range(12):
    # each step of the push: her face in that style with the collage building on it (2 frames clean then 2 cut up,
    # every other step), and the Nous logo at that same zoom cut in between on alternate steps
    seq += [("front", i, 0), ("front", i, 0), ("collage", i, 0), ("collage", i, 0)] if i % 2 == 0 else \
           [("front", i, 0), ("collage", i, 0), ("logo_at", i, 0)]
for i in range(11):
    seq += [("back", i, 0), ("back", i, 0), ("bcollage", i, 0), ("bcollage", i, 0)] if i % 2 == 0 else            [("back", i, 0), ("bcollage", i, 0)]
# the last shot: her (cut out with OpenCV) stays while her background fades to black, then the busts fade in behind
# her and she pushes in, Gaussian-blurring away, leaving the busts on their slow zoom
seq += [("bgfade", 11, j / (BG_FADE - 1)) for j in range(BG_FADE)]
seq += [("reveal", 0, j / (REVEAL - 1)) for j in range(REVEAL)]
seq += [("busts", 0, j / (BUSTS - 1)) for j in range(BUSTS)]
for i in range(6):
    seq += [("portrait", i, j / (PORTRAIT - 1)) for j in range(PORTRAIT)]

def main():
    """render the outro as one flat video (a reference; the comp builds it from layers: make_cyberpunk_outro_comp.py)"""
    global patches
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", "%dx%d" % (W, H),
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "14", "-pix_fmt", "yuv420p", OUT],
                         stdin=subprocess.PIPE)
    logo_matte = cv2.dilate((logo_a > 0.5).astype(np.uint8) * 255, np.ones((25, 25), np.uint8))
    for f, (kind, i, t) in enumerate(seq):
        on2 = f - f % 2  # the lines are redrawn on twos
        if kind == "flash":
            frame = np.full((H, W, 3), 0.0 if i == 2 else 255.0, np.float32)
        elif kind == "logo":
            frame = np.repeat(logo_a[:, :, None] * 255.0, 3, axis=2)
            frame = lines_over(frame, "outro logo %d" % on2, logo_matte)
            frame = frame * (1 - logo_a[:, :, None]) + 255.0 * logo_a[:, :, None]
        elif kind == "front":
            frame = lines_over(fronts[i].copy(), "outro front %d" % on2)
        elif kind == "collage":
            if f % 2 == 0:  # new pieces on twos, piling up: big strips round her face and her features blown up
                patches += [new_patch("strip") for _ in range(int(crng.integers(2, 4)))]
                patches += [new_patch("feature") for _ in range(int(crng.integers(1, 3)))]
                patches = patches[-12:]
            frame = lines_over(collage(i), "outro collage %d" % on2)
        elif kind == "logo_at":
            frame = zoomrefs[i].copy()  # the Nous logo at exactly this step of the push: a perfect match cut
        elif kind == "back":
            frame = lines_over(backs[i].copy(), "outro back %d" % on2)
        elif kind == "bcollage":
            if f % 2 == 0:
                patches += [new_patch("strip") for _ in range(int(crng.integers(2, 4)))]
                patches += [new_patch("feature") for _ in range(int(crng.integers(1, 3)))]
                patches = patches[-12:]
            frame = lines_over(collage(i, backs), "outro bcollage %d" % on2)
        elif kind == "bgfade":
            k = 1.0 + 0.02 * t
            bg = scale_about(backs[11], k) * (1 - t)  # her background fades to black
            ga = scale_about(girl_a, k)[:, :, None] if girl_a.ndim == 2 else scale_about(girl_a[:, :, 0], k)[:, :, None]
            frame = bg * (1 - ga) + scale_about(girl_rgb, k) * ga
        elif kind == "reveal":
            def ease(x):
                x = min(1.0, max(0.0, x))
                return x * x * x  # ease-in: slow to start, then dropping away
            fade = min(1.0, t / 0.85)
            under = scale_about(busts, BUSTS_IN + 0.02 * t) * (fade * fade * (3 - 2 * fade))  # the busts, pushing in underneath, fading up from black
            girl_dy = int(H * 1.05 * ease((t - 0.15) / 0.85))  # she slides down and away (no black plate over the busts)
            frame = under.copy()
            k = 1.02 + 0.18 * t
            sigma = 0.5 + 18 * t ** 1.5
            ga = scale_about(girl_a[:, :, 0], k)
            gr = scale_about(girl_rgb, k)
            ks = int(sigma * 3) * 2 + 1
            pre = cv2.GaussianBlur(gr * ga[:, :, None], (ks, ks), sigma)
            ga = cv2.GaussianBlur(ga, (ks, ks), sigma)
            m = np.float32([[1, 0, 0], [0, 1, girl_dy]])
            pre = cv2.warpAffine(pre, m, (W, H))
            ga = cv2.warpAffine(ga, m, (W, H))[:, :, None]
            frame = frame * (1 - ga) + pre
        elif kind == "busts":
            frame = scale_about(busts, BUSTS_IN + 0.02 + 0.08 * t)  # a slow zoom in on the busts
        else:
            d = 1 if i % 2 == 0 else -1  # alternate: one pans right, the next left, slowly
            frame = scale_about(portraits[i], 1.08, d * (-45 + 90 * t))
        p.stdin.write(np.clip(frame, 0, 255).astype(np.uint8).tobytes())
    p.stdin.close()
    p.wait()
    print(len(seq), "frames (%.2f s) ->" % (len(seq) / FPS), OUT)


if __name__ == "__main__":
    main()
