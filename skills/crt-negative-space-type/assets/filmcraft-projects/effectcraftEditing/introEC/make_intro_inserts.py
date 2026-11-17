"""The cold open's flash cuts, made from matt (matt, 2026-11-16: "the in-between zoomed-in masked shots ... the same
effect we did before ... using me"): the launch film ending's girl inserts (listeningkit-templates textAnimations/assets/
make_ending_girl_inserts.py) with him instead: 16 moments of him from the recording (the 20min edit's camera cutaway
moments, spread through it), each framed zoomed in on his face, pushing in over 4 frames, with the cyberpsycho eye
glitch (eye_glitch, unchanged: his eyes echoing outwards, face cut-ins from his other shots, a quadrant to another
shot, band slips; drawn new every frame) and the Edgerunners 2 red slashes (plugins/redlines) looping round his matte
(rembg, as make_face_cutouts.py), masked on black. And red cracks through the giant words, as there.
Writes mattins/ins_NN/f_NN.jpg (4 frames each) and mattins/giant_NN/c_NN.png (RGBA cracks, 7 frames each).
  uv run --no-project --with "rembg[cpu]" --with "opencv-python-headless<5" --with "numpy<3" python make_intro_inserts.py"""
import json
import os
import random
import shutil
import subprocess
import sys

import cv2
import numpy as np
from PIL import Image
from rembg import new_session, remove

HERE = os.path.dirname(os.path.abspath(__file__))
TA = r"C:/Users/0/.buzz/REPOS/listeningkit-templates/textAnimations"
sys.path.insert(0, os.path.join(TA, "plugins", "redlines"))
import redlines as RL  # noqa: E402

CAM = r"C:\Users\0\AppData\Roaming\so.cap.desktop\recordings\Generic PnP Monitor (Display) 2026-11-16 03.27 PM.cap\content\segments\segment-0\camera.mp4"
OUT = os.path.join(HERE, "mattins")
W, H = 1920, 1080
N_INS, INS_LEN, N_GIANT, GIANT_LEN = 16, 4, 6, 7

# eye_glitch / paste / push, from the girl script unchanged
src = open(os.path.join(TA, "assets", "make_ending_girl_inserts.py"), encoding="utf8").read()
G = {"np": np, "cv2": cv2, "W": W, "H": H}
for name in ("def paste", "def eye_glitch", "def push"):
    a = src.index(name); b = src.index("\n\n\n", a)
    exec(compile(src[a:b], "make_ending_girl_inserts.py", "exec"), G)

det_face = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
det_eye = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")
sess = new_session("u2net_human_seg")

# 16 moments: the 20min edit's camera cutaways (the punchlines, curses and numbers), spread through the recording
cams = json.load(open(os.path.join(HERE, "..", "effectcraftEditing-camera-20min-v10.json")))
pick = [cams[int(i * (len(cams) - 1) / (N_INS - 1))] for i in range(N_INS)]
TIMES = [c["source_in_frame"] / 60 + 0.3 for c in pick]


def grab(t):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", "%.3f" % t, "-i", CAM, "-frames:v", "1", "-f", "rawvideo",
                          "-pix_fmt", "bgr24", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(720, 1280, 3).copy()


def framed(cam):
    """zoomed in on his face: the face about 55% of the frame's height, centred a little high"""
    g = cv2.cvtColor(cam, cv2.COLOR_BGR2GRAY)
    f = det_face.detectMultiScale(g, 1.1, 6, minSize=(80, 80))
    x, y, w, h = max(f, key=lambda b: b[2] * b[3]) if len(f) else (458, 351, 281, 281)
    k = 0.55 * H / h
    big = cv2.resize(cam, (int(1280 * k), int(720 * k)), interpolation=cv2.INTER_CUBIC)
    cx, cy = (x + w / 2) * k, (y + h / 2) * k
    x0 = int(min(max(cx - W / 2, 0), big.shape[1] - W)) if big.shape[1] >= W else 0
    y0 = int(min(max(cy - H * 0.45, 0), big.shape[0] - H)) if big.shape[0] >= H else 0
    out = np.zeros((H, W, 3), np.uint8)
    crop = big[y0:y0 + H, x0:x0 + W]
    out[:crop.shape[0], :crop.shape[1]] = crop
    return out


def eyes_of(img):
    """his eyes as shares of the frame: the eye cascade inside the face, else the face's proportions"""
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    f = det_face.detectMultiScale(g, 1.1, 6, minSize=(200, 200))
    if not len(f):
        return ((.44, .40), (.56, .40))
    x, y, w, h = max(f, key=lambda b: b[2] * b[3])
    e = det_eye.detectMultiScale(g[y:y + h // 2 + h // 8, x:x + w], 1.1, 8, minSize=(w // 10, w // 10))
    if len(e) >= 2:
        e = sorted(sorted(e, key=lambda b: b[2] * b[3])[-2:], key=lambda b: b[0])
        return tuple(((x + ex + ew / 2) / W, (y + ey + eh / 2) / H) for ex, ey, ew, eh in e)
    return (((x + .3 * w) / W, (y + .4 * h) / H), ((x + .7 * w) / W, (y + .4 * h) / H))


def matte_of(img):
    m = np.array(remove(Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)), session=sess, only_mask=True))
    return (m > 120).astype(np.uint8) * 255


if os.path.isdir(OUT):
    shutil.rmtree(OUT)
shots = [framed(grab(t)) for t in TIMES]
eyes = [eyes_of(s) for s in shots]
mattes = [matte_of(s) for s in shots]
for i in range(N_INS):
    img, m = shots[i], mattes[i]
    d = os.path.join(OUT, "ins_%02d" % (i + 1)); os.makedirs(d)
    others = [shots[q] for q in range(N_INS) if q != i]
    for j in range(INS_LEN):
        s = 1.0 + 0.025 * j
        rnd = random.Random("matt eyes %d %d" % (i, j))
        g = G["eye_glitch"](img, eyes[i], others, rnd, j)
        base = G["push"](g, s).astype(np.float32)
        # masked on black (matt: "zoomed-in masked shots on black"): him, the glitch and the eye echoes kept inside his
        # matte grown a little, black round him
        keep = cv2.GaussianBlur(cv2.dilate(G["push"](m, s), np.ones((31, 31), np.uint8)), (0, 0), 6).astype(np.float32) / 255
        base = base * keep[:, :, None]
        sl = RL.slashes("matt %d %d" % (i, j), matte=G["push"](m, s), n=random.Random(i * 7 + j).randint(2, 4))
        a = sl[:, :, 3:4].astype(np.float32) / 255
        out = base * (1 - a) + sl[:, :, :3][:, :, ::-1].astype(np.float32) * a
        cv2.imwrite(os.path.join(d, "f_%02d.jpg" % (j + 1)), out.astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 92])
    print("insert", i + 1, "at %.1f s" % TIMES[i], flush=True)
for g in range(N_GIANT):
    d = os.path.join(OUT, "giant_%02d" % (g + 1)); os.makedirs(d)
    x = random.Random("intro giant %d" % g).uniform(0.35, 0.65) * W
    for j in range(GIANT_LEN):
        im = RL.cracks("intro giant %d %d" % (g, j), [(x + 60, -20), (x, H / 2), (x - 50, H + 20)])
        cv2.imwrite(os.path.join(d, "c_%02d.png" % (j + 1)), cv2.cvtColor(im, cv2.COLOR_RGBA2BGRA))
    print("giant cracks", g + 1, flush=True)
json.dump(TIMES, open(os.path.join(OUT, "times.json"), "w"))
