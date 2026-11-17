"""The outro's audio (matt, 2026-11-16): instead of looping the last bar and fading, the girl's last sung phrase is
stuttered, loops cut shorter and shorter on the beat, then a glitch and a reverb tail.
From assets/audio/launch_music.wav (156 bpm, beat 0.384 s, measured by onset autocorrelation; the phrase's beats land
at 58.30, 58.69, 59.07 s). The music plays as it is to 58.30 s (where the end card comes in), then:
  2 beats x2, 1 beat x2, 1/2 x2, 1/4 x4, 1/8 x4  (each repeat of the phrase's start, 3 ms edges so nothing clicks)
  a 0.15 s glitch (the last slice reversed, bit-crushed and stuttered)
  a reverb tail of the 1-beat slice (convolved with a decaying noise impulse, darkened), 3.6 s
Writes assets/audio/launch_music_outro.wav and prints the loop start times (s, from 58.30) for plugins/endingOutro.jsx.
  python textAnimations/assets/make_outro_audio.py"""
import os
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
w = wave.open(os.path.join(HERE, "audio", "launch_music.wav")); sr = w.getframerate(); ch = w.getnchannels()
x = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, ch).astype(np.float32) / 32768
T0, BEAT = 58.30, 0.384


def sl(t, d):
    s = x[int(t * sr):int((t + d) * sr)].copy()
    e = int(0.003 * sr); r = np.linspace(0, 1, e)[:, None]
    s[:e] *= r; s[-e:] *= r[::-1]
    return s


parts, starts, t = [x[:int(T0 * sr)]], [], 0.0
for beats, reps in ((2, 2), (1, 2), (0.5, 2), (0.25, 4), (0.125, 4)):
    for _ in range(reps):
        starts.append(round(t, 3)); seg = sl(T0, beats * BEAT); parts.append(seg); t += len(seg) / sr
gl_at = t
last = sl(T0, 0.125 * BEAT)
g = np.concatenate([last[::-1], last, last[::-1]])                  # the glitch: reversed, crushed, stuttered
g = np.round(g * 6) / 6
g = np.concatenate([g, g[: len(g) // 2]])[: int(0.15 * sr)]
parts.append(g); t += len(g) / sr
rng = np.random.default_rng(3)
L = int(3.6 * sr)
ir = rng.standard_normal(L) * np.exp(-np.linspace(0, 7, L))
ir = np.convolve(ir, np.ones(40) / 40, "same")                        # darker
src = sl(T0, BEAT)
tail = np.stack([np.convolve(src[:, c], ir)[:L] for c in range(ch)], 1)
tail = tail / (np.abs(tail).max() + 1e-9) * 0.45
parts.append(tail)
y = np.clip(np.concatenate(parts), -1, 1)
o = wave.open(os.path.join(HERE, "audio", "launch_music_outro.wav"), "wb")
o.setnchannels(ch); o.setsampwidth(2); o.setframerate(sr); o.writeframes((y * 32767).astype(np.int16).tobytes()); o.close()
print("length %.2f s; loops at %s; glitch at %.3f; tail from %.3f (all from %.2f)" % (len(y) / sr, starts, gl_at, t - L / sr, T0))
