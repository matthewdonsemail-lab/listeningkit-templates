"""Mix the RE-USE cleaned mic with the original where RE-USE drops speech (matt, 2026-11-16: "places where the audio
just goes silent ... the original has background noise, the clean one is a bit too strict").

  * level-match the original to the RE-USE file (median gain on speech frames)
  * dropouts: 10 ms frames where the original has speech (within 12 dB of its speech median) but RE-USE is more than
    DROP_DB under the level-matched original, held for 50 ms+, padded 40 ms each side; there the original (light
    denoise: ffmpeg afftdn) replaces RE-USE, with 20 ms crossfades
  * everywhere else: RE-USE + BLEND of the level-matched original, so it sounds less strict
Writes voice_mixed_full.wav (same length as the mic) and mix_report.txt.
  uv run --no-project --with numpy python mix_dialogue.py [--blend 0.15] [--drop-db 10]"""
import argparse
import subprocess
import wave

import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("--blend", type=float, default=0.15)
ap.add_argument("--drop-db", type=float, default=10.0)
args = ap.parse_args()


def read(p):
    with wave.open(p) as w:
        sr, ch = w.getframerate(), w.getnchannels()
        d = np.frombuffer(w.readframes(w.getnframes()), "<i2").astype(np.float32).reshape(-1, ch).mean(1) / 32768
    return d, sr


subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "mic.wav", "-af", "afftdn=nr=12:nf=-50", "-c:a", "pcm_s16le",
                "mic_denoised.wav"], check=True)
raw, sr = read("mic_denoised.wav")
reu, sr2 = read("voice_reuse_full.wav")
assert sr == sr2 and abs(len(raw) - len(reu)) < sr // 10, (sr, sr2, len(raw), len(reu))
n = min(len(raw), len(reu)); raw, reu = raw[:n], reu[:n]
hop = sr // 100; m = n // hop


def env(x):
    return 10 * np.log10(np.maximum((x[:m * hop].reshape(m, hop) ** 2).mean(1), 1e-12))


er, eu = env(raw), env(reu)
speech_med = np.median(er[er > np.percentile(er, 60)])
speech = er > speech_med - 12
gain_db = float(np.median(eu[speech] - er[speech]))  # how much louder RE-USE is on speech
raw_m = raw * 10 ** (gain_db / 20)
er_m = er + gain_db
k = np.ones(5) / 5
drop = speech & (np.convolve(eu, k, "same") < np.convolve(er_m, k, "same") - args.drop_db)
# keep runs of 50 ms+, pad 40 ms each side
mask = np.zeros(m, bool)
i = 0
while i < m:
    if drop[i]:
        j = i
        while j < m and drop[j]:
            j += 1
        if j - i >= 5:
            mask[max(0, i - 4):min(m, j + 4)] = True
        i = j
    else:
        i += 1
# sample-level weight for the original, 20 ms ramps
w = np.repeat(mask.astype(np.float32), hop)
w = np.r_[w, np.zeros(n - len(w), np.float32)]
ramp = np.ones(int(0.02 * sr), np.float32) / int(0.02 * sr)
w = np.clip(np.convolve(w, ramp, "same"), 0, 1)
out = (1 - w) * (reu + args.blend * raw_m) / (1 + args.blend) + w * raw_m
out = out / max(1.0, float(np.abs(out).max()) / 0.98)
with wave.open("voice_mixed_full.wav", "wb") as o:
    o.setnchannels(1); o.setsampwidth(2); o.setframerate(sr)
    o.writeframes((np.clip(out, -1, 1) * 32767).astype("<i2").tobytes())
runs = []
i = 0
while i < m:
    if mask[i]:
        j = i
        while j < m and mask[j]:
            j += 1
        runs.append((i / 100, j / 100)); i = j
    else:
        i += 1
lines = [f"RE-USE gain over the original on speech: {gain_db:+.1f} dB; blend {args.blend:.0%} original; dropout "
         f"threshold {args.drop_db} dB", f"dropouts patched from the original: {len(runs)}, {mask.sum() / 100:.1f} s in total", ""]
lines += [f"{a // 60:.0f}:{a % 60:05.2f}  {b - a:.2f}s" for a, b in runs]
open("mix_report.txt", "w", encoding="utf8").write("\n".join(lines) + "\n")
print("\n".join(lines[:3]))
print("longest:", sorted(runs, key=lambda r: r[0] - r[1])[:5])
