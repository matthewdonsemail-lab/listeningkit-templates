"""The opening's cyberpsycho shout (matt, 2026-11-15): the man behind the blinds and the man at the chalkboard shouting
at each other, cut against each other on the beat of the launch music. The base stays the two real shots
(projects/opening/mattgen/Through the Blinds, Wired In Silence.png and Intense Gaze Before the Chalkboard.png), framed
exactly as their clips are in FilmCraft (launchIntro-v1, the Motion below). His cyberpsycho comes through in
rectangles cut from his 12 cyberpsycho stills (images/gen/make_opening_psycho.py) over the parts of his face: eyes,
brows, nose, mouth, cheeks, bands across the face. The glitch starts in his eyes.

- Before the drop (00:00:10:08 = 10.27 s, --drop): the original edit, the blinds shot then the chalkboard (9.37 s,
  --second), the real frames, none of the cyberpsycho; now and then their real eyes echo outwards off the frame: 2-4 copies of an eye, different sizes, stepping out (left eye left, right eye right),
  overlapping, more often as the drop comes.
- From the drop: a hard cut between the two men on every half-beat of launch_music.wav (0.39 s beats, counted from
  the drop); in the last 40% every quarter-beat. The cyberpsycho step advances with time, 1 to 12.
- Aligned on the eyes: every cyberpsycho still is scaled and moved so his eyes sit exactly where they are in the real
  shot (aligned() in make_cyberpunk_closeups.py), so a rectangle cut from it lands on his face in place.
- Over his face: in each cut the rectangles start large (his whole face, half of it, the band across his eyes) and
  break into smaller ones over its frames; each cut is a bit crazier than the last (projects/cyberpunk/README.md,
  "Glitch collage"). His eyes echo outwards, each copy from a different cyberpsycho variation, and the
  cyberpsycho lines (plugins/cyberpsycho) start inside his eyes and shoot outward.
- Off his background: he is on his matte (make_opening_psycho_matte.py); behind him his own background has blocks of
  the other man's background and of the red cyberpsycho stills cut into it, more of them each cut.
- The last 40%: band slips, dropouts and a white flash frame on the beats as well.

Writes textAnimations/assets/collage/opening_psycho.mp4 at 1920x1080, 30 fps, already framed for the timeline (put it on
the track at 100%, no Motion). --start and --end are in seconds on the FilmCraft timeline (= the music's own time);
the default runs from the blinds shot (8.43 s) to cyberpunk (15.0 s)."""
import argparse
import os
import random
import subprocess
import sys

import cv2
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", "plugins", "cyberpsycho"))
import cyberpsycho  # noqa: E402

OP = os.path.join(ROOT, "projects", "opening")
OUT = os.path.join(HERE, "collage", "opening_psycho.mp4")
W, H, FPS = 1920, 1080, 30
IW, IH = 1672, 941  # the shots' own size; everything is built at this size, then framed
BEAT, GRID0 = 0.39, 11.0  # launch_music.wav: kick/snare every 0.39 s, on the grid through 11.0 s
CRAZY = 0.6
SHOTS = {
    # the real shot, its eyes in it (image pixels), its clip's Motion in launchIntro-v1 (anchor, position, scale %)
    "blinds": ("mattgen/Through the Blinds, Wired In Silence.png", ((705, 362), (945, 355)),
               ((836.0, 470.5), (735.0, 588.0), 149.0)),
    "chalk": ("mattgen/Intense Gaze Before the Chalkboard.png", ((715, 385), (925, 385)),
              ((836.0, 470.5), (1230.0, 540.0), 148.5)),
}
ORDER = ["blinds", "chalk"]
# the eyes in each cyberpsycho still at 1920x1080 (left, right), read off a grid
EYES = {
    "blinds": [((802, 420), (1110, 412)), ((787, 405), (1087, 405)), ((810, 262), (1042, 255)),
               ((832, 255), (1080, 247)), ((780, 255), (1042, 255)), ((825, 255), (1042, 247)),
               ((817, 255), (1065, 247)), ((810, 262), (1042, 255)), ((810, 262), (1035, 262)),
               ((817, 270), (1057, 255)), ((810, 262), (1050, 262)), ((832, 270), (1057, 270))],
    "chalk": [((795, 450), (1057, 442)), ((787, 435), (1042, 435)), ((780, 382), (1057, 382)),
              ((825, 382), (1110, 382)), ((825, 382), (1110, 382)), ((825, 382), (1095, 382)),
              ((817, 382), (1095, 382)), ((840, 382), (1095, 382)), ((817, 382), (1095, 382)),
              ((817, 390), (1095, 390)), ((817, 390), (1102, 390)), ((817, 390), (1095, 390))],
}

