"""Break the reference trailer down: where the song sits under it, what sound design is laid on top, the dialogue,
and the cut rhythm. Writes trailer_map.json beside it and prints a timeline."""
import json
import subprocess
import sys

import numpy as np

SR, HOP, N = 22050, 512, 2048
HERE = sys.argv[1] if len(sys.argv) > 1 else "."


def load(p):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", p, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True).stdout
    return np.frombuffer(raw, np.float32)


def bands(x, nb=24):
    win = np.hanning(N).astype(np.float32)
    frames = np.lib.stride_tricks.sliding_window_view(x, N)[::HOP] * win
    mag = np.abs(np.fft.rfft(frames, axis=1))
    edges = np.unique(np.geomspace(2, mag.shape[1] - 1, nb + 1).astype(int))
    return np.stack([mag[:, a:b].mean(1) for a, b in zip(edges[:-1], edges[1:])], 1)


tr, so = load(HERE + "/trailer.wav"), load(HERE + "/song.wav")
bt, bs = bands(tr), bands(so)
lt, ls = np.log1p(bt * 50), np.log1p(bs * 50)
fps = SR / HOP


def z(a):
    a = a - a.mean(0)
    return a / (np.linalg.norm(a) + 1e-9)


# align: each 2 s window of the trailer against every offset in the song (correlation of the band envelopes)
W = int(2 * fps)
step = int(0.5 * fps)
song_n = len(ls)
F = 1 << int(np.ceil(np.log2(song_n + W)))
S = np.fft.rfft(ls - ls.mean(0), n=F, axis=0)
S2 = np.fft.rfft(np.square(ls - ls.mean(0)).sum(1), n=F)
align = []
for s0 in range(0, len(lt) - W, step):
    w = lt[s0:s0 + W] - lt[s0:s0 + W].mean(0)
    num = np.fft.irfft(np.conj(np.fft.rfft(w, n=F, axis=0)) * S, n=F, axis=0).sum(1)[:song_n - W]
    energy = np.fft.irfft(np.conj(np.fft.rfft(np.ones(W), n=F)) * S2, n=F)[:song_n - W]
    score = num / (np.linalg.norm(w) * np.sqrt(np.maximum(energy, 1e-9)))
    k = int(np.argmax(score))
    align.append((s0 / fps, k / fps, float(score[k])))

# sections: consecutive windows that keep the same trailer-to-song offset
sections = []
for t, st, sc in align:
    off = st - t
    if sc > 0.55 and sections and sections[-1]["kind"] == "song" and abs(sections[-1]["offset"] - off) < 0.3:
        sections[-1]["end"] = t + 2
        continue
    kind = "song" if sc > 0.55 else "other"
    if sections and sections[-1]["kind"] == kind == "other":
        sections[-1]["end"] = t + 2
        continue
    sections.append({"kind": kind, "start": t, "end": t + 2, "offset": off, "songAt": st, "score": sc})

# sound design on top: per frame, the trailer's level above what the mapped song explains (in dB), by register
lvl = lambda b: 20 * np.log10(b + 1e-6)
extra = np.zeros(len(bt))
lo, hi = slice(0, 8), slice(14, 24)
riser_hi = np.zeros(len(bt))
for sec in sections:
    a, b = int(sec["start"] * fps), min(int(sec["end"] * fps), len(bt))
    if sec["kind"] == "song":
        o = int(sec["offset"] * fps)
        idx = np.clip(np.arange(a, b) + o, 0, len(bs) - 1)
        gain = np.median(lvl(bt[a:b]) - lvl(bs[idx]))
        extra[a:b] = (lvl(bt[a:b]) - lvl(bs[idx]) - gain).clip(0).mean(1)
        riser_hi[a:b] = (lvl(bt[a:b, hi]) - lvl(bs[idx][:, hi]) - gain).mean(1)
    else:
        extra[a:b] = 12.0
        riser_hi[a:b] = lvl(bt[a:b, hi]).mean(1) - np.median(lvl(bt[:, hi]).mean(1))

flux = np.r_[0, np.maximum(np.diff(lt, axis=0), 0).sum(1)]
loud = lvl(bt).mean(1)
events = []
# impacts: big broadband onsets
thr = np.percentile(flux, 99.3)
last = -9
for i in np.nonzero(flux > thr)[0]:
    if i / fps - last > 0.35:
        events.append({"t": round(i / fps, 2), "kind": "impact", "flux": round(float(flux[i]), 1)})
        last = i / fps
# risers: high register climbing steadily for 1-5 s into a peak
sm = np.convolve(lvl(bt[:, hi]).mean(1), np.ones(9) / 9, "same")
i = 0
while i < len(sm) - int(fps):
    j = i
    while j + 1 < len(sm) and sm[j + 1] >= sm[j] - 0.15:
        j += 1
    if (j - i) / fps >= 1.0 and sm[j] - sm[i] > 10:
        events.append({"t": round(i / fps, 2), "kind": "riser", "len": round((j - i) / fps, 2),
                       "rise_db": round(float(sm[j] - sm[i]), 1)})
    i = j + 1
# glitch: fast stuttering flux (many sharp changes in under a second) in the high register
hf = np.r_[0, np.abs(np.diff(lt[:, hi], axis=0)).sum(1)]
g = np.convolve((hf > np.percentile(hf, 97)).astype(float), np.ones(int(fps * 0.5)), "same")
inside = False
for k in range(len(g)):
    if g[k] >= 6 and not inside:
        start, inside = k, True
    elif g[k] < 3 and inside:
        inside = False
        if (k - start) / fps > 0.25:
            events.append({"t": round(start / fps, 2), "kind": "glitch/stutter", "len": round((k - start) / fps, 2)})
events.sort(key=lambda e: e["t"])

cuts = [float(c) for c in open(HERE + "/cuts.txt").read().split()]

speech = []
try:
    from faster_whisper import WhisperModel
    model = WhisperModel("small", device="cpu", compute_type="int8")
    segs, _ = model.transcribe(HERE + "/trailer.wav", vad_filter=True, word_timestamps=False)
    speech = [{"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip()} for s in segs]
except Exception as e:  # noqa: BLE001
    speech = [{"error": str(e)[:200]}]

out = {"sections": sections, "events": events, "cuts": cuts, "speech": speech,
       "loudness_per_s": [round(float(loud[int(s * fps):int((s + 1) * fps)].mean()), 1) for s in range(int(len(loud) / fps))]}
json.dump(out, open(HERE + "/trailer_map.json", "w"), indent=1)
print("SECTIONS")
for s in sections:
    print("  %6.1f-%6.1f %-5s %s" % (s["start"], s["end"], s["kind"], "song @%.1f s" % s["songAt"] if s["kind"] == "song" else ""))
print("SPEECH")
for s in speech:
    print("  ", s)
print("EVENTS")
for e in events:
    print("  ", e)
print("CUTS/sec by 5 s:", [sum(1 for c in cuts if a <= c < a + 5) for a in range(0, int(len(tr) / SR), 5)])
