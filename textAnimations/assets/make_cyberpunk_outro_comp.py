"""The cyberpunk outro as EffectCraft pre-comps, built from layers (not one flat video).

Replays the outro's timeline from make_cyberpunk_outro.py (same shots, same seeded cut-ups) and writes:
  assets/collage/cyberpunk_outro_lines.mov   the glitched cyberpsycho lines alone, ProRes 4444 with alpha, the
                                             outro's full length (transparent where a shot has no lines)
  plugins/cyberpunkOutro.jsx                 the script that builds the comps (generated: edit this file, not it)

Comps (in the Project panel folder "cyberpunk outro parts"):
  cyberpunk outro       the whole outro: a black plate, each section below as a nested pre-comp, the lines on top
    outro flash         white, white, black, white solids
    outro logo          the Nous logo, white on black
    outro push          the 12 steps of the push into the girl in the logo, each its own pre-comp:
      outro push 00-11    that step's styled frame, the cut-up pieces from the other styles as masked image layers
                          (each piece is the other style's still, scaled to the same zoom, with a rectangle mask), and
                          on alternate steps the Nous logo at the same zoom for its match-cut frame
    outro back          the same 11 framings with her turned round
      outro back 00-10
    outro end           her background fading to black, then the busts fading up from black behind her while she
                        slides down, pushes in and Gaussian-blurs away; then the busts' slow zoom (plain keyframes)
    outro portraits     the six caricature portraits, each panning slowly, alternating
Comps are rebuilt in place (cleared and refilled, never deleted), so whatever nests them stays connected: after the
first build, cyberpunkEyes.jsx (which nests "cyberpunk outro" at the end of the cyberpunk comp) never needs rerunning.

To change one pre-comp, rebuild only that one (a rebuild replaces its layers, so any hand edits in it are lost):
  python assets/make_cyberpunk_outro_comp.py --only "outro end"      (or "outro push 03", "outro portraits"...)
  effectcraft-cli --project textAnimations.ecproj script plugins/cyberpunkOutro.jsx --save
--only skips the lines video (--no-lines skips it on a full build). A section name ("outro push") rebuilds that
section and all its steps; "cyberpunk outro" rebuilds only the top comp's nesting."""
import json
import math
import os
import subprocess
import sys

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_cyberpunk_outro as O  # noqa: E402  (importing loads the stills; it renders nothing)

ROOT = os.path.normpath(os.path.join(HERE, "..", "..")).replace("\\", "/") + "/"
CPR = "projects/cyberpunk/outro/"
W, H, FPS = O.W, O.H, O.FPS
LINES_OUT = os.path.join(HERE, "collage", "cyberpunk_outro_lines.mov")
JSX_OUT = os.path.join(HERE, "..", "plugins", "cyberpunkOutro.jsx")
ONLY = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None  # one pre-comp to rebuild
BLUR_PER_SIGMA = 2.0  # EffectCraft's Gaussian Blur "Blurriness" for one pixel of sigma


def size(rel):
    im = cv2.imread(ROOT + rel, cv2.IMREAD_UNCHANGED)
    return im.shape[1], im.shape[0]


