"""The ending's cards with the Edgerunners 2 trailer's red lines (matt, 2026-11-15), drawn with plugins/redlines:
  even cards: cracks running top to bottom down through the card's big word (redlines.cracks), a new drawing every
              frame, as the trailer's title cards
  odd cards:  slashes looping round the big word (redlines.slashes with the word's box as the matte), a new drawing
              every frame
On the red cards (background red) the lines take the card's ink instead of red, so they read.
The card geometry is read from the project (the big word per card, as plugins/endingCards.jsx picks it).
Writes assets/collage/redlines/card_NN/r_NNN.png (RGBA); plugins/endingCards.jsx places them.
  python textAnimations/assets/make_ending_redlines.py --project <a .ecproj with the ending's captions>"""
import argparse
import os
import json
import shutil
import subprocess
import sys

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "plugins", "redlines"))
sys.path.insert(0, HERE)
import redlines as RL  # noqa: E402

OUT = os.path.join(HERE, "collage", "redlines")
W, H = 1920, 1080
INK = [(255, 255, 255), (16, 24, 60), (254, 206, 0), (255, 255, 255)]   # RGB, as endingCards.jsx (index i % 4)
RED_BG = 3                                                               # the card colour index that's red

CLI = "C:/Users/0/effectcraft/target/release/effectcraft-cli.exe"

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


ap = argparse.ArgumentParser()
ap.add_argument("--project", required=True)
a = ap.parse_args()
cards = cards_of(a.project)

MATTE_JSX = r"""var C;for(var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof CompItem && it.name==="ending") C=it;}
for(var k=1;k<=C.numLayers;k++){var L=C.layer(k);
 if(/^cap /.test(L.name)){ var e=L.property("Effects"); for(var q=e.numProperties;q>=1;q--) e.property(q).remove();
   var f=e.addProperty("ADBE Fill"); f.property(f.property(1).matchName.replace(/-\d+$/,"")+"-0002").setValue([1,1,1,1]); }
 else if(L.name!=="black") L.enabled=false; }"""


def text_mattes(project, cards):
    """each card's own text, white on black, rendered from a scratch copy of the project with everything else off"""
    tmp = os.path.join(OUT, "_mattes"); os.makedirs(tmp, exist_ok=True)
    js = os.path.join(tmp, "m.jsx"); open(js, "w").write(MATTE_JSX)
    proj = os.path.join(tmp, "m.ecproj")
    subprocess.run([CLI, "--project", project, "script", js, "--save-as", proj], capture_output=True)
    out = []
    for i, c in enumerate(cards):
        png = os.path.join(tmp, "m_%02d.png" % (i + 1))
        subprocess.run([CLI, "--project", proj, "render-frame", "--comp", "ending", "--frame", str(c[0] + 3), "--out", png], capture_output=True)
        im = cv2.imread(png, cv2.IMREAD_GRAYSCALE)
        out.append((cv2.resize(im, (W, H)) > 128).astype(np.uint8) * 255 if im is not None else np.zeros((H, W), np.uint8))
    shutil.rmtree(tmp)
    return out


if os.path.isdir(OUT):
    shutil.rmtree(OUT)
os.makedirs(OUT)
mattes = text_mattes(a.project, cards)
for i, (start, end, wl, top, ww, wh) in enumerate(cards):
    n = end - start
    d = os.path.join(OUT, "card_%02d" % (i + 1)); os.makedirs(d)
    cx, cy = wl + ww / 2, top + wh / 2
    text = mattes[i]
    if not text.any():                               # no text found: fall back to the word's box
        cv2.rectangle(text, (int(wl), int(top)), (int(wl + ww), int(top + wh)), 255, -1)
    hugm = cv2.dilate(text, np.ones((9, 9), np.uint8))   # the slashes loop round the letters' own outline
    recolor = INK[i % 4] if i % 4 == RED_BG else None
    for j in range(n):
        if i % 2 == 0:
            x0 = cx + (ww * 0.18 if (i // 2) % 2 else -ww * 0.22)
            path = [(x0 + 60, -20), (x0, cy), (x0 - 40, H + 20)]
            im = RL.cracks("card %d f %d" % (i, j), path, avoid=text)   # bending round each letter
        else:
            im = RL.slashes("card %d f %d" % (i, j), matte=hugm, n=3)
            # weaving: on part of the word (a band that moves every few frames) the slashes go behind the letters
            rr = np.random.default_rng(i * 1000 + j // 3)
            bx = int(wl + rr.uniform(0, 1) * ww); bw_ = int(ww * rr.uniform(0.25, 0.5))
            band = np.zeros((H, W), np.float32); band[:, max(0, bx - bw_):bx + bw_] = 1
            im[:, :, 3] = (im[:, :, 3].astype(np.float32) * (1 - band * (text > 0))).astype(np.uint8)
        if recolor is not None:
            im[:, :, :3] = recolor
        cv2.imwrite(os.path.join(d, "r_%03d.png" % (j + 1)), cv2.cvtColor(im, cv2.COLOR_RGBA2BGRA))
    print("card", i + 1, "cracks" if i % 2 == 0 else "slashes", n, "frames")
