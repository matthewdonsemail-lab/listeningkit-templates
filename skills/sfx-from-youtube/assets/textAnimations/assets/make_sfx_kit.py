"""The launch film's sound effects (matt, 2026-11-16): free sound-effect videos found on YouTube with yt-dlp
(assets/sfx/raw/*.wav, ids in SOURCES below), each split into its separate sounds (an RMS envelope, gaps of 120 ms
of quiet), trimmed to the length the cue wants, faded at the end and normalised, into one folder per kind of cue:
assets/sfx/<kind>/NN.wav. Then writes plugins/sfxLay.jsx, which lays a clip on every cue in sfx_cues.csv (the
"sfx cues" markers), rotating through each kind's clips so repeats vary.
  python textAnimations/assets/make_sfx_kit.py"""
import csv
import json
import os
import shutil
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TA = os.path.normpath(os.path.join(HERE, ".."))
RAW = os.path.join(HERE, "sfx", "raw")
OUT = os.path.join(HERE, "sfx")
SOURCES = {"glitch_pack": "oys87TrYFbA", "glitch4": "ziI1z21LQ6o", "glitch_cine": "8zFB-ki2Gk4", "glitch_free": "CYcbnFL2HS4",
           "blip_ui": "9cNJyi8NtAw", "blip_text": "CbnHrtjMAeo", "whoosh_pack": "Hj7-pltIVng", "whoosh5": "qP_iJ-yLi7c",
           "static_burst": "dpC00rE6qfw", "static_pop": "NpcPLL60e8w", "vhs": "0GZ-td_LhgQ", "zap": "Zfcaj7M0Qnk",
           "zap_circuit": "MX3N550cq-0", "heartbeat": "9zw6eZEBp30", "sub_drop": "Yzq8c2Xv5IY", "bass_impact": "7DYBjzrhdWw",
           "riser": "Q8mYX1scq6I", "hit_cine": "fo-ULy4Ty08", "hit_sudden": "img8cqU6owQ", "scanner": "59igcK_WY3Y",
           "stutter": "Rz-ZDtDKLkM", "reverse": "_g4Wazm3cJc"}
# kind: (the sound text in the cue sheet, starts with) -> (sources, max seconds, gain dB)
KINDS = {
    "vhs_tick": ("tape glitch", ["vhs", "glitch_free"], 0.45, -8),
    "drop_impact": ("big sub impact", ["sub_drop"], 2.5, -2),
    "riser": ("riser", ["riser"], 1.1, -6),
    "glitch_stutter": ("digital glitch stutter", ["stutter", "glitch4"], 0.3, -9),
    "zap": ("electric zap", ["zap", "zap_circuit"], 0.6, -9),
    "glitch_burst": ("glitch burst", ["glitch_cine"], 0.6, -7),
    "glitch_whoosh": ("glitch whoosh", ["whoosh_pack", "glitch_pack"], 0.7, -9),
    "blip": ("digital blip", ["blip_ui", "blip_text"], 0.15, -14),
    "whoosh_glitch": ("whoosh + glitch", ["whoosh5", "glitch4"], 0.6, -10),
    "text_stab": ("glitch hit / text stab", ["glitch_pack"], 0.4, -8),
    "red_flash": ("electric tear", ["zap_circuit", "heartbeat"], 0.6, -6),
    "static_burst": ("static burst", ["static_burst", "static_pop"], 0.3, -9),
    "bass_hit": ("bass hit", ["bass_impact"], 1.2, -5),
    "reverse": ("reverse glitch", ["reverse"], 0.5, -9),
    "logo_hit": ("logo hit", ["hit_sudden", "hit_cine"], 3.0, -3),
    "thermal_sweep": ("thermal scan sweep", ["scanner"], 1.0, -6),
}


def read(path):
    w = wave.open(path); sr, ch = w.getframerate(), w.getnchannels()
    x = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, ch).astype(np.float32) / 32768
    return (x if ch == 2 else np.repeat(x, 2, 1)), sr


def segments(x, sr):
    hop = int(0.01 * sr)
    env = np.array([np.sqrt(np.mean(x[i:i + hop] ** 2)) for i in range(0, len(x) - hop, hop)])
    db = 20 * np.log10(env + 1e-9)
    on = db > db.max() - 32
    segs, start, quiet = [], None, 0
    for i, v in enumerate(on):
        if v:
            if start is None:
                start = i
            quiet = 0
        elif start is not None:
            quiet += 1
            if quiet >= 12:
                segs.append((start * hop, (i - quiet + 1) * hop)); start = None; quiet = 0
    if start is not None:
        segs.append((start * hop, len(x)))
    return [s for s in segs if s[1] - s[0] > 0.05 * sr]


def write(path, y, sr):
    o = wave.open(path, "wb"); o.setnchannels(2); o.setsampwidth(2); o.setframerate(sr)
    o.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes()); o.close()


