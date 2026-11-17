"""The cold open's type with random letters switching font inside every word (matt, 2026-11-17: "random letters
changed in all of the words"). EffectCraft can't give single letters of one text layer their own font, so the type is
drawn here, frame by frame: every letter sits where its Satoshi letter sits (Satoshi Bold advances, the layers'
own positions, sizes, alignment and line spacing from textlayers.json), and every 3 frames about a third of the letters
are redrawn in the 8-bit font (Press Start 2P) or the gothic one (UnifrakturMaguntia), centred in the Satoshi
letter's cell, sized to its cap height. The line cards keep their word-by-word reveal (beats.json); the word cards and
their small lines are drawn for their 2 frames. White on transparent: the layers' ink Fill colours it in EffectCraft.
Writes letters/<layer>/t_NNN.png (RGBA, 1920x1080, NNN = frame within the layer).
  uv run --no-project --with pillow python make_letter_text.py"""
import json
import math
import os
import shutil

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FD = r"C:\Users\0\AppData\Local\Microsoft\Windows\Fonts"
SAT, PIX, GOT = (os.path.join(FD, f) for f in ("Satoshi-Bold.otf", "PressStart2P-Regular.ttf", "UnifrakturMaguntia-Book.ttf"))
W, H, F = 1920, 1080, 30
ALT_SHARE, HOLD = 0.34, 3
layers = json.load(open(os.path.join(HERE, "textlayers.json"), encoding="utf-8-sig"))
beats = json.load(open(os.path.join(HERE, "beats.json")))
OUT = os.path.join(HERE, "letters")
if os.path.isdir(OUT):
    shutil.rmtree(OUT)
cache = {}


def font(path, size):
    k = (path, size)
    if k not in cache:
        cache[k] = ImageFont.truetype(path, size)
    return cache[k]


def rnd(*a):
    x = math.sin(sum((i + 1) * 12.9898 * v for i, v in enumerate(a)) + 4.1414) * 43758.5453
    return x - math.floor(x)


def draw_line(d, text, x, y, size, just, seed, f, upto=None):
    """one line of type, letters mixing fonts; upto: how many characters are visible (reveal)"""
    sat = font(SAT, size)
    advs = [sat.getlength(c) for c in text]
    total = sum(advs)
    x0 = x if just == "L" else (x - total / 2 if just == "C" else x - total)
    cap = sat.getbbox("H", anchor="ls")[1]                 # negative: cap height above the baseline
    for i, c in enumerate(text):
        if upto is not None and i >= upto:
            break
        if c != " ":
            r = rnd(seed, i, f // HOLD)
            if r < ALT_SHARE / 2:
                fp, k = PIX, 0.62
            elif r < ALT_SHARE:
                fp, k = GOT, 1.05
            else:
                fp, k = SAT, 1.0
            fn = font(fp, max(6, int(size * k)))
            if fp != SAT:                                  # fit the alt glyph to the cell: cap height, then width
                g = fn.getbbox("H", anchor="ls")[1]
                s2 = max(6, int(size * k * (cap / g if g else 1)))
                fn = font(fp, s2)
                w = fn.getlength(c)
                if w > advs[i] * 1.15:
                    fn = font(fp, max(6, int(s2 * advs[i] * 1.15 / w)))
                cx = x0 + advs[i] / 2
                d.text((cx, y), c, font=fn, fill=(255, 255, 255, 255), anchor="ms")
            else:
                d.text((x0, y), c, font=fn, fill=(255, 255, 255, 255), anchor="ls")
        x0 += advs[i]


def card_reveal(idx, text, t):
    """characters visible per line at time t: the card's words land when he says them (beats.json)"""
    words = beats[idx]["words"]
    lines = text.split("\r")
    out, wi = [], 0
    for ln in lines:
        vis, pos = 0, 0
        for w_ in ln.split(" "):
            if wi < len(words) and t >= words[wi][0] - 0.04:
                vis = pos + len(w_)
            pos += len(w_) + 1
            wi += 1
        out.append(vis)
    return out


# the line cards as chunks of 1-2 words, big, around the screen (baseline x, y, alignment), cycled
SPOTS = [(110, 430, "L"), (1810, 820, "R"), (960, 300, "C"), (110, 880, "L"), (1810, 360, "R"), (960, 930, "C"),
         (110, 640, "L"), (1810, 600, "R")]
BIG, MAXW = 240, 1500
chunks, k = [], 0
for bi, b in enumerate(beats):
    ws = [(w[0], w[1].upper()) for w in b["words"]]
    groups, i = [], 0
    while i < len(ws):
        g = [ws[i]]
        if len(ws[i][1]) < 7 and i + 1 < len(ws) and len(ws[i][1]) + len(ws[i + 1][1]) <= 11:
            g.append(ws[i + 1])
        groups.append(g); i += len(g)
    cs = []
    for g in groups:
        text = " ".join(w for _, w in g)
        sx, sy, sj = SPOTS[k % len(SPOTS)]
        size = BIG
        while font(SAT, size).getlength(text) > MAXW and size > 80:
            size -= 10
        marks, pos = [], 0
        for wt, w in g:
            pos += len(w); marks.append((wt, pos)); pos += 1
        cs.append({"text": text, "t0": g[0][0], "marks": marks, "x": sx, "y": sy, "j": sj, "size": size, "k": k})
        k += 1
    chunks.append(cs)


n = 0
for L in layers:
    name = L["name"]
    size = L["size"] / {"Press Start 2P": 0.5, "UnifrakturMaguntia": 1.15}.get(L["font"], 1.0)
    size = int(round(size))
    d_ = os.path.join(OUT, name.replace(" ", "_")); os.makedirs(d_)
    seed = sum(ord(c) * (i + 1) for i, c in enumerate(name)) % 9973
    for fr in range(L["a"], L["b"]):
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
        if name.startswith("card "):
            # matt: "larger text, smaller amounts of words, switching between ... more of it around the screen":
            # the line goes up 1-2 words at a time, big, each chunk at a new place, words landing as he says them
            idx = int(name.split()[1]) - 1
            ch = chunks[idx]; t = fr / F
            cur = None
            for c in ch:
                if t >= c["t0"] - 0.04:
                    cur = c
            if cur is not None:
                upto = 0
                for wt, end in cur["marks"]:
                    if t >= wt - 0.04:
                        upto = end
                draw_line(d, cur["text"], cur["x"], cur["y"], cur["size"], cur["j"], seed + cur["k"] * 31, fr, upto)
        else:
            draw_line(d, L["text"].replace("\r", " "), L["x"], L["y"], size, L["j"], seed, fr)
        img.save(os.path.join(d_, "t_%03d.png" % (fr - L["a"])))
        n += 1
print(len(layers), "layers,", n, "frames")
