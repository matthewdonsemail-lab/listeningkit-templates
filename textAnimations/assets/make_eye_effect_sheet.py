"""The outward eye effect, isolated, across every scene that uses it (matt, 2026-11-16), for the process board:
  reference   what it's based on: the red sun_ae TikTok (projects/opening/ref/sun_ae), frames 177-224, the faces
              echoing outwards
  then one row per scene, each the same four steps:
    the shot | its eyes found (boxes) | the eye echoes alone, on black | the effect on the shot
  scenes: the opener's two men (projects/opening/psycho/blinds, chalk; eyes from make_opening_psycho_cut.py), the
  busts going into the outro (projects/cyberpunk/outro/portrait_N + styles; eyes from make_bust_lines.py), the girl's
  flash cuts in the ending (make_ending_girl_inserts.py's shots and eyes)
The echoes are drawn the way those scripts draw them: copies of each eye taken from the shot's other versions, scaled
0.6-1.9x, stepping outwards (left eye left, right eye right), 2-6 per side.
Writes textAnimations/assets/collage/process/eye_effect.jpg
  python textAnimations/assets/make_eye_effect_sheet.py"""
import glob
import importlib.util
import os
import random

import cv2
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(HERE, "collage", "process")
W, H = 1920, 1080


def cover(path, k=1.0):
    im = cv2.imread(path)
    s = max(W / im.shape[1], H / im.shape[0]) * k
    im = cv2.resize(im, (int(im.shape[1] * s), int(im.shape[0] * s)), interpolation=cv2.INTER_AREA)
    y0, x0 = (im.shape[0] - H) // 2, (im.shape[1] - W) // 2
    return im[y0:y0 + H, x0:x0 + W]


def echoes(eyes, versions, rnd):
    """the echo layer alone (BGR + mask): eyes copied outwards from the versions"""
    (lx, ly), (rx, ry) = eyes
    d = max(60.0, float(np.hypot(rx - lx, ry - ly)))
    lay = np.zeros((H, W, 3), np.uint8); m = np.zeros((H, W), np.uint8)
    for (ex, ey), side in (((lx, ly), -1), ((rx, ry), 1)):
        ew, eh = d * 0.55, d * 0.32
        reach = 0.0
        for _ in range(rnd.randint(3, 6)):
            src = rnd.choice(versions)
            crop = src[int(max(ey - eh / 2, 0)):int(ey + eh / 2), int(max(ex - ew / 2, 0)):int(ex + ew / 2)]
            if crop.size == 0:
                continue
            k = rnd.uniform(0.6, 1.9)
            p = cv2.resize(crop, (max(4, int(crop.shape[1] * k)), max(4, int(crop.shape[0] * k))))
            reach += d * rnd.uniform(0.3, 0.55)
            x, y = int(ex + side * reach - p.shape[1] / 2), int(ey - p.shape[0] / 2)
            x0, y0, x1, y1 = max(x, 0), max(y, 0), min(x + p.shape[1], W), min(y + p.shape[0], H)
            if x1 > x0 and y1 > y0:
                lay[y0:y1, x0:x1] = p[y0 - y:y1 - y, x0 - x:x1 - x]; m[y0:y1, x0:x1] = 255
    return lay, m


def marked(img, eyes):
    out = img.copy()
    (lx, ly), (rx, ry) = eyes
    d = max(60.0, float(np.hypot(rx - lx, ry - ly)))
    for ex, ey in eyes:
        cv2.rectangle(out, (int(ex - d * .28), int(ey - d * .17)), (int(ex + d * .28), int(ey + d * .17)), (0, 255, 255), 4)
    return out


rows = []
# the opener's two men: their 12 cyberpsycho stills
spec = importlib.util.spec_from_file_location("x", os.path.join(HERE, "make_opening_psycho_cut.py"))
src = open(os.path.join(HERE, "make_opening_psycho_cut.py"), encoding="utf8").read()
EYES_OP = eval(src[src.index("EYES = {") + 7:src.index("}", src.index("EYES = {")) + 1])
for man, step in (("blinds", 6), ("chalk", 8)):
    vers = [cover(p) for p in sorted(glob.glob(os.path.join(REPO, "projects", "opening", "psycho", man, "*.png")))]
    rows.append(("The opener, %s" % ("the man at the blinds" if man == "blinds" else "the man at the chalkboard"), vers[step], EYES_OP[man][step], vers))
# the busts
bsrc = open(os.path.join(HERE, "make_bust_lines.py"), encoding="utf8").read()
EYES_B = eval(bsrc[bsrc.index("EYES = [") + 7:bsrc.index("]]", bsrc.index("EYES = [")) + 2] if "]]" in bsrc[bsrc.index("EYES = ["):bsrc.index("EYES = [") + 600] else bsrc[bsrc.index("EYES = [") + 7:bsrc.index("\n# each bust", bsrc.index("EYES = ["))].strip())
OUTRO = os.path.join(REPO, "projects", "cyberpunk", "outro")
for i in (1, 3):
    vers = [cover(os.path.join(OUTRO, "portrait_%d.png" % i), 1.08)]
    vers += [cover(p, 1.08) for p in sorted(glob.glob(os.path.join(OUTRO, "styles", "portrait_%d_*.png" % i)))]
    rows.append(("The busts, going into the outro (bust %d)" % (i + 1), vers[0], EYES_B[i], vers))