ap = argparse.ArgumentParser()
ap.add_argument("--start", type=float, default=253 / 30)
ap.add_argument("--end", type=float, default=450 / 30)
ap.add_argument("--drop", type=float, default=308 / 30, help="where the beat drops (timeline seconds; 00:00:10:08)")
ap.add_argument("--second", type=float, default=281 / 30, help="where the chalkboard shot starts in the original edit")
ap.add_argument("--after", default="speakers", choices=["speakers", "glitch"],
                help="after the drop: the real Sam / Dario clips zooming in, glitched at each peak (speakers), or the "
                     "two cyberpsycho stills alternating with the glitch blocks (glitch, the earlier cut)")
ap.add_argument("--flash", type=int, default=0, help="white frames at each switch after the drop (0: the "
                "thermogram in EffectCraft, plugins/openingThermal.jsx, does the switch)")
ap.add_argument("--out", default=OUT)
ap.add_argument("--frames", help="comma-separated frame numbers: write just these as PNGs to --png-dir, no video")
ap.add_argument("--png-dir", default=os.path.join(ROOT, "renders", "opening_psycho_frames"))
a = ap.parse_args()


def mid(e):
    (x1, y1), (x2, y2) = e
    return (x1 + x2) / 2, (y1 + y2) / 2, float(np.hypot(x2 - x1, y2 - y1))


base, stills, face, frame_m = {}, {}, {}, {}
for s, (path, eyes, (anc, pos, sc)) in SHOTS.items():
    base[s] = np.asarray(Image.open(os.path.join(OP, path)).convert("RGB").resize((IW, IH)))
    tx, ty, td = mid(eyes)
    face[s] = (tx, ty, td)
    k = sc / 100
    frame_m[s] = np.float32([[k, 0, pos[0] - k * anc[0]], [0, k, pos[1] - k * anc[1]]])
    stills[s] = []
    for i in range(12):
        im = np.asarray(Image.open(os.path.join(OP, "psycho", s, "%s_%02d.png" % (s, i))).convert("RGB")
                        .resize((IW, IH), Image.LANCZOS))
        (x1, y1), (x2, y2) = EYES[s][i]
        mx, my, d = mid(((x1 * IW / W, y1 * IH / H), (x2 * IW / W, y2 * IH / H)))
        kk = td / d
        m = np.float32([[kk, 0, tx - kk * mx], [0, kk, ty - kk * my]])
        stills[s].append(cv2.warpAffine(im, m, (IW, IH), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REPLICATE))


def parts(s):
    """the parts of his face, as (centre x, centre y, w, h) in image pixels, from his eyes"""
    x, y, d = face[s]
    return {
        "face": (x, y + 0.35 * d, 1.9 * d, 2.3 * d),
        "left half": (x - 0.45 * d, y + 0.35 * d, 0.95 * d, 2.2 * d),
        "right half": (x + 0.45 * d, y + 0.35 * d, 0.95 * d, 2.2 * d),
        "eye band": (x, y, 1.75 * d, 0.42 * d),
        "eye left": (x - d / 2, y, 0.5 * d, 0.3 * d),
        "eye right": (x + d / 2, y, 0.5 * d, 0.3 * d),
        "brows": (x, y - 0.27 * d, 1.6 * d, 0.26 * d),
        "forehead": (x, y - 0.6 * d, 1.3 * d, 0.4 * d),
        "nose": (x, y + 0.42 * d, 0.48 * d, 0.55 * d),
        "mouth": (x, y + 0.9 * d, 0.95 * d, 0.45 * d),
        "cheek left": (x - 0.6 * d, y + 0.55 * d, 0.5 * d, 0.6 * d),
        "cheek right": (x + 0.6 * d, y + 0.55 * d, 0.5 * d, 0.6 * d),
        "jaw": (x, y + 1.25 * d, 1.4 * d, 0.4 * d),
    }


BIG = ["face", "left half", "right half", "eye band", "mouth", "forehead"]
SMALL = ["eye left", "eye right", "brows", "nose", "mouth", "cheek left", "cheek right", "jaw", "eye band"]
rnd = random.Random("opening psycho faces")


def split(patch, k):
    patch = patch.copy()
    patch[:, :, 0] = np.roll(patch[:, :, 0], k, axis=1)
    patch[:, :, 2] = np.roll(patch[:, :, 2], -k, axis=1)
    return patch


def paste(img, patch, x, y):
    x0, y0 = max(x, 0), max(y, 0)
    x1, y1 = min(x + patch.shape[1], img.shape[1]), min(y + patch.shape[0], img.shape[0])
    if x1 > x0 and y1 > y0:
        img[y0:y1, x0:x1] = patch[y0 - y:y1 - y, x0 - x:x1 - x]


