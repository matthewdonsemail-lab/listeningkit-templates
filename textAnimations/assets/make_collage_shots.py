"""Random cut-up collage per story shot (Nick Jayk style), from the original still and its 8 style variations.
All variations share the original's composition, so a rectangle cut from any of them lands in place.
Every 2 frames a new layout: sometimes a whole variation, otherwise a base image with 3-8 random rectangles
from other variations pasted over it (some enlarged around their centre, some nudged, each a touch brighter or
darker so the edges show). The first 4 frames are the clean original. Writes assets/collage/<stem>.mp4 (30 fps)."""
import os
import random
import subprocess

from PIL import Image, ImageEnhance

IMG = "C:/Users/0/.buzz/REPOS/listeningkit-templates/images/"
OUT = "C:/Users/0/.buzz/REPOS/listeningkit-templates/textAnimations/assets/collage/"
W, H, FPS = 1920, 1072, 30
STYLES = ["hyperreal", "ps2", "oil", "magritte", "clay", "ukiyoe", "macpaint", "crtcollage"]
# stem, original still, shot length (s)
SHOTS = [("01_log_ingests", "shadow/01_log_ingests", 1.24), ("02_every_conversation", "shadow/02_every_conversation", 1.04),
         ("03_youve_ever_had", "beats/03_youve_ever_had", 1.00), ("05_a_voice_profile", "shadow/05_a_voice_profile", 1.23),
         ("06_of_you", "shadow/06_of_you", 1.00), ("07_local_models", "beats/07_local_models", 0.97),
         ("08_re_rank", "shadow/08_re_rank", 0.63), ("09_embed", "beats/09_embed", 0.70),
         ("10_vector_search", "beats/10_vector_search", 0.90), ("11_the_way_you_actually", "beats/11_the_way_you_actually", 0.94),
         ("12_talk", "shadow/12_talk", 1.06), ("13_time_back", "shadow/13_time_back", 1.80),
         ("Blue_Noir_Only_Moat", "Blue Noir Only Moat", 2.43)]
os.makedirs(OUT, exist_ok=True)


def load(p):
    return Image.open(p).convert("RGB").resize((W, H), Image.LANCZOS)


for stem, orig, dur in SHOTS:
    rnd = random.Random(stem)
    base = load(IMG + orig + ".png")
    var = [load(IMG + "variants/%s/%s.png" % (stem, s)) for s in STYLES
           if os.path.exists(IMG + "variants/%s/%s.png" % (stem, s))]
    pool = [base] + var
    n = int(round(dur * FPS)) + 2
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "%dx%d" % (W, H),
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p",
                          OUT + stem + ".mp4"], stdin=subprocess.PIPE)
    frame = base
    for f in range(n):
        if f >= 4 and f % 2 == 0:  # new layout every 2 frames
            if rnd.random() < 0.22:
                frame = rnd.choice(var).copy()  # a whole variation
            else:
                frame = rnd.choice([base, base, rnd.choice(var)]).copy()
                for _ in range(rnd.randint(3, 8)):
                    src = rnd.choice(pool)
                    w = int(W * rnd.uniform(0.10, 0.42))
                    h = int(H * rnd.uniform(0.08, 0.36))
                    x, y = rnd.randint(0, W - w), rnd.randint(0, H - h)
                    patch = src.crop((x, y, x + w, y + h))
                    s = rnd.choice([1.0, 1.0, rnd.uniform(1.2, 1.7)])  # some enlarged, like the blown-up eye
                    if s > 1:
                        pw, ph = int(w * s), int(h * s)
                        patch = src.crop((x + (w - w / s) / 2, y + (h - h / s) / 2,
                                          x + (w + w / s) / 2, y + (h + h / s) / 2)).resize((w, h), Image.LANCZOS)
                    patch = ImageEnhance.Brightness(patch).enhance(rnd.choice([0.8, 0.9, 1.12, 1.25]))
                    dx, dy = int(rnd.uniform(-0.04, 0.04) * W), int(rnd.uniform(-0.03, 0.03) * H)
                    frame.paste(patch, (min(max(x + dx, 0), W - w), min(max(y + dy, 0), H - h)))
        p.stdin.write(frame.tobytes())
    p.stdin.close()
    p.wait()
    print(stem, n, "frames")
