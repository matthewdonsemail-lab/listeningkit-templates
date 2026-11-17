"""The launch film's sound effects taken from its own music (matt, 2026-11-16: the YouTube ones didn't belong). The
music bed is cut from the Edgerunners 2 trailer's soundtrack (make_launch_sound_trailer.py), so its sound design is
the trailer's: this pulls the trailer's own hits, risers and cut sounds out of projects/opening/ref/trailer_nodialogue.wav
(the trailer with the dialogue taken out):
  impacts   at the trailer's measured impact events (trailer_map.json "impact"): 1.2 s (bass_hit), 2.5 s (drop_impact),
            3 s (logo_hit), from just before the hit
  risers    at its "riser" events: the second before each one peaks
  cut sounds at every cut in the trailer (cuts.txt): a slice round the cut, sorted by how bright and how noisy it is
            (spectral centroid, spectral flatness) into the short bright ticks (blip, vhs_tick, glitch_stutter,
            text_stab), the noisy ones (static_burst, glitch_burst, zap, red_flash) and the longer swept ones
            (glitch_whoosh, whoosh_glitch, thermal_sweep); reverse = swept ones played backwards
Writes the clips into assets/sfx/<kind>/NN.wav (replacing what's there); then
  SFX_VO_WAV=<vo.wav> python textAnimations/assets/make_sfx_kit.py --lay-only   sets the levels and lays them.
  python textAnimations/assets/make_sfx_from_music.py"""
import json
import os
import shutil
import subprocess

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.normpath(os.path.join(HERE, "..", "..", "projects", "opening", "ref"))
OUT = os.path.join(HERE, "sfx")
SR = 48000

raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", os.path.join(REF, "trailer_nodialogue.wav"), "-ac", "2",
                      "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
x = np.frombuffer(raw, np.float32).reshape(-1, 2)
tmap = json.load(open(os.path.join(REF, "trailer_map.json")))
cuts = [float(v) for v in open(os.path.join(REF, "cuts.txt")).read().split()]


def sl(t0, d):
    a, b = max(0, int(t0 * SR)), min(len(x), int((t0 + d) * SR))
    y = x[a:b].copy()
    e = min(len(y) // 4, int(0.004 * SR)); y[:e] *= np.linspace(0, 1, e)[:, None]
    f = min(len(y) // 3, int(0.04 * SR)); y[-f:] *= np.linspace(1, 0, f)[:, None]
    return y / (np.abs(y).max() + 1e-9) * 0.7


def feats(y):
    m = y.mean(1); sp = np.abs(np.fft.rfft(m * np.hanning(len(m)))) + 1e-9
    fr = np.fft.rfftfreq(len(m), 1 / SR)
    return float((sp * fr).sum() / sp.sum()), float(np.exp(np.log(sp).mean()) / sp.mean())


def write(kind, ys):
    d = os.path.join(OUT, kind)
    if os.path.isdir(d):
        shutil.rmtree(d)
    os.makedirs(d)
    import wave
    for i, y in enumerate(ys):
        o = wave.open(os.path.join(d, "%02d.wav" % (i + 1)), "wb"); o.setnchannels(2); o.setsampwidth(2); o.setframerate(SR)
        o.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes()); o.close()
    print(kind, len(ys))


imp = sorted([e for e in tmap["events"] if e["kind"] == "impact"], key=lambda e: -e.get("flux", 0))
ris = [e for e in tmap["events"] if e["kind"] == "riser"]
write("bass_hit", [sl(e["t"] - 0.03, 1.2) for e in imp[:6]])
write("drop_impact", [sl(e["t"] - 0.03, 2.5) for e in imp[:2]])
write("logo_hit", [sl(e["t"] - 0.03, 3.0) for e in imp[:3]])
write("riser", [sl(e["t"] + e["len"] - 1.1, 1.1) for e in ris])

short, noisy, swept = [], [], []
for c in cuts:
    s = sl(c - 0.04, 0.3); cen, flat = feats(s)
    w = sl(c - 0.3, 0.8)
    short.append((cen, s)); noisy.append((flat, s)); swept.append((cen, w))
short.sort(key=lambda v: -v[0]); noisy.sort(key=lambda v: -v[0])
sh = [v[1] for v in short]; no = [v[1] for v in noisy]; sw = [v[1] for v in swept]
write("blip", [y[: int(0.15 * SR)] for y in sh[:8]])
write("vhs_tick", [y[: int(0.4 * SR)] for y in sh[8:16]])
# the stutter and the glitch whoosh (matt: the first ones rose, which fought the picture): only slices that start on
# their hit and decay (envelope falling from the first 50 ms to the last), never a build
def decay(y):
    m = np.abs(y).mean(1); n = len(m) // 4
    return float(m[:n].mean() / (m[-n:].mean() + 1e-9))
falling = sorted([sl(c, 0.35) for c in cuts], key=lambda y: -decay(y))
write("glitch_stutter", [np.concatenate([y[: int(0.045 * SR)], y[: int(0.045 * SR)] * 0.7, y[: int(0.09 * SR)] * 0.5]) for y in falling[:8]])
write("text_stab", sh[24:32])
write("static_burst", no[:10])
write("glitch_burst", [sl(c - 0.05, 0.6) for c in cuts[::7][:8]])
write("zap", no[10:16])
write("red_flash", no[16:24])
write("glitch_whoosh", falling[8:24])
write("whoosh_glitch", sw[16:28])
write("thermal_sweep", [sl(e["t"] + e["len"] - 1.0, 1.0) for e in ris[:1]])
write("reverse", [y[::-1].copy() for y in sw[28:32]])
