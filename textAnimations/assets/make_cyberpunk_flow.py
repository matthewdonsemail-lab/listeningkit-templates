"""Cyberpunk opening as one video (assets/collage/cyberpunk_opening_flow.mp4, 0-2.0 s of the pre-comp): the girl on
her own layer (projects/cyberpunk/girl.png, make_cyberpunk_matte.py), sharp and still, over a background that lives:
- the crowd moments (open_a-g) cycle a new one every frame, every third frame one of them in the intro's anime or
  light-being style (styles/open_<k>_<style>.png; open_b's are shot3/shot1), so the people flicker through styles;
- a slow shutter: each background frame is blended with the ones before (exponential decay), so the people drag into
  ghost trails, like a long exposure;
- zoom streaks radiating from her, stronger as the push builds, as if the shutter stays open through the zoom;
- the light bends: the background is warped in a swirl around her that grows and turns;
- film noise on the background only.
Over the last 0.6 s the glitch slices (as make_cyberpunk_collage.py) cut around her; the final 4 frames are clean."""
import os
import random
import subprocess

import sys

import cv2
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "plugins", "cyberpsycho"))
import cyberpsycho  # noqa: E402  the blue cyberpsychosis lines, coming out from behind her

CP = "C:/Users/0/.buzz/REPOS/listeningkit-templates/projects/cyberpunk/"
OUT = "C:/Users/0/.buzz/REPOS/listeningkit-templates/textAnimations/assets/collage/cyberpunk_opening_flow.mp4"
W, H, FPS = 1920, 1080, 30
# timed to matt's VO (projects/cyberpunk/audio.mp3, words in audio_words.json; cyberpunk starts at 8.78 s on "split"):
# the crowd alone through "people became fearful, uncertain, doubtful of each other", she appears on "because" (15.10 s),
# and the glitch push ends on the thermogram cut on "now" (17.60 s)
FRAMES, GLITCH_FROM, CLEAN_FROM = 265, 247, 261
CX, CY = 961, 690  # her centre
rnd = random.Random("cyberpunk flow")


def load(path):
    im = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if im.shape[1] != W:
        im = cv2.resize(im, (W, H), interpolation=cv2.INTER_LANCZOS4)
    return im


girl = load(CP + "girl.png").astype(np.float32)
g_rgb, g_a = girl[:, :, :3], girl[:, :, 3:4] / 255.0
APPEAR = 190  # the frame she first appears on (VO "because", 15.10 s)

# her other versions, for the body-quadrant cuts: the same spot in the anime and light-being frames, kept to her shape
her_variants = [load(CP + "shot3.png").astype(np.float32), load(CP + "shot1.png").astype(np.float32)]
for k in "cdefg":
    for s in ("anime", "being"):
        p_ = CP + "styles/open_%s_%s.png" % (k, s)
        if os.path.exists(p_):
            her_variants.append(load(p_).astype(np.float32))
_ys, _xs = np.where(girl[:, :, 3] > 128)
GX0, GX1, GY0, GY1 = int(_xs.min()), int(_xs.max()), int(_ys.min()), int(_ys.max())
FACE_END = GY0 + 110  # her head and face: never swapped
MIDX, MIDY = (GX0 + GX1) // 2, (FACE_END + GY1) // 2
QUADS = [(GX0, FACE_END, MIDX, MIDY), (MIDX, FACE_END, GX1, MIDY), (GX0, MIDY, MIDX, GY1), (MIDX, MIDY, GX1, GY1)]
qrnd = random.Random("cyberpunk her quadrants")


