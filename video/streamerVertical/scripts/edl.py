"""Plan the cut (EDL) for a vertical streamer clip, per matt's awesome-video-editing guides
(filmcraft/examples/pacing, jcut, audio).

    uv run --no-project --with numpy python edl.py --dir DIR --ranges "SRC:0,19.24;SRC:19.89,38.47;OTHER:0,8.3"

DIR holds <SRC>.mp4 and assembly_<SRC>.json (transcribe.py) for every source named in --ranges.
--ranges = the source spans to keep, in order. Writes DIR/edl.json and prints the beat list.

How it works
1. Loudness envelope: the source audio as 16 kHz mono, RMS in 10 ms frames, in dBFS (a <SRC>.pcm
   cache is made with ffmpeg the first time).
2. Beats: the kept words are split at sentence ends with a >= 0.10 s gap, at any gap >= 0.25 s, and at
   range boundaries. A beat shorter than 1.0 s merges into the next when the gap is under 0.5 s
   (longer gaps are dead air and stay cut).
3. Edges: each beat's in/out snaps to the quiet instant (>= 12 dB under that beat's median speech
   level) nearest its first/last word within 0.25 s, then 0.04 s further out, so no word is clipped and
   no breath is left hanging. Adjacent beats in one range never replay source (overlaps meet midway).
4. J-cuts: the outgoing line's tail is measured (time after it last comes within 6 dB of its speech
   level). The next beat starts over that tail: 3 frames at the cold open, up to 6 in the body,
   capped by the tail and by 1/3 of the beat. In EffectCraft the OUTGOING layer stays on top, so
   the picture cuts late while the next voice already leads.
Output per beat: src, sin/sout (source seconds), T (comp start), overlap_frames, words, wtimes.
"""
import json, os, subprocess, sys, numpy as np

def _arg(n):
    return sys.argv[sys.argv.index(n) + 1]

DIR = os.path.join(_arg("--dir"), "")
FPS = 30
# (source, keep-from s, keep-to s): spans of each full source to use, in order
RANGES = [(r.split(":")[0], *map(float, r.split(":")[1].split(","))) for r in _arg("--ranges").split(";")]
for s in {r[0] for r in RANGES}:
    if not os.path.exists(DIR + s + ".pcm"):
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", DIR + s + ".mp4", "-ac", "1", "-ar", "16000",
                        "-f", "s16le", DIR + s + ".pcm"], check=True)

env = {}
for s in {r[0] for r in RANGES}:
    a = np.fromfile(DIR + s + ".pcm", dtype=np.int16).astype(np.float32) / 32768
    n = len(a) // 160
    rms = np.sqrt((a[: n * 160].reshape(n, 160) ** 2).mean(1) + 1e-12)
    env[s] = 20 * np.log10(rms)  # 10 ms frames, dBFS

def db(src, t):
    i = int(t * 100)
    e = env[src]
    return float(e[min(max(i, 0), len(e) - 1)])

words = []
for src, a, b in RANGES:
    ws = json.load(open(DIR + f"assembly_{src}.json", encoding="utf-8"))["words"]
    for w in ws:
        s, e = w["start"] / 1000, w["end"] / 1000
        if a - 0.05 <= s < b:
            words.append(dict(src=src, s=s, e=e, t=w["text"], rng=(a, b)))

# beats: cut at sentence ends with >= 0.10 s gap, any gap >= 0.25 s, and at range boundaries
beats, cur = [], [words[0]]
for p, w in zip(words, words[1:]):
    gap = w["s"] - p["e"]
    if w["rng"] != p["rng"] or gap >= 0.25 or (p["t"].endswith((".", "!", "?")) and gap >= 0.10):
        beats.append(cur); cur = []
    cur.append(w)
beats.append(cur)

# merge a beat shorter than 1.0 s into the next one when the gap between them is under 0.5 s,
# so single words don't sit alone (a longer gap stays cut: that's dead air worth removing)
merged = []
k = 0
while k < len(beats):
    bw = beats[k]
    while (k + 1 < len(beats) and bw[-1]["e"] - bw[0]["s"] < 1.0 and beats[k + 1][0]["rng"] == bw[0]["rng"]
           and beats[k + 1][0]["s"] - bw[-1]["e"] < 0.5):
        k += 1
        bw = bw + beats[k]
    merged.append(bw)
    k += 1
