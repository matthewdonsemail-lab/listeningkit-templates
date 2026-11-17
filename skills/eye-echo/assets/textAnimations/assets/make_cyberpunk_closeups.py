"""Cyberpunk: the close-up half of the cut as one collage video (assets/collage/cyberpunk_closeups.mp4).
Every close-up is aligned first: scaled and cropped so the point between its eyes (the core, for the brain) sits at
frame centre with the eyes the same distance apart, so anything cut from one lands in place on another.
- Underneath, the face hard-cuts to the next variation every 4 frames (photo, anime, the five Intro 1 styles, the
  brain), with no zoom or move on the cuts: the only movement is the slow push the comp puts on the whole video.
- On top, a collage that builds: every 2 frames 1-2 large rectangle strips cut from other variations, placed around
  her face, and 1-2 of her features (an eye, an eyebrow, the nose, the lips) cut from a variation, enlarged in place.
  They pile up over each other (the newest 12 stay), so the collage keeps growing and turning over.
The first 4 frames are the clean photo close-up, so the zoom from the overhead lands on her face."""
import random
import subprocess

from PIL import Image, ImageEnhance, ImageOps

CP = "C:/Users/0/.buzz/REPOS/listeningkit-templates/projects/cyberpunk/"
OUT = "C:/Users/0/.buzz/REPOS/listeningkit-templates/textAnimations/assets/collage/cyberpunk_closeups.mp4"
W, H, FPS, FRAMES = 1920, 1080, 30, 183  # VO: "now" (17.60 s) to "introducing" (23.70 s)
SPAN = 520  # eyes this far apart on screen in every variation
# file, centre x, centre y, pupil-to-pupil distance (source pixels, 2752x1536); the variants share eyes2's framing
SRC = {
    "photo": (CP + "eyes2.png", 1390, 610, 355),
    "anime": (CP + "eyes3.png", 1397, 612, 333),
    "brain": (CP + "eyes1.png", 1376, 695, None),
}
STYLES = ["ps2", "oil", "magritte", "clay", "ukiyoe"]
for s in STYLES:
    SRC[s] = (CP + "variants/eyes2/%s.png" % s, 1390, 610, 355)
CYCLE = ["photo", "anime", "ps2", "oil", "magritte", "brain", "clay", "ukiyoe"]
FACES = ["photo", "anime"] + STYLES  # the variations her features are cut from
# her features in the aligned frame: centre x, centre y, width, height
FEATURES = {"eye left": (718, 443, 330, 190), "eye right": (1202, 634, 330, 190), "brow left": (660, 345, 380, 140),
            "brow right": (1180, 530, 360, 130), "nose": (838, 770, 260, 230), "lips": (760, 985, 380, 170)}
FACE = (0.22, 0.10, 0.78, 0.98)  # the rectangle strips circle around this box (fractions of the frame)
KEEP = 12


def aligned(path, cx, cy, span):
    im = Image.open(path).convert("RGB")
    k = 1.0 if span is None else SPAN / span
    cw, ch = W / k, H / k
    x0 = min(max(cx - cw / 2, 0), im.width - cw)
    y0 = min(max(cy - ch / 2, 0), im.height - ch)
    return im.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((W, H), Image.LANCZOS)


pool = {k: aligned(*v) for k, v in SRC.items()}
rnd = random.Random("cyberpunk closeups v2")


def tone(im):
    return ImageEnhance.Brightness(im).enhance(rnd.choice([0.8, 0.92, 1.1, 1.25]))


def strip():
    l, t, r, b = FACE
    w, h = int(W * rnd.uniform(0.16, 0.34)), int(H * rnd.uniform(0.08, 0.30))
    if rnd.random() < 0.35:  # a long thin strip across her
        w, h = int(W * rnd.uniform(0.32, 0.52)), int(H * rnd.uniform(0.04, 0.09))
    cx, cy = rnd.uniform(l, r) * W, rnd.uniform(t, b) * H
    x, y = int(min(max(cx - w / 2, 0), W - w)), int(min(max(cy - h / 2, 0), H - h))
    src = pool[rnd.choice(FACES)]
    s = rnd.choice([0.8, 1.0, 1.0, 1.3, 1.6])
    sw, sh = w / s, h / s
    sx = min(max(x + w / 2 - sw / 2, 0), W - sw)
    sy = min(max(y + h / 2 - sh / 2, 0), H - sh)
    patch = tone(src.crop((int(sx), int(sy), int(sx + sw), int(sy + sh))).resize((w, h), Image.LANCZOS))
    dx, dy = int(rnd.uniform(-0.03, 0.03) * W), int(rnd.uniform(-0.03, 0.03) * H)
    return patch, (min(max(x + dx, 0), W - w), min(max(y + dy, 0), H - h))


def feature():
    cx, cy, fw, fh = FEATURES[rnd.choice(list(FEATURES))]
    src = pool[rnd.choice(FACES)]
    crop = src.crop((int(max(cx - fw / 2, 0)), int(max(cy - fh / 2, 0)), int(min(cx + fw / 2, W)), int(min(cy + fh / 2, H))))
    s = rnd.uniform(1.25, 2.1)  # enlarged, the way Intro 1 blew up the eye
    w, h = int(crop.width * s), int(crop.height * s)
    patch = tone(crop.resize((w, h), Image.LANCZOS))
    ox, oy = rnd.uniform(-0.06, 0.06) * W, rnd.uniform(-0.05, 0.05) * H
    x, y = int(cx - w / 2 + ox), int(cy - h / 2 + oy)
    return patch, (min(max(x, 0), W - w), min(max(y, 0), H - h))


stack = []
p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "%dx%d" % (W, H),
                      "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", OUT],
                     stdin=subprocess.PIPE)
for f in range(FRAMES):
    seg = f // 4
    base = pool[CYCLE[seg % len(CYCLE)]]
    if f >= 4 and f % 2 == 0:
        for _ in range(rnd.randint(1, 2)):
            stack.append(strip())
        for _ in range(rnd.randint(1, 2)):
            stack.append(feature())
        stack = stack[-KEEP:]
    frame = base.copy()
    if seg % 2 == 1:  # every other 4-frame cut is the collage; the rest are her full face, clean, so she reads
        for patch, pos in stack:
            frame.paste(patch, pos)
    p.stdin.write(ImageOps.mirror(frame).tobytes())  # flipped so her head sits where it is in the overhead
p.stdin.close()
p.wait()
print(FRAMES, "frames ->", OUT)
