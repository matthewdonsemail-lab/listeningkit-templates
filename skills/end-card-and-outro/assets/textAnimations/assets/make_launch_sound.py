"""The launch film's sound (intro + cyberpunk, about 24 s): High Forever (Marlon Hoffstadt Remix) cut so its drop
lands on the Nous flash, with sound design on top in the way the Edgerunners 2 trailer does it (risers into the big
moments, impacts on the hits, a glitch stutter when it goes mental, a drop-out before it comes back). No dialogue.
The SFX are synthesised here, nothing downloaded. Writes assets/audio/launch_sound_synth.wav (48 kHz stereo); the film plays the trailer-cut version (make_launch_sound_trailer.py).

  0 - 7.0 s    the intro (the creation of AI, sunny): the song's soft intro, a little muffled, room tone, a shimmer on
               the dust, soft whooshes on the cutaways; a riser into the white flash
  7.0          the flash into cyberpunk: an impact and a glitch stutter, as the trailer's hit at 41 s
  7.0 - 12.2   cyberpunk's walk-in and close-ups: the song's last build before its second drop; an impact on the
               thermogram cut; a riser into the drop
  13.4 -       the drop (song 138 s) on the flash and the Nous logo, under the outro's fast cuts; hits on its sections;
               a glitch stutter and a cut to silence at the very end
Song: projects/opening/ref/song.wav (downloaded by matt's request from his link)."""
import json
import os
import subprocess

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SONG = os.path.normpath(os.path.join(HERE, "..", "..", "projects", "opening", "ref", "song.wav"))
OUT = os.path.join(HERE, "audio", "launch_sound_synth.wav")
SR = 48000
ED = json.load(open(os.path.join(HERE, "opening_edit.json")))
OPEN = ED["frames"] / ED["fps"]                      # 8.2 s
CYBER = 5.2 + 356 / 30                               # cyberpunk's length: close-ups end at 5.2 s, then the outro
DROP = OPEN + 5.2                                    # the outro's flash
DUR = OPEN + CYBER
rng = np.random.default_rng(7)
mix = np.zeros((int(DUR * SR) + SR, 2), np.float32)


def song(at, dur):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-ss", "%.3f" % at, "-t", "%.3f" % dur, "-i", SONG,
                          "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()


def put(x, t, gain=1.0):
    a = int(t * SR)
    b = min(len(mix), a + len(x))
    mix[a:b] += x[:b - a] * gain


def fade(x, fin=0.0, fout=0.0):
    n = len(x)
    env = np.ones(n, np.float32)
    if fin:
        k = min(n, int(fin * SR)); env[:k] = np.linspace(0, 1, k)
    if fout:
        k = min(n, int(fout * SR)); env[n - k:] *= np.linspace(1, 0, k)
    return x * env[:, None]


def onepole(x, cutoff, high=False):
    """one-pole low/high pass; cutoff may be an array (a sweep)"""
    cut = np.broadcast_to(np.asarray(cutoff, np.float32), (len(x),))
    a = np.exp(-2 * np.pi * cut / SR).astype(np.float32)
    y = np.empty_like(x)
    s = np.zeros(x.shape[1], np.float32)
    for i in range(len(x)):
        s = (1 - a[i]) * x[i] + a[i] * s
        y[i] = s
    return x - y if high else y


def noise(dur):
    return rng.standard_normal((int(dur * SR), 2)).astype(np.float32)


def riser(dur):
    n = int(dur * SR)
    t = np.linspace(0, 1, n, dtype=np.float32)
    nz = onepole(onepole(noise(dur), 400 + 9000 * t ** 2, high=True), 2000 + 14000 * t)
    f = 90 * (10 ** (t * 1.2))  # a pitch climbing about 4 octaves
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR).astype(np.float32)[:, None] * np.array([[1, 1]], np.float32)
    env = (t ** 2.2)[:, None]
    return (0.35 * nz + 0.25 * tone) * env


def impact(dur=1.6, sub=52):
    n = int(dur * SR)
    t = np.arange(n, dtype=np.float32) / SR
    f = sub * np.exp(-t * 1.4) + 28
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.6)
    crack = onepole(noise(dur), 3500)[:, 0] * np.exp(-t * 28)
    x = np.tanh(1.6 * (0.9 * boom + 0.6 * crack)).astype(np.float32)
    return np.stack([x, x], 1)


def whoosh(dur=0.45, peak=0.55):
    n = int(dur * SR)
    t = np.linspace(0, 1, n, dtype=np.float32)
    env = np.where(t < peak, (t / peak) ** 2, ((1 - t) / (1 - peak)) ** 1.5)[:, None]
    return onepole(onepole(noise(dur), 300 + 2500 * env[:, 0], high=True), 800 + 6000 * env[:, 0]) * env * 0.5