def cover_tf(rel):
    """the cover fit of make_cyberpunk_outro.cover(): scale k and offset, so screen = k * pixel + off"""
    w, h = size(rel)
    k = max(W / w, H / h)
    rw, rh = int(w * k + 0.5), int(h * k + 0.5)
    return w, h, k, np.array([-((rw - W) // 2), -((rh - H) // 2)], np.float64)


def rel_of(pool, j):
    return CPR + ("front_%02d.png" if pool == "front" else "back_%02d.png") % j


def layer_rect(S, T, rect):
    """a screen rectangle (x, y, w, h) in the layer's own pixels, for its mask"""
    x, y, w, h = rect
    return [(x - T[0]) / S, (y - T[1]) / S, w / S, h / S]


def clip(rect, box):
    x0, y0 = max(rect[0], box[0]), max(rect[1], box[1])
    x1, y1 = min(rect[0] + rect[2], box[0] + box[2]), min(rect[1] + rect[3], box[1] + box[3])
    return None if x1 - x0 < 2 or y1 - y0 < 2 else [x0, y0, x1 - x0, y1 - y0]


def pieces(i, pool, frame_patches):
    """the cut-up pieces on step i, as make_cyberpunk_outro.collage() places them: one layer spec per piece"""
    out = []
    for pid, patch_ in frame_patches:
        if patch_[0] == "screen":
            _, fx, fy, fw, fh, j, br = patch_
            if j == i:
                continue
            a = O.K[i] / O.K[j]
            b = O.B[i] - a * O.B[j]
            pw, ph = int(fw * W), int(fh * H)
            px, py = int(fx * (W - pw)), int(fy * (H - ph))
            rect = [px, py, pw, ph]
            kind = "cut"
        else:
            j, cx, cy, w, h, z, br, ox, oy = patch_
            if j == i:
                continue
            a = O.K[i] / O.K[j]
            b0 = O.B[i] - a * O.B[j]
            k = O.K[i]
            X, Y = k * (cx + ox) + O.B[i][0], k * (cy + oy) + O.B[i][1]
            pw, ph = int(k * w), int(k * h)
            if pw < 8 or ph < 8 or pw >= W or ph >= H:
                continue
            sx, sy = k * cx + O.B[i][0], k * cy + O.B[i][1]
            sw, sh = pw / z, ph / z
            x0, y0 = int(np.clip(sx - sw / 2, 0, W - sw)), int(np.clip(sy - sh / 2, 0, H - sh))
            if int(sw) <= 0 or int(sh) <= 0:
                continue
            zx = pw / int(sw)
            px, py = int(np.clip(X - pw / 2, 0, W - pw)), int(np.clip(Y - ph / 2, 0, H - ph))
            # screen = zx * (warped - (x0, y0)) + (px, py), warped = a * cover + b0
            a, b = zx * a, zx * (b0 - np.array([x0, y0])) + np.array([px, py])
            rect = [px, py, pw, ph]
            kind = "feature"
        rel = rel_of(pool, j)
        _, _, kc, off = cover_tf(rel)
        S, T = a * kc, a * off + b
        # the still was cropped to the frame before it was warped: clip the piece to what that crop covers
        crop_box = [b[0], b[1], a * W, a * H]
        r = clip(rect, crop_box)
        if r is None:
            continue
        out.append({"id": pid, "name": "%s %02d (%s %02d)" % (kind, pid, pool, j), "p": rel, "s": S * 100,
                    "x": T[0], "y": T[1], "mask": layer_rect(S, T, r),
                    "exp": round(math.log2(br), 4) if br != 1 else 0})
    return out


# replay the timeline: the same seeded cut-ups the flat render makes, frame by frame
seq = O.seq
patches, frame_patches, pid = [], {}, 0
for f, (kind, i, t) in enumerate(seq):
    if kind in ("collage", "bcollage"):
        if f % 2 == 0:
            new = [O.new_patch("strip") for _ in range(int(O.crng.integers(2, 4)))]
            new += [O.new_patch("feature") for _ in range(int(O.crng.integers(1, 3)))]
            for p_ in new:
                patches.append((pid, p_))
                pid += 1
            patches = patches[-12:]
        frame_patches[f] = list(patches)

# sections, in outro frames
starts, f = {}, 0
for f, (kind, i, t) in enumerate(seq):
    sec = {"flash": "flash", "logo": "logo", "front": "push", "collage": "push", "logo_at": "push", "back": "back",
           "bcollage": "back", "bgfade": "end", "reveal": "end", "busts": "end", "portrait": "portraits"}[kind]
    starts.setdefault(sec, [f, f])
    starts[sec][1] = f + 1


def steps(section, base_kind, cut_kind, pool):
    """each step of the push (or of the back) as a pre-comp: its frame, the pieces, the logo match-cut frame"""
    s0 = starts[section][0]
    out = {}
    for f, (kind, i, t) in enumerate(seq):
        if kind not in (base_kind, cut_kind, "logo_at") or not (starts[section][0] <= f < starts[section][1]):
            continue
        st = out.setdefault(i, {"name": "outro %s %02d" % (section, i), "start": f - s0, "frames": 0,
                                "base": rel_of(pool, i), "pieces": [], "logo_at": None})
        local = f - s0 - st["start"]
        st["frames"] = local + 1
        if kind == "logo_at":
            st["logo_at"] = local
        elif kind == cut_kind:
            for sp in pieces(i, pool, frame_patches[f]):
                last = st["pieces"][-1] if st["pieces"] else None
                prev = next((q for q in st["pieces"] if q["id"] == sp["id"] and q["out"] == local), None)
                if prev:
                    prev["out"] = local + 1
                else:
                    sp["in"], sp["out"] = local, local + 1
                    st["pieces"].append(sp)
    for st in out.values():
        st["pieces"].sort(key=lambda q: q["id"])  # older pieces under newer ones, as the collage piles them up
        bw, bh, bk, boff = cover_tf(st["base"])
        st["bs"], st["bx"], st["by"] = bk * 100, boff[0], boff[1]
    return [out[i] for i in sorted(out)]


def cover_spec(rel, extra=1.0):
    w, h, k, off = cover_tf(rel)
    return {"p": rel, "s": k * 100 * extra, "ax": w / 2, "ay": h / 2}


lw_logo = O.lw
logo_rel = "textAnimations/assets/endcard/nous_logo_white.png"
lgw, lgh = size(logo_rel)
# the top comp laid out on matt's VO (projects/cyberpunk/audio.mp3; the outro starts on "introducing", 23.70 s):
# the flash, then the push and the back of her stretched over "introducing log by listeningkit in collaboration with",
# the Nous logo on "nous research" (27.52 s), the busts on "you are someone different" (28.34 s), the portraits
# stretched to the end of "win more deals" (37.44 s). (comp, at frame, stretch %)
VO_AT = {"logo": 115, "end": 139, "stop": 412}
MENTAL = VO_AT["logo"] - 4
LAYOUT = [["outro flash", 0, 100.0], ["outro push", 4, 100.0 * MENTAL / 76],
          ["outro back", 4 + 42 * MENTAL / 76, 100.0 * MENTAL / 76], ["outro logo", VO_AT["logo"], 100.0],
          ["outro end", VO_AT["end"], 100.0],
          ["outro portraits", VO_AT["end"] + 72, 100.0 * (VO_AT["stop"] - VO_AT["end"] - 72) / 180]]
data = {
    "layout": LAYOUT, "topFrames": VO_AT["stop"], "mental": [4, VO_AT["logo"], 100.0 * MENTAL / 76],
    "root": ROOT, "fps": FPS, "frames": len(seq), "blurPerSigma": BLUR_PER_SIGMA,
    "sections": {k: v for k, v in starts.items()},
    "logo": {"p": logo_rel, "s": O.LOGO_H / lgh * 100, "x": float(O.LX), "y": float(O.LY)},
    "zoomrefs": [dict(zip(("s", "x", "y"), (cover_tf(CPR + "zoomref/zoom_%02d.png" % i)[2] * 100,
                                             *cover_tf(CPR + "zoomref/zoom_%02d.png" % i)[3]))) | {"p": CPR + "zoomref/zoom_%02d.png" % i}
                 for i in range(12)],
    "push": steps("push", "front", "collage", "front"),
    "back": steps("back", "back", "bcollage", "back"),
    "end": {"bg": cover_spec(CPR + "back_11.png"), "girl": cover_spec(CPR + "back_11_girl.png"),
            "busts": cover_spec(CPR + "ensemble.png"), "bgFade": O.BG_FADE, "reveal": O.REVEAL, "busts_n": O.BUSTS,
            "bustsIn": O.BUSTS_IN},
    "portraits": [cover_spec(CPR + "portrait_%d.png" % i, 1.08) for i in range(6)], "portraitFrames": O.PORTRAIT,
    "lines": "textAnimations/assets/collage/cyberpunk_outro_lines.mov",
}


def js_num(o):
    if isinstance(o, dict):
        return {k: js_num(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [js_num(v) for v in o]
    if isinstance(o, (float, np.floating)):
        return round(float(o), 3)
    if isinstance(o, np.integer):
        return int(o)
    return o


JSX = r"""// GENERATED by assets/make_cyberpunk_outro_comp.py: edit that script and rerun it, not this file.
// Builds the cyberpunk outro as pre-comps from layers (see the script's docstring for the comp tree), in the
// Project panel folder "cyberpunk outro parts". The first build: then run cyberpunkEyes.jsx to nest it in cyberpunk.
// ONLY (set by the script's --only) rebuilds just that one pre-comp, in place; null rebuilds them all, in place.
var D = __DATA__;
var ONLY = __ONLY__;
function want(n){ return ONLY===null || ONLY===n; }
var F = D.fps, ROOT = D.root;
function findFile(path){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof FootageItem && it.file && it.file.fsName.replace(/\\/g,"/").toLowerCase()===path.toLowerCase()) return it;} return null; }
var seen={};
function foot(rel){ var p=ROOT+rel; if(seen[p]) return seen[p]; var it=findFile(p); if(it) it.replace(new File(p)); else it=app.project.importFile(new ImportOptions(new File(p))); seen[p]=it; return it; }
function P(e,path){ var s=path.split("/"); var p=e; for(var i=0;i<s.length;i++){ p=p.property(s[i]); if(!p) throw new Error("no "+path); } return p; }
// an earlier build's folder was named "cyberpunk outro" and took that name from the comp: drop it
for (var i=app.project.numItems;i>=1;i--){ var it=app.project.item(i); if(it instanceof FolderItem && it.name==="cyberpunk outro" && it.numItems===0) it.remove(); }
var FOLDER=null; for (var i=1;i<=app.project.numItems;i++){ var it=app.project.item(i); if(it instanceof FolderItem && it.name==="cyberpunk outro parts") FOLDER=it; }
if(!FOLDER) FOLDER=app.project.items.addFolder("cyberpunk outro parts");
// a comp by name, rebuilt in place: an existing one is emptied and kept (so the comps nesting it stay connected)
function comp(name,frames){
  for (var i=1;i<=app.project.numItems;i++){ var it=app.project.item(i);
    if(it instanceof CompItem && it.name===name){ for (var k=it.numLayers;k>=1;k--) it.layer(k).remove(); it.duration=frames/F; return it; } }
  var c=app.project.items.addComp(name,1920,1080,1,frames/F,F); c.parentFolder=FOLDER; return c; }
function span(L,a,b){ L.startTime=0; L.inPoint=a/F; L.outPoint=b/F; }
// a still, its top-left at (x, y), scaled s%; optional rectangle mask in its own pixels and exposure in stops
function still(c,name,rel,s,x,y,a,b,mask,exp){
  var L=c.layers.add(foot(rel)); L.name=name; span(L,a,b);
  var tr=L.property("Transform"); tr.property("Anchor Point").setValue([0,0]); tr.property("Position").setValue([x,y]); tr.property("Scale").setValue([s,s]);
  if(mask){ var m=L.Masks.addProperty("Mask"), sh=new Shape(); var X=mask[0],Y=mask[1],W=mask[2],H=mask[3];
    sh.vertices=[[X,Y],[X+W,Y],[X+W,Y+H],[X,Y+H]]; sh.closed=true; m.property("ADBE Mask Shape").setValue(sh); }
  if(exp){ var e=L.property("Effects").addProperty("ec.color.exposure"); P(e,"Master/Exposure").setValue(exp);
    try{ e.property("Bypass Linear Light Conversion").setValue(1); }catch(x){} }
  return L;
}
// a still centred in the frame, scaled s%, for the expression-driven shots
function centred(c,name,sp,a,b){ var L=c.layers.add(foot(sp.p)); L.name=name; span(L,a,b);
  var tr=L.property("Transform"); tr.property("Anchor Point").setValue([sp.ax,sp.ay]); tr.property("Position").setValue([960,540]); tr.property("Scale").setValue([sp.s,sp.s]); return L; }
function nest(parent,child,name,at){ var L=parent.layers.add(child); L.name=name; L.startTime=at/F; L.inPoint=at/F; L.outPoint=(at+child.duration*F)/F; return L; }
function sec(n){ return D.sections[n]; }
function compNamed(n){ for (var i=1;i<=app.project.numItems;i++){ var it=app.project.item(i); if(it instanceof CompItem && it.name===n) return it; } throw new Error("no comp "+n); }
var FR="var fr=Math.round(time*"+F+");";


// flash: white, white, black, white
if(want("outro flash")){
var FL=comp("outro flash",sec("flash")[1]-sec("flash")[0]);
var w1=FL.layers.addSolid([1,1,1],"white",1920,1080,1); span(w1,0,2);
var w2=FL.layers.addSolid([1,1,1],"white 2",1920,1080,1); span(w2,3,4);
}

// the Nous logo, white on black
if(want("outro logo")){
var LG=comp("outro logo",sec("logo")[1]-sec("logo")[0]);
still(LG,"nous logo",D.logo.p,D.logo.s,D.logo.x,D.logo.y,0,LG.duration*F);
}

// the push and the back of her: one pre-comp per step (ONLY a step's name rebuilds just that step)
function stepComps(list,parentName,secName){
  var all=want(parentName), PC=all?comp(parentName,sec(secName)[1]-sec(secName)[0]):null;
  for (var i=0;i<list.length;i++){ var st=list[i]; if(!all && !want(st.name)) continue; var c=comp(st.name,st.frames);
    still(c,st.name.replace("outro ",""),st.base,st.bs,st.bx,st.by,0,st.frames);
    for (var k=0;k<st.pieces.length;k++){ var q=st.pieces[k]; still(c,q.name,q.p,q.s,q.x,q.y,q["in"],q.out,q.mask,q.exp); }
    if(st.logo_at!==null){ var z=D.zoomrefs[parseInt(st.name.slice(-2),10)]; still(c,"nous logo at this zoom",z.p,z.s,z.x,z.y,st.logo_at,st.logo_at+1); }
    if(PC) nest(PC,c,st.name,st.start); }
  return PC;
}
var PU=stepComps(D.push,"outro push","push");
var BA=stepComps(D.back,"outro back","back");

// the end: her background fades to black; the busts fade up from black behind her while she slides down, pushes in
// and blurs away; then the busts' slow zoom. Plain keyframes (no expressions), to edit by hand: extra keys in between
// trace the eases (her slide drops away slowly then fast, the blur grows faster towards the end)
var E=D.end, B0=E.bgFade, R=E.reveal, N=E.busts_n, RE=B0+R-1;
function keys(prop,list){ for (var k=0;k<list.length;k++) prop.setValueAtTime(list[k][0]/F,list[k][1]); }
function sc(s,z){ return [s*z,s*z]; }
if(want("outro end")){
var EN=comp("outro end",B0+R+N);
var bu=centred(EN,"busts",E.busts,B0,B0+R+N), bs=E.busts.s, z0=E.bustsIn;
keys(bu.property("Transform").property("Scale"),[[B0,sc(bs,z0)],[RE,sc(bs,z0+0.02)],[B0+R+N-1,sc(bs,z0+0.10)]]);
var bo=Math.round(B0+0.85*(R-1));
keys(bu.property("Transform").property("Opacity"),[[B0,0],[Math.round((B0+bo)/2),50],[bo,100]]);
var bg=centred(EN,"her background",E.bg,0,B0);
keys(bg.property("Transform").property("Scale"),[[0,sc(E.bg.s,1)],[B0-1,sc(E.bg.s,1.02)]]);
keys(bg.property("Transform").property("Opacity"),[[0,100],[B0-1,0]]);
var gi=centred(EN,"her",E.girl,0,B0+R), gs=E.girl.s;
keys(gi.property("Transform").property("Scale"),[[0,sc(gs,1)],[B0-1,sc(gs,1.02)],[RE,sc(gs,1.20)]]);
var g0=Math.round(B0+0.15*(R-1)), gpos=[];
for (var e=0;e<=4;e++){ var u=e/4; gpos.push([Math.round(g0+u*(RE-g0)),[960,540+1080*1.05*u*u*u]]); }
keys(gi.property("Transform").property("Position"),[[0,[960,540]]].concat(gpos));
var gb=gi.property("Effects").addProperty("ec.blur.gaussian");
try{ gb.property("Repeat Edge Pixels").setValue(0); }catch(x){}
var bl=[[B0-1,0]];
for (var e=0;e<=4;e++){ var t=e/4; bl.push([Math.round(B0+t*(R-1)),D.blurPerSigma*(0.5+18*Math.pow(t,1.5))]); }
keys(gb.property("Blurriness"),bl);
}

// the six caricature portraits, each panning slowly, alternating right and left
if(want("outro portraits")){
var PF=D.portraitFrames, PO=comp("outro portraits",PF*D.portraits.length);
for (var i=0;i<D.portraits.length;i++){ var L=centred(PO,"portrait "+i,D.portraits[i],i*PF,(i+1)*PF);
  L.property("Transform").property("Position").expression=FR+"var t=(fr-"+(i*PF)+")/"+(PF-1)+";[960+"+(i%2===0?1:-1)+"*(-45+90*t),540]"; }
}

// the top comp: a black plate, the sections nested in order, the lines on top
if(want("cyberpunk outro")){
var TOP=comp("cyberpunk outro",D.topFrames);
var BL=TOP.layers.addSolid([0,0,0],"black",1920,1080,1); span(BL,0,D.topFrames);
// each section where the VO puts it, stretched to fit (D.layout: comp, at frame, stretch %)
function place(src,name,at,st,a,b){ var L=TOP.layers.add(src); L.name=name; L.stretch=st; L.startTime=at/F;
  L.inPoint=(a===undefined?at:a)/F; L.outPoint=(b===undefined?at+src.duration*F*st/100:b)/F; return L; }
for (var i=0;i<D.layout.length;i++) place(compNamed(D.layout[i][0]),D.layout[i][0],D.layout[i][1],D.layout[i][2]);
// the lines video follows the original order (logo, push, back), so it goes in twice: under the logo, and stretched
// under the push and the back
var lf=foot(D.lines), M=D.mental, ls=sec("logo")[0], ps=sec("push")[0];
place(lf,"cyberpsycho lines (logo)",D.layout[3][1]-ls,100,D.layout[3][1],D.layout[3][1]+24);
place(lf,"cyberpsycho lines (push and back)",M[0]-ps*M[2]/100,M[2],M[0],M[1]);
}
writeLn("cyberpunk outro: rebuilt "+(ONLY===null?"every pre-comp":"'"+ONLY+"'")+", in place");
"""

with open(JSX_OUT, "w", encoding="ascii", newline="\n") as fh:
    fh.write(JSX.replace("__DATA__", json.dumps(js_num(data), ensure_ascii=True)).replace("__ONLY__", json.dumps(ONLY)))
print("wrote", os.path.normpath(JSX_OUT))

if "--no-lines" not in sys.argv and ONLY is None:
    # the lines alone, with alpha, over the shots that have them (the same seeds as the flat render)
    logo_matte = cv2.dilate((O.logo_a > 0.5).astype(np.uint8) * 255, np.ones((25, 25), np.uint8))
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", "%dx%d" % (W, H),
                          "-r", str(FPS), "-i", "-", "-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", "yuva444p10le",
                          LINES_OUT], stdin=subprocess.PIPE)
    empty = np.zeros((H, W, 4), np.uint8)
    names = {"logo": "outro logo", "front": "outro front", "collage": "outro collage", "back": "outro back",
             "bcollage": "outro bcollage"}
    for f, (kind, i, t) in enumerate(seq):
        on2 = f - f % 2
        if kind in names:
            lines = O.cyberpsycho.frame("%s %d" % (names[kind], on2), (W, H), logo_matte if kind == "logo" else None,
                                        (225, 240, 255), 0.5, outline=(0, 0, 0), outline_px=2)
            p.stdin.write(np.ascontiguousarray(O.cyberpsycho.glitch(lines, "%s %d" % (names[kind], on2), 1.0)).tobytes())
        else:
            p.stdin.write(empty.tobytes())
    p.stdin.close()
    p.wait()
    print("lines ->", os.path.normpath(LINES_OUT))
