"""The ending's heartbeat lines drawn like our cyberpsycho lines (matt, 2026-11-15): the same pen as
plugins/cyberpsycho/cyberpsycho.py (jittered variable-width strokes, sharp corners, new drawing every second frame,
a blade-wedge swelling on the spike, barbs and ticks, a dark outline, the CRT glitch), following a heartbeat path
through each card's big word: drawn on left to right with a bright hot head, then eaten from the left.
The card geometry is read from the project (the big word per card, as plugins/endingCards.jsx picks it); the ink per
card matches endingCards.jsx.
Writes assets/collage/heartbeat/card_NN/h_NNN.png (RGBA, one per frame of the card) and paths.json; then
plugins/endingCards.jsx uses them in place of its shape-layer line.
  python textAnimations/assets/make_heartbeat_lines.py --project <a .ecproj with the ending's captions>"""
import argparse
import json
import math
import os
import random
import shutil
import subprocess
import sys

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "plugins", "cyberpsycho"))
import cyberpsycho as CP  # noqa: E402

CLI = "C:/Program Files/ArtCraft/EffectCraft/effectcraft-cli.exe"
OUT = os.path.join(HERE, "collage", "heartbeat")
W, H, F = 1920, 1080, 30
DRAW, ERASE_AT = 12, 18
INK = [(255, 255, 255), (16, 24, 60), (254, 206, 0), (255, 255, 255)]   # RGB, as endingCards.jsx
DARK = [(10, 10, 14), (254, 206, 0), (16, 24, 60), (40, 0, 6)]          # the outline: the card's background-ish

DUMP = r"""var C;for(var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof CompItem && it.name==="ending") C=it;}
var cards={},order=[];
for(var k=1;k<=C.numLayers;k++){var L=C.layer(k); if(!/^cap /.test(L.name)) continue; var f=Math.round(L.inPoint*30), d=L.property("Source Text").value;
 if(!cards[f]){cards[f]={start:f,end:Math.round(L.outPoint*30),key:null,ks:0};order.push(f);} if(d.fontSize>cards[f].ks){cards[f].ks=d.fontSize;cards[f].key=L;}}
order.sort(function(a,b){return a-b;}); var out=[];
for(var i=0;i<order.length;i++){var c=cards[order[i]],L=c.key,p=L.property("Transform").property("Position").value,r={left:0,top:-c.ks*0.7,width:c.ks*3,height:c.ks*0.7};
 try{var q=L.sourceRectAtTime((c.start+3)/30,false); if(q.width>10) r=q;}catch(e){}
 out.push("["+c.start+","+c.end+","+(p[0]+r.left)+","+(p[1]+r.top)+","+r.width+","+r.height+"]");}
writeLn("CARDS ["+out.join(",")+"]");"""


def cards_of(project):
    tmp = os.path.join(OUT, "_dump.jsx")
    os.makedirs(OUT, exist_ok=True)
    open(tmp, "w").write(DUMP)
    r = subprocess.run([CLI, "--project", project, "script", tmp], capture_output=True, text=True)
    os.remove(tmp)
    line = next(l for l in r.stdout.splitlines() if l.startswith("CARDS "))
    return json.loads(line[6:])


def beat(wl, wr, cy, wh, flip):
    """the heartbeat's corners: flat across the frame, the beat in the bigger empty space beside the word"""
    d, u = (-1 if flip else 1), max(28.0, wh / 3.2)
    bx = wl / 2 if wl > W - wr else (wr + W) / 2
    bx = max(7 * u, min(W - 6 * u, bx))
    return [(-40, cy), (bx - 7 * u, cy), (bx - 5.8 * u, cy - 0.8 * u * d), (bx - 4.6 * u, cy), (bx - 2 * u, cy),
            (bx - 1.4 * u, cy + 1.1 * u * d), (bx - 0.5 * u, cy - 5.5 * u * d), (bx + 0.5 * u, cy + 3 * u * d),
            (bx + 1.3 * u, cy), (bx + 3 * u, cy - 1.3 * u * d), (bx + 4.6 * u, cy), (W + 40, cy)], (6, 7, 8)


def resample(corners, step=9.0):
    """the corners as dense points (keeping the corners), with each point's segment index"""
    pts, seg = [], []
    for i in range(len(corners) - 1):
        a, b = np.array(corners[i], np.float32), np.array(corners[i + 1], np.float32)
        n = max(1, int(np.hypot(*(b - a)) / step))
        for k in range(n):
            pts.append(a + (b - a) * k / n); seg.append(i)
    pts.append(np.array(corners[-1], np.float32)); seg.append(len(corners) - 2)
    pts = np.array(pts)
    arc = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(pts, axis=0).T))])
    return pts, np.array(seg), arc / arc[-1]