def her_with_quadrants(f):
    """her, and every 6 frames, for 2 frames, one or two quadrants of her body (never her face) from another version"""
    rgb = g_rgb
    if f >= APPEAR + 8 and f % 6 in (0, 1):
        rgb = g_rgb.copy()
        rr = random.Random("quad %d" % (f // 6))
        for q in rr.sample(QUADS, rr.choice([1, 1, 2])):
            x0, y0, x1, y1 = q
            rgb[y0:y1, x0:x1] = rr.choice(her_variants)[y0:y1, x0:x1]
    return rgb


def pixel_sort(rgb, alpha, strength, f):
    """sort her pixels by brightness down each column, within her shape, blended in by strength, with the columns
    slipped up and down a little; strength 1 is fully sorted streaks, 0 is her untouched"""
    if strength <= 0:
        return rgb
    out = rgb.copy()
    x0, x1, y0, y1 = GX0, GX1 + 1, GY0, GY1 + 1
    block = rgb[y0:y1, x0:x1]
    m = alpha[y0:y1, x0:x1, 0] > 0.5
    lum = block.mean(axis=2)
    sorted_block = block.copy()
    rr = np.random.default_rng(1000 + f)
    for c in range(block.shape[1]):
        rows = np.where(m[:, c])[0]
        if len(rows) < 2:
            continue
        order = rows[np.argsort(lum[rows, c])]
        col = block[order, c]
        shift = int(rr.integers(-40, 41) * strength)
        sorted_block[rows, c] = np.roll(col, shift, axis=0)
    out[y0:y1, x0:x1] = block * (1 - strength) + sorted_block * strength
    return out


def exposure_env(f):
    """a blow-out into and out of her appearing: rises over 3 frames, falls over 6"""
    d = f - APPEAR
    if -3 < d <= 0:
        p = (d + 3) / 3.0
    elif 0 < d < 7:
        p = 1 - d / 7.0
    else:
        return 0.0
    return p * p * (3 - 2 * p)
# she is in every background frame too, a little off from the cut-out: paint her out of each with the empty open_a in
# the same style, under a widened, softened copy of her matte, so the cut-out is the only her
hole = cv2.dilate((girl[:, :, 3] > 20).astype(np.uint8) * 255, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (71, 71)))
hole = (cv2.GaussianBlur(hole, (41, 41), 0).astype(np.float32) / 255.0)[:, :, None]
plate = {"photo": load(CP + "open_a.png").astype(np.float32),
         "anime": load(CP + "styles/open_a_anime.png").astype(np.float32),
         "being": load(CP + "styles/open_a_being.png").astype(np.float32)}


def empty(img, style):
    return img * (1 - hole) + plate[style] * hole


photo = {k: empty(load(CP + "open_%s.png" % k).astype(np.float32), "photo") for k in "abcdefg"}
styled = []
for k in "acdefg":
    for s in ("anime", "being"):
        p = CP + "styles/open_%s_%s.png" % (k, s)
        if os.path.exists(p):
            styled.append(empty(load(p).astype(np.float32), s))
styled += [empty(load(CP + "shot3.png").astype(np.float32), "anime"),
           empty(load(CP + "shot1.png").astype(np.float32), "being")]

yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
dx, dy = xx - CX, yy - CY
r = np.sqrt(dx * dx + dy * dy)
theta = np.arctan2(dy, dx)
falloff = np.exp(-(r / 700.0) ** 2)


def bend(img, t):
    """the light bends: a swirl around her, growing and turning, plus a slow ripple"""
    a = (0.10 + 0.35 * t) * falloff * np.sin(2.2 * t * np.pi + r / 260.0)
    ripple = 6.0 * np.sin(r / 45.0 - t * 9.0) * falloff
    mx = CX + (r + ripple) * np.cos(theta + a)
    my = CY + (r + ripple) * np.sin(theta + a)
    return cv2.remap(img, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


def zoom_streak(img, amount, taps=9):
    """the shutter open through the zoom: copies scaled out from her centre, averaged"""
    acc = np.zeros_like(img)
    for i in range(taps):
        s = 1.0 + amount * i / (taps - 1)
        m = np.float32([[s, 0, CX * (1 - s)], [0, s, CY * (1 - s)]])
        acc += cv2.warpAffine(img, m, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    return acc / taps


order = list("abcdefg")
pool = [photo[k] for k in order] + styled
BOX = (0.42, 0.33, 0.57, 0.90)


def slice_onto(frame):
    for _ in range(rnd.randint(4, 9)):
        l, t, rr, b = BOX
        cx, cy = rnd.uniform(l - 0.03, rr + 0.03) * W, rnd.uniform(t, b) * H
        w, h = int(W * rnd.uniform(0.05, 0.20)), int(H * rnd.uniform(0.05, 0.26))
        x, y = int(min(max(cx - w / 2, 0), W - w)), int(min(max(cy - h / 2, 0), H - h))
        src = rnd.choice(styled)
        s = rnd.choice([0.55, 0.75, 1.0, 1.0, 1.4, 1.8])
        sw, sh = w / s, h / s
        sx, sy = int(min(max(x + w / 2 - sw / 2, 0), W - sw)), int(min(max(y + h / 2 - sh / 2, 0), H - sh))
        patch = cv2.resize(src[sy:sy + int(sh), sx:sx + int(sw)], (w, h)) * rnd.choice([0.75, 0.9, 1.15, 1.3])
        ox, oy = int(rnd.uniform(-0.03, 0.03) * W), int(rnd.uniform(-0.03, 0.03) * H)
        px, py = min(max(x + ox, 0), W - w), min(max(y + oy, 0), H - h)
        frame[py:py + h, px:px + w] = patch
    for _ in range(rnd.randint(2, 5)):
        l, t, rr, b = BOX
        h = max(4, int(H * rnd.uniform(0.012, 0.05)))
        y = min(int(rnd.uniform(t, b) * H), H - h)
        x0, x1 = int(max(0, (l - 0.06) * W)), int(min(W, (rr + 0.06) * W))
        strip = rnd.choice(styled)[y:y + h, x0:x1] * rnd.choice([0.8, 1.0, 1.25])
        shift = int(rnd.uniform(-0.06, 0.06) * W)
        px = min(max(x0 + shift, 0), W - (x1 - x0))
        frame[y:y + h, px:px + (x1 - x0)] = strip
    return frame


p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", "%dx%d" % (W, H),
                      "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", OUT],
                     stdin=subprocess.PIPE)
lp = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", "%dx%d" % (W, H),
                       "-r", str(FPS), "-i", "-", "-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", "yuva444p10le",
                       OUT.replace("cyberpunk_opening_flow.mp4", "cyberpunk_lines.mov")], stdin=subprocess.PIPE)