import sys
clips = {}
LAY_ONLY = "--lay-only" in sys.argv          # the clips are already in assets/sfx/<kind>/ (make_sfx_from_music.py)
for kind, (_, srcs, mx, gain) in KINDS.items():
    if LAY_ONLY:
        d = os.path.join(OUT, kind)
        clips[kind] = sorted(os.path.join(d, f).replace("\\", "/") for f in os.listdir(d) if f.endswith(".wav")) if os.path.isdir(d) else []
        continue
    d = os.path.join(OUT, kind)
    if os.path.isdir(d):
        shutil.rmtree(d)
    os.makedirs(d)
    n = 0
    for s in srcs:
        x, sr = read(os.path.join(RAW, s + ".wav"))
        for a, b in segments(x, sr)[:8]:
            y = x[a:min(b, a + int(mx * sr))].copy()
            if kind == "riser":                                   # the riser: its last second, leading into the drop
                y = x[max(a, b - int(mx * sr)):b].copy()
            f = min(len(y), int(0.03 * sr)); y[-f:] *= np.linspace(1, 0, f)[:, None]
            y[: int(0.002 * sr)] *= np.linspace(0, 1, int(0.002 * sr))[:, None]
            y = y / (np.abs(y).max() + 1e-9) * (10 ** (gain / 20))
            n += 1
            write(os.path.join(d, "%02d.wav" % n), y, sr)
    clips[kind] = [os.path.join(d, "%02d.wav" % i).replace("\\", "/") for i in range(1, n + 1)]
    print(kind, n, "clips")

# the mix: each sound's level set against what the music and VO are doing under it, so it sits in the track
# instead of on top: the sound's RMS lands REL dB below the bed's RMS over the sound's length (the big moments
# closer, the ticks further down), never above -6 dB peak
REL = {"blip": -16, "vhs_tick": -12, "glitch_stutter": -18, "text_stab": -11, "static_burst": -12, "glitch_whoosh": -18,
       "whoosh_glitch": -12, "zap": -11, "glitch_burst": -10, "red_flash": -9, "reverse": -11, "riser": -8,
       "thermal_sweep": -10, "bass_hit": -6, "drop_impact": -4, "logo_hit": -6}
music, msr = read(os.path.join(HERE, "audio", "launch_music_outro.wav"))
VO = os.environ.get("SFX_VO_WAV")
bed = music.copy()
if VO and os.path.exists(VO):
    vo, _ = read(VO); n = min(len(bed), len(vo)); bed[:n] += vo[:n]


def rms(y):
    return float(np.sqrt(np.mean(y ** 2)) + 1e-9)


def level(kind, f, clip):
    y, sr = read(clip)
    a = int(f / 30 * msr); b = a + max(len(y), int(0.25 * msr))
    under = rms(bed[a:b]) if a < len(bed) else rms(bed[-msr:])
    want = under * 10 ** (REL[kind] / 20)
    g = 20 * np.log10(want / rms(y))
    peak = 20 * np.log10(np.abs(y).max() + 1e-9) + g
    return round(float(min(g, -6 - peak + g if peak > -6 else g)), 1)


# lay them on the cues
lay, used = [], {}
for row in csv.DictReader(open(os.path.join(TA, "sfx_cues.csv"), encoding="utf8")):
    kind = next((k for k, v in KINDS.items() if row["sound"].strip().startswith(v[0])), None)
    if not kind or not clips[kind]:
        continue
    i = used.get(kind, 0); used[kind] = i + 1
    f = int(row["frame"])
    if kind == "riser":
        f -= 30                                                    # it ends on the drop
    c = clips[kind][i % len(clips[kind])]
    lay.append([f, c, kind, level(kind, f, c)])
js = ["// GENERATED by assets/make_sfx_kit.py: a sound effect on every cue (sfx_cues.csv), as audio layers \"sfx <kind>\"",
      "// in the launch film (rerun replaces them). The clips are in assets/sfx/<kind>/.",
      "var LF=null;for(var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof CompItem && it.name===\"launch film\") LF=it;}",
      "for(var k=LF.numLayers;k>=1;k--) if(/^sfx /.test(LF.layer(k).name)) LF.layer(k).remove();",
      "var C=" + json.dumps(lay) + ", cache={};",
      "function imp(p){ if(cache[p]) return cache[p]; cache[p]=app.project.importFile(new ImportOptions(new File(p))); return cache[p]; }",
      "for(var i=0;i<C.length;i++){ var L=LF.layers.add(imp(C[i][1])); L.name=\"sfx \"+C[i][2]; L.startTime=C[i][0]/30; L.inPoint=C[i][0]/30; L.outPoint=Math.min(LF.duration, C[i][0]/30+L.source.duration); L.property(\"Audio\").property(\"Audio Levels\").setValue([C[i][3],C[i][3]]); L.moveToEnd(); }",
      "writeLn(\"sfx: \"+C.length+\" sounds laid\");"]
open(os.path.join(TA, "plugins", "sfxLay.jsx"), "w", encoding="utf8").write("\n".join(js) + "\n")
print(len(lay), "sounds laid")