def shimmer(dur):
    """the dust: tiny bright glints"""
    x = np.zeros((int(dur * SR), 2), np.float32)
    for _ in range(int(dur * 14)):
        a = rng.integers(0, len(x) - 4000)
        f = rng.uniform(3000, 7000)
        t = np.arange(4000) / SR
        g = (np.sin(2 * np.pi * f * t) * np.exp(-t * 60)).astype(np.float32) * rng.uniform(0.05, 0.15)
        x[a:a + 4000, 0] += g * rng.uniform(0.3, 1)
        x[a:a + 4000, 1] += g * rng.uniform(0.3, 1)
    return x


def stutter(t, dur=0.42, slice_=0.045):
    """the trailer's glitch: one short slice of what is playing, repeated, gated, each repeat a little lower"""
    a = int(t * SR)
    src = mix[a:a + int(slice_ * SR)].copy()
    out = np.zeros((int(dur * SR), 2), np.float32)
    k, rep = 0, 0
    while k < len(out):
        step = max(64, int(len(src) * (1 + 0.12 * rep)))
        idx = np.linspace(0, len(src) - 1, step).astype(int)  # stretched: the pitch drops each repeat
        piece = src[idx] * (1.0 if rep % 2 == 0 else 0.7)
        piece[-200:] *= np.linspace(1, 0, 200)[:, None]
        out[k:k + len(piece)] = piece[:len(out) - k]
        k += len(piece) + int(0.008 * SR)
        rep += 1
    mix[a:a + len(out)] = out[:len(mix) - a]


# --- the opening: the song's soft intro, muffled, under room tone
intro = onepole(song(2.0, OPEN), 2400)
put(fade(intro, 1.2, 0.2), 0.0, 1.6)
put(onepole(onepole(noise(OPEN), 120, high=True), 600) * 0.02, 0.0)               # room tone
for s in ED["shots"]:
    t = s["in"] / ED["fps"]
    if s["in"]:
        put(whoosh(0.35), t - 0.2, 0.22)                                           # soft air on each cutaway
    if s.get("dust"):
        put(shimmer((s["out"] - s["in"]) / ED["fps"] + 0.6), t, 1.0)
put(riser(1.8), OPEN - 1.8, 0.95)                                                  # into the white flash
put(impact(2.2, 60), OPEN, 1.0)

# --- cyberpunk: the build before the second drop, then the drop on the flash
build_from = 138.0 - (DROP - OPEN)          # so song 138.0 (the drop) lands on the flash
put(fade(song(build_from, DROP - OPEN), 0.25, 0.0), OPEN, 1.0)
stutter(OPEN + 0.02, 0.36)                                                         # the glitch on the flash
put(impact(1.4, 48), OPEN + 2.0, 0.7)                                              # the thermogram cut
put(whoosh(0.6, 0.8), OPEN + 2.0 - 0.45, 0.5)
put(riser(1.8), DROP - 1.8, 1.0)                                                   # into the drop
put(fade(song(138.0, DUR - DROP), 0.0, 0.0), DROP, 1.0)
put(impact(2.4, 64), DROP, 1.1)                                                    # the flash
OUTRO = {"logo": 4, "push": 28, "back": 70, "end": 104, "portraits": 176}
for k in ("push", "back", "portraits"):
    put(impact(0.9, 70), DROP + OUTRO[k] / 30, 0.45)
put(whoosh(0.9, 0.7), DROP + OUTRO["end"] / 30 - 0.6, 0.5)                         # the busts reveal
for i in range(1, 6):
    put(whoosh(0.3), DROP + (OUTRO["portraits"] + 30 * i) / 30 - 0.15, 0.3)        # the portrait cuts
stutter(DUR - 0.42, 0.42)                                                          # the end, as the trailer ends
mix[int(DUR * SR):] = 0

peak = np.abs(mix).max()
mix = np.tanh(mix / peak * 1.25) * 0.89  # a soft limit
os.makedirs(os.path.dirname(OUT), exist_ok=True)
p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-",
                      "-t", "%.3f" % DUR, "-c:a", "pcm_s16le", OUT], stdin=subprocess.PIPE)
p.stdin.write(mix.astype(np.float32).tobytes())
p.stdin.close()
p.wait()
print("%.2f s -> %s (cyberpunk %.2f, drop %.2f)" % (DUR, OUT, OPEN, DROP))