def draw(card_i, j, n, pts, seg, arc, spike, ink, dark):
    """frame j of n of one card's line"""
    rnd = random.Random("heartbeat %d %d" % (card_i, j // 2))          # a new drawing on twos
    pen = CP.Pen(W, H, rnd)
    pen.k = W / CP.REF_W
    head = 1 - (1 - min(1.0, j / DRAW)) ** 3
    ea = min(ERASE_AT, n - 6)
    tail = min(1.0, max(0.0, (j - ea) / max(4, n - ea - 1))) ** 2
    on = (arc <= head) & (arc >= tail)
    if on.sum() < 2:
        return np.zeros((H, W, 4), np.uint8)
    p, s = pts[on], seg[on]
    jit = np.array([[rnd.uniform(-2.2, 2.2), rnd.uniform(-2.2, 2.2)] for _ in p], np.float32) * pen.k
    jit[:, 1] *= np.where(np.isin(s, spike), 0.4, 1)                    # keep the spike sharp
    p = p + jit
    w = np.array([rnd.choice([2.5, 3, 3.5, 4.5]) for _ in p], np.float32)
    # the spike swells into a blade wedge and tapers to its point, like the cyberpsycho blades
    sp = np.where(np.isin(s, spike))[0]
    if len(sp) > 2:
        t = np.linspace(0, 1, len(sp))
        peak = rnd.uniform(0.3, 0.6)
        w[sp] = np.maximum(w[sp], rnd.choice([12, 16, 22]) * np.where(t < peak, t / peak, (1 - t) / (1 - peak)) ** 1.2)
    for _ in range(rnd.randint(0, 2)):                                  # a short thick slab on the flat
        i0 = rnd.randrange(len(w)); w[i0:i0 + 3] = rnd.uniform(9, 16)
    pen.poly(p, w)
    for _ in range(rnd.randint(1, 3)):                                  # ticks / barbs off it
        i0 = rnd.randrange(len(p))
        a = rnd.choice([-1, 1]) * math.pi / 2 + rnd.uniform(-0.5, 0.5)
        pen.poly([p[i0], p[i0] + rnd.uniform(10, 40) * pen.k * np.array([math.cos(a), math.sin(a)])], [2.5, 1])
    if rnd.random() < 0.5:                                              # a drip off the spike
        CP.drip(pen, pts[sp[len(sp) // 2]] if len(sp) else p[-1], 0)
    rgba = CP._finish(pen, ink, dark, 3)
    # the hot head: a bright core and glow at the drawing tip while it's still being drawn
    if head < 0.999:
        hx, hy = p[-1]
        core = np.zeros((H, W), np.float32)
        cv2.circle(core, (int(hx), int(hy)), int(9 * pen.k), 1.0, -1, cv2.LINE_AA)
        glow = cv2.GaussianBlur(core, (0, 0), 18) * 2.2
        a = np.clip(core + glow, 0, 1)
        col = np.array([255, 255, 255], np.float32) * core[:, :, None] + np.array(ink, np.float32) * (1 - core[:, :, None])
        out = rgba.astype(np.float32)
        out[:, :, :3] = out[:, :, :3] * (1 - a[:, :, None]) + col * a[:, :, None]
        out[:, :, 3] = np.maximum(out[:, :, 3], a * 255)
        rgba = out.astype(np.uint8)
    if j % 2 == 0 or j < DRAW:
        rgba = CP.glitch(rgba, "hb %d %d" % (card_i, j), 0.35 + 0.4 * (j < DRAW))
    return rgba


ap = argparse.ArgumentParser()
ap.add_argument("--project", required=True)
a = ap.parse_args()
cards = cards_of(a.project)
if os.path.isdir(OUT):
    shutil.rmtree(OUT)
os.makedirs(OUT)
paths = {}
for i, (start, end, wl, top, ww, wh) in enumerate(cards):
    if i % 2:
        continue                                                        # heartbeat on every other card
    cy = top + wh / 2
    corners, spike = beat(wl, wl + ww, cy, wh, i % 4 == 2)
    pts, seg, arc = resample(corners)
    n = end - start
    d = os.path.join(OUT, "card_%02d" % (i + 1)); os.makedirs(d)
    for j in range(n):
        im = draw(i, j, n, pts, seg, arc, spike, INK[i % 4], DARK[i % 4])
        cv2.imwrite(os.path.join(d, "h_%03d.png" % (j + 1)), cv2.cvtColor(im, cv2.COLOR_RGBA2BGRA))
    paths[i + 1] = {"start": start, "end": end, "first": os.path.join(d, "h_001.png").replace("\\", "/")}
    print("card", i + 1, n, "frames")
json.dump(paths, open(os.path.join(OUT, "paths.json"), "w"), indent=1)
