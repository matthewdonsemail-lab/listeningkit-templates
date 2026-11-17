"""Sound-effect cues for the launch film (matt, 2026-11-16): every cut and effect beat, with the kind of sound it wants,
so a sound-effect pack can be laid in. Reads the film's cuts from plugins/launchSectionCuts.jsx (opening, cyberpunk)
and the ending's layers from the project (card changes, transitions, red flashes, girl flash cuts, giant words,
the end card).
Writes
  textAnimations/SFX_CUES.md          the cue sheet (time, frame, what happens, the sound), by section
  textAnimations/sfx_cues.csv         the same as a table
  textAnimations/plugins/sfxCues.jsx  puts every cue as a marker (labelled with the sound) on a "sfx cues" null
                                      in "launch film", so they show on the timeline
  python textAnimations/assets/make_sfx_cues.py --project <the .ecproj>"""
import argparse
import json
import os
import re
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
TA = os.path.normpath(os.path.join(HERE, ".."))
CLI = "C:/Program Files/ArtCraft/EffectCraft/effectcraft-cli.exe"
F = 30
CYBER_AT, ENDING_AT = 263, 1123       # where the sections sit in the launch film (frames)

ap = argparse.ArgumentParser()
ap.add_argument("--project", required=True)
a = ap.parse_args()

cues = []


def cue(f, sec, what, sound):
    cues.append((int(f), sec, what, sound))


# opening and cyberpunk, from the section cuts
s = open(os.path.join(TA, "plugins", "launchSectionCuts.jsx"), encoding="utf8").read()
D = json.loads(re.search(r"var D=(\{.*?\}), FX=", s).group(1))
for c in D["opening"]:
    f = c["cut"]
    if f < 308:
        cue(f, "opening", "shot cut (VHS, clip blend)", "tape glitch / VHS cut tick")
    elif f == 308:
        cue(f, "opening", "THE DROP: into the cyberpsycho, thermogram", "big sub impact + riser end + distorted hit")
    else:
        cue(f, "opening", "cyberpsycho swap between the two men", "digital glitch stutter (short, punchy)")
cue(308 - 30, "opening", "build to the drop", "riser starts (1 s)")
busts = [659, 693, 727, 760, 794, 827]
for c in D["cyberpunk"]:
    f, ff = c["cut"], c["cut"] + CYBER_AT
    if f in busts:
        cue(ff, "cyberpunk", "next bust: line wipes round him", "electric zap / line whoosh")
        cue(ff + 17, "cyberpunk", "bust apex: face glitch, eye echoes", "glitch burst + data crunch")
    elif f < 265:
        cue(ff, "cyberpunk", "match-cut flow", "glitch whoosh")
    elif f < 448:
        cue(ff, "cyberpunk", "close-up style switch", "digital blip / UI tick")
    else:
        cue(ff, "cyberpunk", "outro cut", "whoosh + glitch")

# the ending, from the project
DUMP = r"""var C;for(var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof CompItem && it.name==="ending") C=it;}
var o=[], st={};
for(var k=1;k<=C.numLayers;k++){var L=C.layer(k), n=L.name, a=Math.round(L.inPoint*30), b=Math.round(L.outPoint*30);
 if(/^cap /.test(n)){ if(!st[a]){ st[a]=1; o.push('["card",'+a+','+b+',"'+L.property("Source Text").value.text.replace(/"/g,"")+'"]'); } }
 else if(/^end trans /.test(n)) o.push('["trans",'+a+','+b+',"'+n+'"]');
 else if(/^insert /.test(n)) o.push('["insert",'+a+','+b+',""]');
 else if(/^giant \d+ fill/.test(n)) o.push('["giant",'+a+','+b+',""]');
 else if(n==="ending card") o.push('["endcard",'+a+','+b+',""]'); }
writeLn("EV ["+o.join(",")+"]");"""
tmp = os.path.join(TA, "_sfx_dump.jsx"); open(tmp, "w").write(DUMP)
r = subprocess.run([CLI, "--project", a.project, "script", tmp], capture_output=True, text=True)
os.remove(tmp)
ev = json.loads(next(l for l in r.stdout.splitlines() if l.startswith("EV "))[3:])
for kind, s0, s1, txt in sorted(ev, key=lambda e: e[1]):
    f = s0 + ENDING_AT
    if kind == "card":
        cue(f, "ending", "card: \"%s\" lands, text glitch" % txt.strip(), "glitch hit / text stab (vary pitch per card)")
    elif kind == "trans" and "redflash" in txt:
        cue(f, "ending", "red flash transition (Edgerunners 2)", "electric tear + heartbeat thump")
    elif kind == "trans":
        cue(f, "ending", "clip-blend transition, pixel sort", "glitch whoosh")
    elif kind == "insert":
        cue(f, "ending", "flash cut to the girl, eye echoes, thermogram", "static burst / shutter + thermal scan")
    elif kind == "giant":
        cue(f, "ending", "giant full-screen word, cracks", "bass hit + whoosh")
        cue(s1 + ENDING_AT, "ending", "giant word glitches back", "reverse glitch")
    elif kind == "endcard":
        cue(f, "ending", "END CARD: Nous + Log", "logo hit with a long reverb tail")
cue(ENDING_AT, "ending", "into the ending, thermogram", "thermal scan sweep + impact")

cues.sort()
tc = lambda f: "%d:%05.2f" % (f // (60 * F), (f % (60 * F)) / F)
with open(os.path.join(TA, "SFX_CUES.md"), "w", encoding="utf8") as fh:
    fh.write("# Launch film: sound effect cues\n\n%d cues, launch film time (30 fps). Same cues as markers on the "
             "\"sfx cues\" layer in the launch film (plugins/sfxCues.jsx).\n" % len(cues))
    sec = None
    for f, s_, what, sound in cues:
        if s_ != sec:
            sec = s_; fh.write("\n## %s\n\n| time | frame | what happens | sound |\n|---|---|---|---|\n" % s_)
        fh.write("| %s | %d | %s | %s |\n" % (tc(f), f, what, sound))
with open(os.path.join(TA, "sfx_cues.csv"), "w", encoding="utf8") as fh:
    fh.write("time,frame,section,what,sound\n")
    for f, s_, what, sound in cues:
        fh.write('%s,%d,%s,"%s","%s"\n' % (tc(f), f, s_, what.replace('"', "'"), sound))
js = ["// GENERATED by assets/make_sfx_cues.py: the sound-effect cues as markers on a \"sfx cues\" null in the launch",
      "// film (rerun replaces it). The full list is SFX_CUES.md.",
      "var LF=null;for(var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof CompItem && it.name===\"launch film\") LF=it;}",
      "for(var k=LF.numLayers;k>=1;k--) if(LF.layer(k).name===\"sfx cues\") LF.layer(k).remove();",
      "var N=LF.layers.addNull(); N.name=\"sfx cues\"; N.startTime=0; N.inPoint=0; N.outPoint=LF.duration; var M=N.property(\"Marker\");",
      "var C=" + json.dumps([[f, sound + "  (" + what + ")"] for f, s_, what, sound in cues]) + ";",
      "for(var i=0;i<C.length;i++) M.setValueAtTime(C[i][0]/30, new MarkerValue(C[i][1]));",
      "writeLn(\"sfx cues: \"+C.length+\" markers\");"]
open(os.path.join(TA, "plugins", "sfxCues.jsx"), "w", encoding="utf8").write("\n".join(js) + "\n")
print(len(cues), "cues")
