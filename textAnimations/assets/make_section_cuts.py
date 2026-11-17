"""The clip blends and cut fx INSIDE the launch film's section comps (matt, 2026-11-15): under the CRT, the VHS look,
the 4:3 bars and the captions, and on every cut the picture really has, not just the edit's: the cyberpsycho clip's
alternations between the two men, the match-cut flow, the closeups' style switches, the outro's push, the busts.

1. Render each section clean (look layers, captions and old cut fx off) as PNG frames:
     cleansec.jsx (sets them off) then  effectcraft-cli render --comp opening --format png --out <dir>/opening/f.png
     (cyberpunk from --start 6.2333, the frame the launch film starts it on)
2. python textAnimations/assets/make_section_cuts.py --frames <dir>
   finds the cuts by frame difference, builds per cut a blend sequence (make_cut_blend.py's luma blend, displacement,
   datamosh, cut-in rectangles, echoes, flicks, tint) with a pixel sort burst on the cut frames, as JPEGs in
   assets/collage/secblend/<section>/<frame>/, and writes plugins/launchSectionCuts.jsx.
3. Run plugins/launchSectionCuts.jsx: in each section comp it puts the blends, the reference edit's extracted glitch
   (screened, on the bigger cuts) and an exposure ramp right above the picture, under captions and every look layer;
   and it takes the old launch-film-level cutfx / cutblend layers out."""
import argparse
import glob
import importlib.util
import json
import os
import random

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(HERE, "collage", "secblend")
FXDIR = os.path.join(ROOT, "projects", "opening", "ref", "tt_elements", "assets", "fx")
FX = [("02-03_rgb_glitch", "chroma"), ("29_pixel_blocks", "chroma"), ("16_eyes_noise", "streaks"), ("39_eyes_close", "lines")]
ap = argparse.ArgumentParser()
ap.add_argument("--frames", required=True)
ap.add_argument("--only", default="", help="section:frame,... to build just those (checking)")
ap.add_argument("--sections", default="opening,cyberpunk", help="which sections to rebuild; the others keep their blends")
a = ap.parse_args()

# the blend itself lives in make_cut_blend.py; load its functions without running its main part
src = open(os.path.join(HERE, "make_cut_blend.py"), encoding="utf8").read()
src = src[:src.index("os.makedirs(OUT, exist_ok=True)")]
src = src[src.index("# the tints"):]
B = {"np": np, "cv2": cv2, "random": random}
exec(compile("import numpy as np\nimport cv2\n" + src, "make_cut_blend.py", "exec"), B)
blend_frame, TINTS = B["blend_frame"], B["TINTS"]

spec = importlib.util.spec_from_file_location("x", os.path.join(HERE, "make_cut_fx.py"))
fxsrc = open(os.path.join(HERE, "make_cut_fx.py"), encoding="utf8").read()
fxsrc = fxsrc[fxsrc.index("def pixel_sort"):fxsrc.index("for ci, c in enumerate(cuts):")]
P = {"np": np, "cv2": cv2, "random": random}
exec(compile(fxsrc, "make_cut_fx.py", "exec"), P)
pixel_sort = P["pixel_sort"]

EDIT_OPENING = [23, 48, 64, 82, 109, 128, 153, 181, 215, 253, 281, 308]
BUSTS = [659, 693, 727, 760, 794, 827]


def frames_of(sec):
    fs = sorted(glob.glob(os.path.join(a.frames, sec, "f_*.png")) + glob.glob(os.path.join(a.frames, sec, "f_*.jpg")))
    return {int(os.path.basename(f)[2:7]): f for f in fs}