beats = merged
def speech_db(bw):
    src = bw[0]["src"]
    vals = [db(src, t) for w in bw for t in np.arange(w["s"], w["e"], 0.01)]
    return float(np.median(vals)) if vals else -30.0

def snap(src, t_word, direction, lo, hi, sp):
    """Quiet instant (>= 12 dB under the beat's speech) nearest the word, searching outward
    within 0.25 s (and 0.03 s into the word); else the quietest; then 0.04 s further out."""
    thr = sp - 12
    rng = np.arange(0, 0.25, 0.01)
    cands = [t_word - d for d in rng] if direction < 0 else [t_word + d for d in rng]
    cands = [c for c in cands if lo <= c <= hi]
    inside = [t_word + 0.03 * (-direction) + 0.0]  # allow 0.03 s into the word
    pool = cands or inside
    q = [c for c in pool if db(src, c) <= thr]
    edge = q[0] if q else min(pool, key=lambda c: db(src, c))
    edge = edge + 0.04 * direction
    return min(max(edge, lo), hi)

edl = []
for i, bw in enumerate(beats):
    src = bw[0]["src"]; a, b = bw[0]["rng"]
    prev_e = beats[i - 1][-1]["e"] if i and beats[i - 1][0]["rng"] == bw[0]["rng"] else a
    next_s = beats[i + 1][0]["s"] if i + 1 < len(beats) and beats[i + 1][0]["rng"] == bw[0]["rng"] else b
    sp = speech_db(bw)
    sin = snap(src, bw[0]["s"], -1, max(a, prev_e), bw[0]["s"], sp)
    sout = snap(src, bw[-1]["e"], +1, bw[-1]["e"], min(b, next_s), sp)
    sin, sout = round(sin * FPS) / FPS, round(sout * FPS) / FPS
    # never replay source: an in-edge can't sit before the previous beat's out-edge
    if edl and edl[-1]["src"] == src and edl[-1]["rng"] == (a, b) and sin < edl[-1]["sout"]:
        mid = round((edl[-1]["sout"] + sin) / 2 * FPS) / FPS
        edl[-1]["sout"] = mid
        sin = mid
    # last instant the outgoing line is within 6 dB of its own speech level
    t = sout
    while t > bw[-1]["s"] and db(src, t) < sp - 6:
        t -= 0.01
    tail = max(0.0, sout - t)
    edl.append(dict(i=i, src=src, rng=(a, b), sin=sin, sout=sout, words=[w["t"] for w in bw],
                    wtimes=[(w["s"], w["e"]) for w in bw], speech_db=round(sp, 1), tail=round(tail, 3)))

# tails measured after the no-replay adjustment
for b in edl:
    t = b["sout"]
    while t > b["wtimes"][-1][0] and db(b["src"], t) < b["speech_db"] - 6:
        t -= 0.01
    b["tail"] = round(max(0.0, b["sout"] - t), 3)

# stacked overlaps: incoming starts over the outgoing tail; cold open (first join) 3 frames, body up to 6
T = 0.0
for k, b in enumerate(edl):
    b["T"] = round(T * FPS) / FPS
    dur = b["sout"] - b["sin"]
    if k + 1 < len(edl):
        cap = 3 if k == 0 else 6
        o = min(cap, round(b["tail"] * FPS), int(dur / 3 * FPS))
        b["overlap_frames"] = max(0, o)
        T = b["T"] + dur - b["overlap_frames"] / FPS
json.dump(edl, open(DIR + "edl.json", "w"), indent=1)
end = edl[-1]["T"] + edl[-1]["sout"] - edl[-1]["sin"]
for b in edl:
    print(f'{b["i"]:2} T {b["T"]:6.3f} {b["src"][:3]} {b["sin"]:6.3f}-{b["sout"]:6.3f} ({b["sout"]-b["sin"]:.2f}s) J {b.get("overlap_frames","-")}f  {" ".join(b["words"])}')
print("beats", len(edl), "words", sum(len(b["words"]) for b in edl), "length", round(end, 2), "s")