acc = None
held = None
for f in range(FRAMES):
    t = max(0.0, (f - APPEAR) / (FRAMES - 1 - APPEAR))  # the zoom streaks build from her arrival
    # the crowd alone, cycling (she is painted out of every background), then the empty hall for a beat, then her (B),
    # then the crowd cycles every frame
    if f < APPEAR - 5:
        base = rnd.choice(styled) if f % 3 == 0 else photo[order[2 + (f % 5)]]
    elif f < APPEAR:
        base = photo["a"]
    elif f < APPEAR + 4:
        base = photo["b"]
    elif f % 3 == 0:
        base = rnd.choice(styled)
    else:
        base = photo[order[2 + (f % 5)]]
    acc = base.copy() if acc is None else acc * 0.58 + base * 0.42  # the slow shutter: people drag
    bg = zoom_streak(acc, 0.015 + 0.09 * t * t)  # no swirl: just the scenes flowing into each other behind her
    bg += np.random.default_rng(f).normal(0, 9.0, (H, W, 1)).astype(np.float32)  # noise, luminance
    on = 0.0 if f < APPEAR else 1.0  # she isn't there until she appears
    # the cyberpsycho lines go to their own transparent layer (cyberpunk_lines.mov), so they can sit above the CRT
    # and stay clean blue; her silhouette is cut out of them, so they read as coming out from behind her
    if on and f < CLEAN_FROM:
        # bright electric blue with a dark navy edge, so they read on the bright marble and the dark crowd alike
        # near-white so the CRT reads them as its own highlights, a thin dark edge, fewer of them, glitched
        lines = cyberpsycho.frame("cyberpunk flow %d" % (f // 2), (W, H), girl[:, :, 3], (225, 240, 255), 0.6,
                                  outline=(0, 0, 0), outline_px=2)
        lines = cyberpsycho.glitch(lines, "flow %d" % f, 1.0)
        lines[:, :, 3] = (lines[:, :, 3].astype(np.float32) * (1 - g_a[:, :, 0])).astype(np.uint8)
    else:
        lines = np.zeros((H, W, 4), np.uint8)
    lp.stdin.write(lines.tobytes())
    her = her_with_quadrants(f)
    sort_strength = max(0.0, 1 - (f - APPEAR) / 10.0) if f >= APPEAR else 0.0  # she resolves out of the sort
    her = pixel_sort(her, g_a, sort_strength, f)
    frame = bg * (1 - g_a * on) + her * g_a * on
    e = exposure_env(f)
    if e > 0:
        frame = frame * (1 + 2.6 * e) + 40 * e  # the exposure ramp as she appears
    if GLITCH_FROM <= f < CLEAN_FROM:
        if (f - GLITCH_FROM) % 2 == 0:
            held = slice_onto(frame.copy())
        frame = held
    p.stdin.write(np.clip(frame, 0, 255).astype(np.uint8).tobytes())
p.stdin.close()
p.wait()
lp.stdin.close()
lp.wait()
print(FRAMES, "frames ->", OUT)
