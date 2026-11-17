"""Offset of matt's Cap render against the timeline's dialogue (dialogue-limited.wav), at 6 points (filmcraft README:
"Swapping in Matt's render"). Positive lag = the render's audio is late against the dialogue."""
import subprocess, sys
import numpy as np
REN = r"C:\Users\0\filmcraft\projects\effectcraft treg\How to Edit in EffectCraft.mp4"
SR = 8000
def pcm(path, t, d):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-t", str(d), "-i", path, "-ac", "1", "-ar", str(SR),
                          "-f", "s16le", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32)
out = []
for t in (120, 800, 1500, 2200, 3000, 3900):
    a = pcm("dialogue-limited.wav", t, 20); b = pcm(REN, t - 1, 22)
    a = (a - a.mean()) / (a.std() + 1e-9); b = (b - b.mean()) / (b.std() + 1e-9)
    n = len(a) + len(b)
    c = np.fft.irfft(np.fft.rfft(b, n) * np.conj(np.fft.rfft(a, n)), n)
    k = int(np.argmax(c[:len(b)]))
    lag = (k / SR) - 1.0          # b starts 1 s earlier
    out.append(lag); print(f"t={t:5d}s  render lag {lag*1000:+7.1f} ms  peak {c[k]/len(a):.2f}")
print(f"median {np.median(out)*1000:+.1f} ms, spread {(max(out)-min(out))*1000:.1f} ms")
