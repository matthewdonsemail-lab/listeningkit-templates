"""The launch film's music bed, cut to matt's VO (projects/cyberpunk/audio.mp3, words in audio_words.json) from the
Edgerunners 2 trailer's own soundtrack with its dialogue taken out (projects/opening/ref/trailer_nodialogue.wav: the
demucs htdemucs voices stem removed wherever Whisper found speech) and the song it uses (High Forever, Marlon
Hoffstadt Remix, projects/opening/ref/song.wav):
  the opening (0 - 8.78 s)       the trailer's opening (0 - 3.0 s), then its build into the 41 s hit, which lands on
                                 "split" and the flash into cyberpunk
  cyberpunk (8.78 - 23.70 s)     the trailer from its 41 s hit on: the hit section, then its drop-out under the
                                 close-ups
  the outro on (23.70 s - end)   the song's second drop (138 s) on "introducing", to the end
Ducked about 8 dB under the VO. Writes assets/audio/launch_music.wav (the VO stays its own layer in the comp)."""
import json
import os
import subprocess

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.normpath(os.path.join(HERE, "..", "..", "projects", "opening", "ref"))
VO = os.path.normpath(os.path.join(HERE, "..", "..", "projects", "cyberpunk", "audio.mp3"))
OUT = os.path.join(HERE, "audio", "launch_music.wav")
SR = 48000
ED = json.load(open(os.path.join(HERE, "opening_edit.json")))
SPLIT = ED.get("cyberStart", ED["frames"]) / ED["fps"]  # 8.78: "split" (the trailer hit)
INTRO = 23.70                        # "introducing": the outro, the drop
HIT, HEAD, XF = 41.0, 3.0, int(0.12 * SR)


def cut(path, a, d):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-ss", "%.3f" % a, "-t", "%.3f" % d, "-i", path, "-ac", "2",
                          "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()


def join(x, y):
    r = np.linspace(0, 1, XF, dtype=np.float32)[:, None]
    x[-XF:] = x[-XF:] * (1 - r) + y[:XF] * r
    return np.concatenate([x, y[XF:]])


vo = cut(VO, 0, 9999)
DUR = len(vo) / SR + 1.0
tr = os.path.join(REF, "trailer_nodialogue.wav")
pieces = [cut(tr, 0.0, HEAD + XF / SR), cut(tr, HIT - (SPLIT - HEAD), SPLIT - HEAD + XF / SR),
          cut(tr, HIT, INTRO - SPLIT + XF / SR), cut(os.path.join(REF, "song.wav"), 138.0, DUR - INTRO)]
mix = pieces[0]
for p in pieces[1:]:
    mix = join(mix, p)
mix = mix[:int(DUR * SR)]
# the duck: follow the VO's level (fast attack, slow release) and pull the music down under it
lvl = np.sqrt(np.convolve((vo ** 2).mean(1), np.ones(int(0.03 * SR)) / int(0.03 * SR), "same"))
env = np.zeros(len(mix), np.float32)
a_att, a_rel, e = np.exp(-1 / (0.02 * SR)), np.exp(-1 / (0.35 * SR)), 0.0
gate = (lvl > 0.02).astype(np.float32)
step = 64
for i in range(0, min(len(gate), len(env)), step):
    g = gate[i]
    e = g + (e - g) * (a_att ** step if g > e else a_rel ** step)
    env[i:i + step] = e
mix *= (1 - 0.6 * env)[:, None]  # about -8 dB while he speaks
mix[-int(1.0 * SR):] *= np.linspace(1, 0, int(1.0 * SR), dtype=np.float32)[:, None]
os.makedirs(os.path.dirname(OUT), exist_ok=True)
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", "-c:a",
                "pcm_s16le", OUT], input=mix.astype(np.float32).tobytes())
print("%.2f s -> %s (hit on split %.2f, drop on introducing %.2f)" % (len(mix) / SR, OUT, SPLIT, INTRO))