# the girl
gsrc = open(os.path.join(HERE, "make_ending_girl_inserts.py"), encoding="utf8").read()
SHOTS = eval(gsrc[gsrc.index("SHOTS = [") + 8:gsrc.index("]\n", gsrc.index("SHOTS = [")) + 1])
EYES_G = eval(gsrc[gsrc.index("EYES = [") + 7:gsrc.index("]\n", gsrc.index("EYES = [")) + 1])
CP = os.path.join(REPO, "projects", "cyberpunk")


def frame_of(path, cx, cy, z):
    im = cv2.imread(os.path.join(CP, path)); h, w = im.shape[:2]
    k = max(W / w, H / h) * z
    im = cv2.resize(im, (int(w * k), int(h * k))); h, w = im.shape[:2]
    x0 = int(min(max(cx * w - W / 2, 0), w - W)); y0 = int(min(max(cy * h - H / 2, 0), h - H))
    return im[y0:y0 + H, x0:x0 + W]


framed = [frame_of(*s) for s in SHOTS]
for gi in (0, 5, 4):
    eyes = tuple((x * W, y * H) for x, y in EYES_G[gi])
    rows.append(("The girl, flash cuts in the ending (%s)" % SHOTS[gi][0].split("/")[-1][:-4], framed[gi], eyes,
                 [framed[gi]]))

# the same moment in the final film, with the CRT and everything over it (renders/launch_film_final_full.mp4 frames)
FINAL = [324, 366, 975, 1039, 1161, 1268, 1248]
cap = cv2.VideoCapture(os.path.join(HERE, "..", "renders", "launch_film_final_full.mp4"))


def film(n):
    cap.set(1, n); ok, f = cap.read()
    return f if ok else np.zeros((H, W, 3), np.uint8)


TW, TH, LAB = 480, 270, 34
heads = ["the shot", "its eyes found", "the eye echoes alone", "on the shot", "in the film, with the CRT"]
sheet = Image.new("RGB", (5 * TW, (len(rows) + 1) * (TH + LAB) + LAB), (14, 14, 16))
d = ImageDraw.Draw(sheet)
# the reference row
def ref_frame(n):
    im = Image.open(os.path.join(REPO, "references", "cyberpsycho", "ref%d.png" % n)).convert("RGB")
    h = im.width * 9 // 16; y0 = (im.height - h) // 2          # the video in the middle of the phone screenshot
    return im.crop((0, y0, im.width, y0 + h))


TT = os.path.join(REPO, "projects", "opening", "ref", "tt_elements", "assets")
def sun_ae(n):
    cap = cv2.VideoCapture(os.path.join(REPO, "projects", "opening", "ref", "sun_ae", "tiktok_7658403141708172558.mp4"))
    cap.set(1, n - 1); ok, f = cap.read()
    return Image.fromarray(cv2.cvtColor(f, cv2.COLOR_BGR2RGB))


# what it's based on: the red sun_ae TikTok, frames 177-224 (matt's pick), the faces echoing outwards
refs = [sun_ae(n) for n in (185, 188, 193, 195)]
d.text((6, 6), "WHAT IT IS BASED ON: the red sun_ae TikTok, frames 185, 188, 193, 195 (from 177-224)", fill=(255, 220, 0))
for c, p in enumerate(refs):
    im = p.convert("RGB").resize((TW, TH)); sheet.paste(im, (c * TW, LAB))
for r, (lab, base, eyes, vers) in enumerate(rows):
    y = (r + 1) * (TH + LAB) + LAB
    d.text((6, y - LAB + 8), lab.upper(), fill=(255, 220, 0))
    rnd = random.Random("eye sheet %d" % r)
    lay, m = echoes(eyes, vers, rnd)
    full = base.copy(); full[m > 0] = lay[m > 0]
    for c, im in enumerate([base, marked(base, eyes), lay, full, film(FINAL[r])]):
        t = Image.fromarray(cv2.cvtColor(cv2.resize(im, (TW, TH)), cv2.COLOR_BGR2RGB)); sheet.paste(t, (c * TW, y))
        if r == 0:
            d.text((c * TW + 6, y + TH - 18), heads[c], fill=(0, 255, 255))
    tcode = "%02d:%02d:%02d:%02d" % (0, FINAL[r] // 1800, (FINAL[r] // 30) % 60, FINAL[r] % 30)
    d.rectangle((4 * TW, y, 4 * TW + 150, y + 18), fill=(0, 0, 0)); d.text((4 * TW + 4, y + 3), tcode, fill=(255, 220, 0))
os.makedirs(OUT, exist_ok=True)
sheet.save(os.path.join(OUT, "eye_effect.jpg"), quality=86)
print("eye_effect.jpg:", len(rows), "scenes")