def rect(s, step, within, heat):
    """a rectangle over part of his face, cut from a cyberpsycho still and pasted in place.
    within: 0 at the start of a cut (large pieces) to 1 at its end (small); heat: 0 calm to 1 crazy"""
    name = rnd.choice(BIG if rnd.random() > within * 0.85 + heat * 0.3 else SMALL)
    cx, cy, pw, ph = parts(s)[name]
    f = rnd.uniform(0.75, 1.25) * (1.0 - 0.55 * within) * (1.0 - 0.35 * heat)  # larger into smaller
    w, h = max(12, int(pw * f)), max(10, int(ph * f))
    cx += rnd.uniform(-0.5, 0.5) * (pw - w if pw > w else pw * 0.2)
    cy += rnd.uniform(-0.5, 0.5) * (ph - h if ph > h else ph * 0.2)
    x, y = int(cx - w / 2), int(cy - h / 2)
    x, y = min(max(x, 0), IW - w), min(max(y, 0), IH - h)
    src = stills[s][min(11, step + rnd.choice([0, 0, 1, 2]))]
    patch = src[y:y + h, x:x + w]
    if rnd.random() < 0.25 + 0.5 * heat:
        patch = split(patch, rnd.randint(2, 4 + int(14 * heat)))
    dx = int(rnd.choice([0, 0, 1]) * rnd.uniform(-1, 1) * face[s][2] * (0.05 + 0.35 * heat))
    return patch, x + dx, y


def eye_patch(s, step):
    cx, cy, ew, eh = parts(s)[rnd.choice(["eye left", "eye right"])]
    src = stills[s][min(11, step + rnd.randint(1, 3))]
    crop = src[int(cy - eh / 2):int(cy + eh / 2), int(cx - ew / 2):int(cx + ew / 2)]
    k = rnd.uniform(1.2, 1.8)
    patch = cv2.resize(crop, (int(crop.shape[1] * k), int(crop.shape[0] * k)), interpolation=cv2.INTER_LANCZOS4)
    if rnd.random() < 0.6:
        patch = split(patch, rnd.randint(3, 8))
    return patch, int(cx - patch.shape[1] / 2 + rnd.uniform(-8, 8)), int(cy - patch.shape[0] / 2 + rnd.uniform(-5, 5))


eye_matte = {}
for s in SHOTS:
    m = np.zeros((IH, IW), np.uint8)
    for nm in ("eye left", "eye right"):
        cx, cy, ew, eh = parts(s)[nm]
        cv2.ellipse(m, (int(cx), int(cy)), (int(ew / 2), int(eh / 2)), 0, 0, 360, 255, -1)
    eye_matte[s] = cv2.warpAffine(m, frame_m[s], (W, H))

matte = {s: cv2.imread(os.path.join(OP, "psycho", "%s_matte.png" % s), cv2.IMREAD_GRAYSCALE).astype(np.float32)[:, :, None]
         / 255 for s in SHOTS}

n = int(round((a.end - a.start) * FPS))
fd = int(round((a.drop - a.start) * FPS))  # the frame the beat drops on
beats = {int(round((a.drop + k * BEAT - a.start) * FPS)) for k in range(0, 40)}  # the beats, from the drop


def twitch_map(s, events):
    """his own eyes, liquified in place: each event (which eye, sx, sy, dx, dy) squeezes or stretches that eye and
    nudges it, fading out round it, so nothing is doubled; returns the remap grids for the whole frame"""
    x, y, d = face[s]
    yy, xx = np.mgrid[0:IH, 0:IW].astype(np.float32)
    mx, my = xx.copy(), yy.copy()
    for eye, sx, sy, dx, dy in events:
        cx, cy, ew, eh = parts(s)[eye]
        rx, ry = ew * 0.95, eh * 1.25
        r = np.sqrt(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2)
        w = np.clip(1 - r, 0, 1) ** 1.5
        w = w * w * (3 - 2 * w)
        mx -= w * ((xx - cx) * (1 - 1 / sx) + dx)
        my -= w * ((yy - cy) * (1 - 1 / sy) + dy)
    return mx, my


