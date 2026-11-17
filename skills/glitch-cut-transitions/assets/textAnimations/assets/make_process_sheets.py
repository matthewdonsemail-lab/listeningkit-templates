"""Extra sheets for the process board (make_process_board.py), matt 2026-11-16:
  opener_bigshort.jpg    The Big Short reference frames (projects/opening/ref/bigshort_*.png): the look for the guys
  opener_shotref.jpg     the reference edit for the opener's shots (ref/shotref.mp4), a frame a second
  opener_sun_ae.jpg      the red sun_ae TikTok the cyberpsycho look comes from
  opener_psycho_steps.jpg  the two men going cyberpsycho in 12 steps each (psycho/blinds, psycho/chalk), and the mattes
                         (GrabCut) that cut each man off his background, so the effects stay on him
  opener_psycho_cut.jpg  the crazy cut itself (assets/collage/opening_psycho_v9.mp4): quadrants, face cut-ins, outward
                         eye echoes, cyberpsycho lines out of the eyes
  transition_howto.jpg   one cut blend taken apart: shot A, shot B, then every blend frame between them
Written to textAnimations/assets/collage/process/.
  python textAnimations/assets/make_process_sheets.py [<dir of the clean opening frames f_NNNNN.jpg>]"""
import glob
import os
import sys

import cv2
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OP = os.path.join(REPO, "projects", "opening")
OUT = os.path.join(HERE, "collage", "process")
os.makedirs(OUT, exist_ok=True)
TW, TH = 384, 216


def sheet(ims, cols, path, labels=None):
    rows = (len(ims) + cols - 1) // cols
    s = Image.new("RGB", (cols * TW, rows * TH), (16, 16, 18))
    for i, im in enumerate(ims):
        t = im.convert("RGB").copy(); t.thumbnail((TW, TH))
        s.paste(t, ((i % cols) * TW + (TW - t.width) // 2, (i // cols) * TH + (TH - t.height) // 2))
        if labels:
            d = ImageDraw.Draw(s); d.rectangle(((i % cols) * TW, (i // cols) * TH, (i % cols) * TW + 140, (i // cols) * TH + 16), fill=(0, 0, 0))
            d.text(((i % cols) * TW + 3, (i // cols) * TH + 2), labels[i], fill=(255, 220, 0))
    s.save(os.path.join(OUT, path), quality=86)
    print(path, len(ims))


def frames(video, every=None, n=None):
    cap = cv2.VideoCapture(video); total = int(cap.get(7)); fps = cap.get(5) or 30
    idx = list(range(0, total, every or int(fps))) if not n else [int(i * (total - 1) / (n - 1)) for i in range(n)]
    out = []
    for i in idx:
        cap.set(1, i); ok, f = cap.read()
        if ok:
            out.append(Image.fromarray(cv2.cvtColor(f, cv2.COLOR_BGR2RGB)))
    return out


sheet([Image.open(p) for p in sorted(glob.glob(os.path.join(OP, "ref", "bigshort_[0-9]*.png")))], 4, "opener_bigshort.jpg")
sheet(frames(os.path.join(OP, "ref", "shotref.mp4"), n=16), 4, "opener_shotref.jpg")
sheet(frames(os.path.join(OP, "ref", "sun_ae", "tiktok_7658403141708172558.mp4"), n=12), 4, "opener_sun_ae.jpg")
st = [Image.open(p) for p in sorted(glob.glob(os.path.join(OP, "psycho", "blinds", "*.png")))[::2]]
st += [Image.open(p) for p in sorted(glob.glob(os.path.join(OP, "psycho", "chalk", "*.png")))[::2]]
st += [Image.open(os.path.join(OP, "psycho", "blinds_matte.png")), Image.open(os.path.join(OP, "psycho", "chalk_matte.png"))]
sheet(st, 7, "opener_psycho_steps.jpg", ["blinds %d" % (i * 2) for i in range(6)] + ["chalk %d" % (i * 2) for i in range(6)] + ["matte", "matte"])
sheet(frames(os.path.join(HERE, "collage", "opening_psycho_v9.mp4"), n=24), 6, "opener_psycho_cut.jpg")
clean = sys.argv[1] if len(sys.argv) > 1 else None
c = 332
bl = [Image.open(p) for p in sorted(glob.glob(os.path.join(HERE, "collage", "secblend", "opening", "%04d" % c, "b_*.jpg")))]
ab = []
if clean:
    ab = [Image.open(os.path.join(clean, "f_%05d.jpg" % (c - 3))), Image.open(os.path.join(clean, "f_%05d.jpg" % (c + 3)))]
sheet(ab + bl, len(ab + bl), "transition_howto.jpg", (["shot A", "shot B"] if ab else []) + ["blend %d" % (i + 1) for i in range(len(bl))])