def find_cuts(sec, files):
    nums = sorted(files)
    small = {n: cv2.resize(cv2.imread(files[n]), (96, 54), interpolation=cv2.INTER_AREA).astype(np.float32) for n in nums}
    d = {n: float(np.abs(small[n] - small[n - 1]).mean()) for n in nums[1:] if n - 1 in small}
    keys = sorted(d)
    v = np.array([d[k] for k in keys])
    cuts = []
    for i, f in enumerate(keys):
        med = float(np.median(v[max(0, i - 7):i + 8]))
        flow = sec == "cyberpunk" and f < 265          # the match-cut flow: its cuts are softer
        if d[f] > (20 if flow else 25) and d[f] >= v[max(0, i - 1)] and d[f] >= v[min(len(v) - 1, i + 1)] \
                and (d[f] > 1.6 * med or flow):
            if cuts and f - cuts[-1] < (4 if flow else 2):
                continue
            cuts.append(f)
    if sec == "opening":
        cuts = sorted(set(cuts) | set(EDIT_OPENING))
    if sec == "cyberpunk":   # in the busts only the cut from one bust to the next (the rest is the line wiping)
        cuts = sorted({c for c in cuts if c < 655} | set(BUSTS))
    return cuts


def build(sec, files, cuts, todo):
    out = []
    lo, hi = min(files), max(files)
    for i, c in enumerate(cuts):
        gp = c - cuts[i - 1] if i else 99
        gn = cuts[i + 1] - c if i + 1 < len(cuts) else 99
        n = min(6, (min(gp, gn) - 1) // 2)
        if n < 1 or c - n - 1 < lo or c + n > hi:
            continue
        d = os.path.join(OUT, sec, "%04d" % c)
        out.append({"cut": c, "n": n, "first": os.path.join(d, "b_01.jpg").replace("\\", "/")})
        if todo is not None and (sec, c) not in todo:
            continue
        os.makedirs(d, exist_ok=True)
        fr = {f: cv2.imread(files[f]) for f in range(c - n - 1, c + n + 1)}
        rnd = random.Random("sec %s %d" % (sec, c))
        col = TINTS[(c // 7) % len(TINTS)]
        prev = None
        for j, k in enumerate(range(-n, n + 1)):
            A = fr[c + k] if k < 0 else fr[max(c - n, c - 1 - k)]
            Bf = fr[c + k] if k >= 0 else fr[min(c + n, c - k - 1)]
            pB = fr.get(c + k - 1) if k >= 1 else None
            img = blend_frame(A, Bf, pB, prev, k, n, rnd, col)
            if abs(k) <= 1 and rnd.random() < 0.65:   # the pixel sort burst on the cut
                ps = pixel_sort(img, "%s %d %d" % (sec, c, k))
                al = ps[:, :, 3:4].astype(np.float32) / 255
                img = (img * (1 - al) + ps[:, :, :3] * al).astype(np.uint8)
            cv2.imwrite(os.path.join(d, "b_%02d.jpg" % (j + 1)), img, [cv2.IMWRITE_JPEG_QUALITY, 93])
            prev = img
    return out


todo = None
if a.only:
    todo = {(x.split(":")[0], int(x.split(":")[1])) for x in a.only.split(",")}
data = {}
old = os.path.join(HERE, "..", "plugins", "launchSectionCuts.jsx")
if os.path.exists(old):                      # the sections not being rebuilt keep what they had
    import re
    m = re.search(r"var D=(\{.*?\}), FX=", open(old, encoding="utf8").read())
    if m:
        data = json.loads(m.group(1))
for sec in a.sections.split(","):
    files = frames_of(sec)
    cuts = find_cuts(sec, files)
    print(sec, len(cuts), "cuts:", cuts)
    data[sec] = build(sec, files, cuts, todo)
    print(sec, len(data[sec]), "blends")

fx = [os.path.join(FXDIR, n, "%s_%s.mov" % (n, l)).replace("\\", "/") for n, l in FX]
JSX = r"""// GENERATED by assets/make_section_cuts.py: the clip blends and cut fx inside the section comps, right above the
// picture, under the captions, CRT, VHS look and bars. Per cut: the blend sequence (pixel sort burst in it); on the
// bigger cuts the reference edit's glitch, screened; one exposure ramp layer over all of them. Rerun replaces them.
var D=__DATA__, FX=__FX__, F=30;
var LOOK=/^(thermal |exposure cuts|bar (left|right)|VHS look|Global Scale|Lens Distortions|Monitor|CRT|Channel Blur|CC|CC 2|Posterize Time|Position Flicker|Glitches|Distortions|Glow|cap |cutfx|cutblend)/;
function findComp(n){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof CompItem && it.name===n) return it;} return null; }
function findFile(p){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof FootageItem && it.file && it.file.fsName.replace(/\\/g,"/").toLowerCase()===p.toLowerCase()) return it;} return null; }
function seq(p){ var f=findFile(p); if(f){ f.replace(new File(p)); } else { var o=new ImportOptions(new File(p)); try{o.sequence=true;}catch(e){} f=app.project.importFile(o); } try{ f.mainSource.conformFrameRate=F; }catch(e){} return f; }
// the old ones on the launch film itself go
var LF=findComp("launch film"); if(LF) for (var k=LF.numLayers;k>=1;k--) if(/^(cutfx|cutblend) /.test(LF.layer(k).name)) LF.layer(k).remove();
var fx=[]; for (var i=0;i<FX.length;i++) fx.push(findFile(FX[i])||app.project.importFile(new ImportOptions(new File(FX[i]))));
var total=0;
for (var name in D){ var C=findComp(name); if(!C) continue; var cuts=D[name];
  for (var k=C.numLayers;k>=1;k--) if(/^(cutfx|cutblend) /.test(C.layer(k).name)) C.layer(k).remove();
  // the picture's top layer: the first one that isn't a look layer or a caption
  var top=null; for (var k=1;k<=C.numLayers;k++) if(!LOOK.test(C.layer(k).name)){ top=C.layer(k); break; }
  function place(L){ if(top) L.moveBefore(top); }
  var X=C.layers.addSolid([0,0,0],"cutfx exposure "+name,C.width,C.height,1); X.adjustmentLayer=true; X.startTime=0; X.inPoint=0; X.outPoint=C.duration; place(X);
  var ts=[];
  for (var i=0;i<cuts.length;i++){ var s=cuts[i], c=s.cut, n=s.n;
    var L=C.layers.add(seq(s.first)); L.name="cutblend "+name+" "+c; L.startTime=(c-n)/F; L.inPoint=(c-n)/F; L.outPoint=(c+n+1)/F; place(L);
    if(n>=3){ ts.push((c/F).toFixed(4));
      var G=C.layers.add(fx[i%fx.length]); G.name="cutfx glitch "+name+" "+c; G.startTime=(c-2)/F-(i%3)*2/F; G.inPoint=(c-2)/F; G.outPoint=(c+2)/F;
      G.blendingMode=BlendingMode.SCREEN; G.property("Transform").property("Opacity").setValue(55); place(G); }
    total++; }
  // the ramp over the blends and glitch, still under the captions and looks
  for (var k=1;k<=C.numLayers;k++){ var nm=C.layer(k).name; if(/^cut(fx|blend) /.test(nm) && nm.indexOf("cutfx exposure")!==0){ if(C.layer(k)!==X) X.moveBefore(C.layer(k)); break; } }
  X.property("Effects").addProperty("ec.color.exposure").property("master").property("exposure").expression=
    "var cuts=["+ts.join(",")+"],env=0;for(var i=0;i<cuts.length;i++){var d=time-cuts[i],p=-1;if(d>-.1&&d<=0)p=(d+.1)/.1;else if(d>0&&d<.2)p=1-d/.2;if(p>=0){p=p*p*(3-2*p);env=Math.max(env,p);}}0.55*env";
}
writeLn("section cuts: "+total+" blends inside opening / cyberpunk, under the looks");
"""
with open(os.path.join(HERE, "..", "plugins", "launchSectionCuts.jsx"), "w", encoding="ascii", newline="\n") as fh:
    fh.write(JSX.replace("__DATA__", json.dumps(data)).replace("__FX__", json.dumps(fx)))
print("wrote plugins/launchSectionCuts.jsx")