def twitch_events(s, f):
    """quick little twitches, more of them nearer the drop; each one held 1-2 frames"""
    r = random.Random("twitch %s %d" % (s, f // 2 if f % 4 < 2 else f))
    if r.random() > 0.3 + 0.6 * f / max(fd, 1):
        return []
    d = face[s][2]
    eyes = r.choice([["eye left", "eye right"], ["eye left", "eye right"], ["eye left"], ["eye right"]])
    sy = r.choice([r.uniform(0.55, 0.8), r.uniform(1.15, 1.35)])  # squeeze shut or stretch wide
    sx = r.uniform(0.9, 1.15) if sy < 1 else r.uniform(0.85, 1.0)
    dx, dy = r.uniform(-0.07, 0.07) * d, r.uniform(-0.1, 0.02) * d  # a little up, left or right
    return [(e, sx, sy, dx * r.uniform(0.7, 1.0), dy) for e in eyes]


def eye_echoes(img, s, f, sources, chance):
    """his eyes breaking out sideways: 2-4 copies of an eye, each cut from one of `sources` (aligned frames: the base
    shot before the drop, the cyberpsycho variations after it), each a different size, stepping outwards (the left
    eye's to the left, the right eye's to the right), overlapping like stacked frames. On `chance` of frames, held 2."""
    r = random.Random("echo %s %d" % (s, f // 2))
    if r.random() > chance:
        return img
    img = img.copy()
    d = face[s][2]
    for eye, side in r.choice([[("eye left", -1), ("eye right", 1)], [("eye left", -1)], [("eye right", 1)]]):
        cx, cy, ew, eh = parts(s)[eye]
        ew, eh = ew * 1.25, eh * 1.35
        copies = r.randint(2, 4)
        reach = 0.0
        for i in range(1, copies + 1):
            src = r.choice(sources)
            crop = src[int(cy - eh / 2):int(cy + eh / 2), int(cx - ew / 2):int(cx + ew / 2)]
            k = r.uniform(0.7, 1.7)
            pw, ph = max(4, int(crop.shape[1] * k)), max(4, int(crop.shape[0] * k))
            patch = cv2.resize(crop, (pw, ph), interpolation=cv2.INTER_LINEAR)
            reach += r.uniform(0.22, 0.42) * d * (0.6 + 0.4 * k)
            x = int(cx + side * reach - pw / 2)
            y = int(cy + r.uniform(-0.08, 0.05) * d - ph / 2)
            al = np.zeros((ph, pw), np.float32)
            cv2.ellipse(al, (pw // 2, ph // 2), (int(pw * 0.46), int(ph * 0.44)), 0, 0, 360, 1.0, -1)
            al = cv2.GaussianBlur(al, (0, 0), max(1.0, min(pw, ph) * 0.08))[:, :, None]
            x0, y0, x1, y1 = max(x, 0), max(y, 0), min(x + pw, IW), min(y + ph, IH)
            if x1 <= x0 or y1 <= y0:
                continue
            pa = al[y0 - y:y1 - y, x0 - x:x1 - x]
            img[y0:y1, x0:x1] = (img[y0:y1, x0:x1] * (1 - pa) + patch[y0 - y:y1 - y, x0 - x:x1 - x] * pa).astype(np.uint8)
    return img


def bg_block(s, other, step, q):
    """a block of another background, pasted in place behind him"""
    pool = [base[other], base[other], stills[s][step], stills[other][step], stills[s][min(11, step + 2)]]
    src = rnd.choice(pool)
    if rnd.random() < 0.35:  # a long strip
        w, h = int(IW * rnd.uniform(0.4, 1.0)), int(IH * rnd.uniform(0.04, 0.14))
    else:
        w, h = int(IW * rnd.uniform(0.15, 0.55)), int(IH * rnd.uniform(0.12, 0.6))
    x, y = rnd.randrange(0, IW - w + 1), rnd.randrange(0, IH - h + 1)
    patch = src[y:y + h, x:x + w]
    if rnd.random() < 0.3 + 0.4 * q:
        patch = split(patch, rnd.randint(4, 6 + int(16 * q)))
    dx = int(rnd.choice([0, 0, 1]) * rnd.uniform(-0.08, 0.08) * IW * (0.3 + q))
    return patch, x + dx, y


# --- the speakers: real footage of the two men talking (matt's picks, projects/opening/ref/speakers/), one per man:
# the blinds man is Sam, the chalkboard man Dario. Each: the file and its stretches of him talking in one take, with
# his eyes (left, right; source pixels) marked on the stretch's first frame; the face is followed from there by
# template matching on the eyes.
SPK = os.path.join(ROOT, "projects", "opening", "ref", "speakers")
SPEAKERS = {
    "blinds": ("sam_old_2.mp4", [(85.0, 100.0, (299, 171), (350, 173))]),      # young Sam, handheld, with a mic
    "chalk": ("dario_young_1.mp4", [(18.0, 26.0, (477, 187), (559, 183)),    # young Dario at a mic, on VHS
                                   (38.0, 44.0, (517, 210), (600, 210))]),
}


class Speaker:
    """his talking frames, in order across the stretches, each with his eyes tracked"""
    def __init__(self, path, stretches):
        self.frames, self.eyes, self.at = [], [], 0
        for t0, t1, el, er in stretches:
            cap = cv2.VideoCapture(os.path.join(SPK, path))
            fps = cap.get(cv2.CAP_PROP_FPS)
            cap.set(cv2.CAP_PROP_POS_FRAMES, int(round(t0 * fps)))
            raw = []
            for _ in range(int(round((t1 - t0) * fps))):
                ok, fr = cap.read()
                if not ok:
                    break
                raw.append(cv2.cvtColor(fr, cv2.COLOR_BGR2RGB))
            step = fps / FPS  # his frames at 30 fps, whatever the file's rate
            picks = [raw[int(i * step)] for i in range(int(len(raw) / step))]
            (lx, ly), (rx, ry) = el, er
            d = float(np.hypot(rx - lx, ry - ly))
            mx, my = (lx + rx) / 2, (ly + ry) / 2
            tw, th = int(2.6 * d), int(1.3 * d)
            g0 = cv2.cvtColor(picks[0], cv2.COLOR_RGB2GRAY)
            tpl = g0[int(my - th / 2):int(my + th / 2), int(mx - tw / 2):int(mx + tw / 2)]
            track, cx, cy = [], mx, my
            for fr in picks:
                g = cv2.cvtColor(fr, cv2.COLOR_RGB2GRAY)
                r = int(0.7 * d)
                x0, y0 = int(max(cx - tw / 2 - r, 0)), int(max(cy - th / 2 - r, 0))
                win = g[y0:int(min(cy + th / 2 + r, g.shape[0])), x0:int(min(cx + tw / 2 + r, g.shape[1]))]
                if win.shape[0] > tpl.shape[0] and win.shape[1] > tpl.shape[1]:
                    _, _, _, (bx, by) = cv2.minMaxLoc(cv2.matchTemplate(win, tpl, cv2.TM_CCOEFF_NORMED))
                    cx, cy = x0 + bx + tw / 2, y0 + by + th / 2
                track.append((cx, cy))
            tr = np.array(track)
            sm = np.array([tr[max(0, i - 5):i + 6].mean(axis=0) for i in range(len(tr))])  # a little smoothing
            for fr, (cx, cy) in zip(picks, sm):
                self.frames.append(fr)
                self.eyes.append(((cx - (mx - lx), cy - (my - ly)), (cx + (rx - mx), cy + (ry - my))))

    def take(self):
        """his next frame and its eyes; he keeps talking from where his last shot left off"""
        i = self.at % len(self.frames)
        self.at += 1
        return self.frames[i], self.eyes[i]


def zoom_crop(fr, eyes, z):
    """a 16:9 crop round his face, z 0 (wide) to 1 (tight on his face), scaled to the frame; returns it and his eyes
    in the output frame"""
    (lx, ly), (rx, ry) = eyes
    d = float(np.hypot(rx - lx, ry - ly))
    sh, sw = fr.shape[:2]
    cw0 = min(sw, sh * 16 / 9, 8.0 * d)
    cw = cw0 + (3.0 * d - cw0) * z
    ch = cw * 9 / 16
    cx, cy = (lx + rx) / 2, (ly + ry) / 2 + 0.35 * d
    x0 = min(max(cx - cw / 2, 0), sw - cw)
    y0 = min(max(cy - ch / 2, 0), sh - ch)
    k = W / cw
    m = np.float32([[k, 0, -x0 * k], [0, k, -y0 * k]])
    out = cv2.warpAffine(fr, m, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return out, (((lx - x0) * k, (ly - y0) * k), ((rx - x0) * k, (ry - y0) * k))


def out_parts(eyes):
    """the parts of his face in the output frame, from his eyes there"""
    (lx, ly), (rx, ry) = eyes
    x, y, d = (lx + rx) / 2, (ly + ry) / 2, float(np.hypot(rx - lx, ry - ly))
    return {"face": (x, y + 0.35 * d, 1.9 * d, 2.3 * d), "left half": (x - 0.45 * d, y + 0.35 * d, 0.95 * d, 2.2 * d),
            "right half": (x + 0.45 * d, y + 0.35 * d, 0.95 * d, 2.2 * d), "eye band": (x, y, 1.75 * d, 0.42 * d),
            "eye left": (lx, ly, 0.5 * d, 0.3 * d), "eye right": (rx, ry, 0.5 * d, 0.3 * d),
            "brows": (x, y - 0.27 * d, 1.6 * d, 0.26 * d), "forehead": (x, y - 0.6 * d, 1.3 * d, 0.4 * d),
            "nose": (x, y + 0.42 * d, 0.48 * d, 0.55 * d), "mouth": (x, y + 0.9 * d, 0.95 * d, 0.45 * d),
            "cheek left": (x - 0.6 * d, y + 0.55 * d, 0.5 * d, 0.6 * d),
            "cheek right": (x + 0.6 * d, y + 0.55 * d, 0.5 * d, 0.6 * d), "jaw": (x, y + 1.25 * d, 1.4 * d, 0.4 * d)}, d


# his own cyberpsycho steps, made from his clip (images/gen/make_opening_psycho_speakers.py):
# projects/opening/psycho/<who>/<who>_00-11.png, with his eyes in each (left, right; 1920x1080), read off a grid
SPK_WHO = {"blinds": "sam", "chalk": "dario"}
SPK_EYES = {
    "sam": [((760, 380), (1060, 360)), ((680, 400), (1040, 380)), ((800, 440), (1120, 400)), ((860, 280), (1100, 260)),
            ((820, 300), (1040, 300)), ((800, 220), (1020, 220)), ((800, 260), (1020, 260)), ((800, 220), (1000, 220)),
            ((800, 280), (1020, 280)), ((880, 420), (1060, 420)), ((800, 260), (1000, 260)), ((800, 300), (980, 300))],
    "dario": [((780, 360), (960, 340)), ((800, 300), (1020, 300)), ((680, 340), (880, 320)), ((1000, 280), (1240, 280)),
              ((860, 220), (1080, 220)), ((860, 260), (1080, 260)), ((680, 240), (880, 220)), ((960, 240), (1160, 220)),
              ((780, 360), (1080, 360)), ((800, 400), (980, 380)), ((760, 240), (920, 240)), ((960, 200), (1120, 200))],
}
_spk_stills = {}


def spk_still(who, k):
    if (who, k) not in _spk_stills:
        _spk_stills[(who, k)] = np.asarray(Image.open(os.path.join(ROOT, "projects", "opening", "psycho", who,
                                                                   "%s_%02d.png" % (who, k))).convert("RGB"))
    return _spk_stills[(who, k)]


def onto_spk(s, k, eyes):
    """his own cyberpsycho step k, warped so its eyes land on his real eyes in the output frame"""
    who = SPK_WHO[s]
    (a1, b1), (a2, b2) = SPK_EYES[who][k]
    (lx, ly), (rx, ry) = eyes
    src = np.float32([[a1, b1], [a2, b2], [(a1 + a2) / 2 - (b2 - b1), (b1 + b2) / 2 + (a2 - a1)]])
    dst = np.float32([[lx, ly], [rx, ry], [(lx + rx) / 2 - (ry - ly), (ly + ry) / 2 + (rx - lx)]])
    return cv2.warpAffine(spk_still(who, k), cv2.getAffineTransform(src, dst), (W, H), flags=cv2.INTER_LINEAR,
                          borderMode=cv2.BORDER_REPLICATE)


def onto(s, k, eyes):
    """cyberpsycho still k of shot s, warped so its eyes land on his real eyes in the output frame"""
    fx, fy, fd = face[s]
    (lx, ly), (rx, ry) = eyes
    src = np.float32([[fx - fd / 2, fy], [fx + fd / 2, fy], [fx, fy + fd]])
    nx, ny = -(ry - ly), (rx - lx)  # down his face, square to the eye line
    dst = np.float32([[lx, ly], [rx, ry], [(lx + rx) / 2 + nx, (ly + ry) / 2 + ny]])
    return cv2.warpAffine(stills[s][k], cv2.getAffineTransform(src, dst), (W, H), flags=cv2.INTER_LINEAR,
                          borderMode=cv2.BORDER_REPLICATE)


def peak_glitch(out, s, step, eyes, within, heat):
    """the frames at the peak of his zoom: the cyberpsycho glitch on his real face (rectangles of his own cyberpsycho
    steps, made from his clip, over
    his face parts, his eyes echoing outwards, band slips, the lines out of his eyes); within: 0-1 through the peak,
    heat: 0-1 through the cut"""
    pp, d = out_parts(eyes)
    srcs = [onto_spk(s, step, eyes), onto_spk(s, min(11, step + 2), eyes)]
    out = out.copy()
    for _ in range(4 + int(10 * heat)):
        name = rnd.choice(BIG if rnd.random() > within * 0.8 + heat * 0.3 else SMALL)
        cx, cy, pw, ph = pp[name]
        f = rnd.uniform(0.75, 1.25) * (1.0 - 0.5 * within) * (1.0 - 0.3 * heat)
        w, h = max(12, min(W, int(pw * f))), max(10, min(H, int(ph * f)))
        cx += rnd.uniform(-0.5, 0.5) * max(pw - w, pw * 0.2)
        cy += rnd.uniform(-0.5, 0.5) * max(ph - h, ph * 0.2)
        x, y = int(min(max(cx - w / 2, 0), W - w)), int(min(max(cy - h / 2, 0), H - h))
        patch = rnd.choice(srcs)[y:y + h, x:x + w]
        if rnd.random() < 0.35 + 0.5 * heat:
            patch = split(patch, rnd.randint(4, 8 + int(20 * heat)))
        paste(out, patch, x + int(rnd.choice([0, 0, 1]) * rnd.uniform(-1, 1) * d * (0.05 + 0.3 * heat)), y)
    for eye, side in (("eye left", -1), ("eye right", 1)):  # his eyes echoing outwards, from the variations
        cx, cy, ew, eh = pp[eye]
        ew, eh, reach = ew * 1.25, eh * 1.35, 0.0
        for _ in range(rnd.randint(1, 2 + int(2 * heat))):
            src = rnd.choice(srcs)
            crop = src[int(max(cy - eh / 2, 0)):int(max(cy + eh / 2, 1)), int(max(cx - ew / 2, 0)):int(max(cx + ew / 2, 1))]
            if crop.size == 0:
                continue
            kk = rnd.uniform(0.7, 1.7)
            patch = cv2.resize(crop, (max(4, int(crop.shape[1] * kk)), max(4, int(crop.shape[0] * kk))))
            reach += rnd.uniform(0.22, 0.42) * d * (0.6 + 0.4 * kk)
            paste(out, patch, int(cx + side * reach - patch.shape[1] / 2), int(cy - patch.shape[0] / 2))
    for _ in range(rnd.randint(1, 2 + int(4 * heat))):  # band slips
        y0, bh = rnd.randrange(H), rnd.randint(6, 70)
        out[y0:y0 + bh] = np.roll(out[y0:y0 + bh], int(rnd.uniform(-160, 160) * (0.3 + heat)), axis=1)
    m = np.zeros((H, W), np.uint8)  # the cyberpsycho lines, out of his eyes
    for eye in ("eye left", "eye right"):
        cx, cy, ew, eh = pp[eye]
        cv2.ellipse(m, (int(cx), int(cy)), (max(1, int(ew / 2)), max(1, int(eh / 2))), 0, 0, 360, 255, -1)
    if m.any():
        lines = cyberpsycho.frame("speaker %d %.2f" % (step, within), (W, H), m, (245, 245, 245), 0.6 + 0.8 * heat,
                                  outline=(20, 0, 0), outline_px=2)
        if heat > 0.5:
            lines = cyberpsycho.glitch(lines, int(within * 10) + step, heat)
        al = lines[:, :, 3:4].astype(np.float32) / 255
        out = (out * (1 - al) + lines[:, :, :3] * al).astype(np.uint8)
    return out


# the cuts after the drop: speakers, a shot on every beat (every half-beat in the crazy part); glitch, the half-beat (the quarter-beat in the crazy part)
cuts, last = [fd], None
for f in range(fd, n):
    q = (f - fd) / max(n - 1 - fd, 1)
    unit = BEAT / ((2 if q >= CRAZY else 1) if a.after == "speakers" else (4 if q >= CRAZY else 2))
    t = a.start + f / FPS
    c = (round(np.floor((t - a.drop) / unit + 1e-6)), unit)  # on the beat, counted from the drop
    if last is not None and c != last:
        cuts.append(f)
    last = c
cuts.append(n)

want = None if a.frames is None else {int(v) for v in a.frames.split(",")}
if want is None:
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s",
                          "%dx%d" % (W, H), "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "14", "-pix_fmt",
                          "yuv420p", a.out], stdin=subprocess.PIPE)
else:
    os.makedirs(a.png_dir, exist_ok=True)


def emit(out, f):
    if want is None:
        p.stdin.write(np.ascontiguousarray(out).tobytes())
    elif f in want:
        Image.fromarray(out).save(os.path.join(a.png_dir, "frame_%03d.png" % f))


# before the drop: the original edit (blinds, then the chalkboard), the real frames, their real eyes now and then
# echoing outwards off the base frame; none of the cyberpsycho variations
f2 = int(round((a.second - a.start) * FPS))
for f in range(fd):
    s = ORDER[0] if f < f2 else ORDER[1]
    img = eye_echoes(base[s], s, f, [base[s]], 0.15 + 0.45 * f / max(fd, 1))
    emit(cv2.warpAffine(img, frame_m[s], (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE), f)

def inside_cut(cuts):
    """the inside scene: the blinds and chalkboard men in their cyberpsycho stills, glitch-cut on the beat
    (cuts: the frames each cut starts on, then the end)"""
    # from the drop: the glitch cut, the two of them off their backgrounds, the backgrounds glitch-cut behind them
    for ci in range(len(cuts) - 1):
        s = ORDER[ci % 2]  # the drop cuts from the chalkboard back to the blinds, then alternates
        other = ORDER[(ci + 1) % 2]
        heat = ci / max(len(cuts) - 2, 1)  # each cut a bit crazier than the last
        stack, bstack = [], []
        length = cuts[ci + 1] - cuts[ci]
        for j in range(length):
            f = cuts[ci] + j
            q = (f - fd) / max(n - 1 - fd, 1)
            step = min(11, int(q * 12))
            within = j / max(length - 1, 1)
            # him: his real frame with the cyberpsycho face coming through in rectangles over his face
            img = base[s].copy()
            for _ in range(rnd.randint(1, 2 + int(4 * heat))):
                stack.append(rect(s, step, within, heat))
            stack = stack[-int(3 + 22 * heat):]
            for patch, x, y in stack:
                paste(img, patch, x, y)
            # his eyes echoing outwards, each copy from a different cyberpsycho variation
            img = eye_echoes(img, s, f, stills[s][:max(step + 3, 4)], 0.5 + 0.5 * heat)
            # behind him: his own background, other backgrounds cutting in
            bg = base[s].copy()
            if f % 2 == 0 or not bstack:
                for _ in range(rnd.randint(1, 2 + int(3 * heat))):
                    bstack.append(bg_block(s, other, step, q))
            bstack = bstack[-int(2 + 10 * heat):]
            for patch, x, y in bstack:
                paste(bg, patch, x, y)
            img = (bg * (1 - matte[s]) + img * matte[s]).astype(np.uint8)
            out = cv2.warpAffine(img, frame_m[s], (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
            if q >= CRAZY * 0.6:
                g = (q - CRAZY * 0.6) / (1 - CRAZY * 0.6)
                for _ in range(rnd.randint(0, int(1 + 5 * g))):  # band slips
                    y0, bh = rnd.randrange(H), rnd.randint(6, 70)
                    out[y0:y0 + bh] = np.roll(out[y0:y0 + bh], int(rnd.uniform(-160, 160) * g), axis=1)
                for _ in range(rnd.randint(0, int(4 * g))):  # dropouts
                    x0, y0 = rnd.randrange(W), rnd.randrange(H)
                    out[y0:y0 + rnd.randint(20, 160), x0:x0 + rnd.randint(40, 360)] = 0
            if want is not None and f not in want:
                continue  # stills only: skip drawing frames that aren't asked for
            lines = cyberpsycho.frame("opening psycho %d" % (f // 2), (W, H), eye_matte[s], (245, 245, 245),
                                      0.35 + 1.0 * q, outline=(20, 0, 0), outline_px=2)
            if q >= CRAZY:
                lines = cyberpsycho.glitch(lines, f // 2, q)
            al = lines[:, :, 3:4].astype(np.float32) / 255 * (0.55 + 0.45 * min(1.0, q / CRAZY))
            out = (out * (1 - al) + lines[:, :, :3] * al).astype(np.uint8)
            if q >= CRAZY and f in beats and f != cuts[0]:  # not on the switch: the thermogram is there
                out = np.full_like(out, 255)
            emit(out, f)


# from the drop, speakers (matt, 2026-11-15): young Sam talking (his clip, one push-in over his 4 beats, his own red
# cyberpsycho breaking through on its last frames, at the peak), a flash, young Dario the same, a flash back into the inside scene
# (the blinds and chalkboard men glitch-cut, as before) until cyberpunk takes over
FLASH, SPK_BEATS = a.flash, 4  # white frames at each switch; 0 when EffectCraft puts the thermogram there


def on_beat(k):
    return fd + int(round(k * BEAT * FPS))


def grid_cuts(f0, f1):
    """cut points from f0 to f1 on the grid counted from the drop (beat; half/quarter as the old cut did)"""
    out, last = [f0], None
    for f in range(f0, f1):
        q = (f - fd) / max(n - 1 - fd, 1)
        unit = BEAT / (4 if q >= CRAZY else 2)
        c = round(np.floor((a.start + f / FPS - a.drop) / unit + 1e-6))
        if last is not None and c != last:
            out.append(f)
        last = c
    return out + [f1]


def flash(f0):
    for f in range(f0, min(f0 + FLASH, n)):
        emit(np.full((H, W, 3), 255, np.uint8), f)
    return min(f0 + FLASH, n)


if a.after == "speakers":
    spk = {s: Speaker(*SPEAKERS[s]) for s in ORDER}
    shots_total, shot_no = 2, 0
    f = fd
    for part, s in enumerate(ORDER):  # Sam (the blinds man), then Dario (the chalkboard man)
        f = flash(f)
        end = on_beat(SPK_BEATS * (part + 1))
        cuts_s = [f, end]  # one shot each: one continuous push-in (matt: not a punch-in every beat)
        for ci in range(len(cuts_s) - 1):
            heat = shot_no / max(shots_total - 1, 1)
            shot_no += 1
            length = cuts_s[ci + 1] - cuts_s[ci]
            peak = 5  # the glitch: the last frames, at the peak of the zoom
            for j in range(length):
                ff = cuts_s[ci] + j
                step = int(round(8 + 3 * heat))  # well into his cyberpsycho: step 8 for Sam, 11 for Dario
                fr, eyes = spk[s].take()
                z = (j / max(length - 1, 1)) ** 2.2  # into the peak, faster and faster
                out, oeyes = zoom_crop(fr, eyes, z)
                if j >= length - peak and (want is None or ff in want):
                    out = peak_glitch(out, s, step, oeyes, (j - (length - peak)) / max(peak - 1, 1), heat)
                emit(out, ff)
        f = end
    f = flash(f)
    if f < n:
        inside_cut(grid_cuts(f, n))
else:
    inside_cut(cuts)
if want is None:
    p.stdin.close()
    p.wait()
print(n, "frames, the drop at frame", fd, ",", len(cuts) - 1, "cuts,", a.start, "-", a.end, "s ->", a.out)
