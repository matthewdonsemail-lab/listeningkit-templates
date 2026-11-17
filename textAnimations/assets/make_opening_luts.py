"""The opening's two grades as 33-point .cube LUTs (assets/luts/), applied per shot by plugins/openingGrade.jsx:
  bigshort_cold.cube   inside shots: The Big Short's cold blue-grey (projects/opening/ref/bigshort_stylesheet.png):
                       colour mostly drained, mapped onto its palette (shadows #0d121b, mids #596b84 / #82a1c0,
                       highlights #aac2e1), a quarter of the original colour kept for skin
  sunny_gold.cube      outside and in the car: warm golden hour, reds and greens lifted, blues pulled down, a gentle
                       S-curve and a little more saturation"""
import os

import numpy as np

N = 33
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "luts")
g = np.linspace(0, 1, N)
b, gg, r = np.meshgrid(g, g, g, indexing="ij")  # .cube order: red fastest
rgb = np.stack([r, gg, b], -1).reshape(-1, 3)
L = rgb @ np.array([0.2126, 0.7152, 0.0722])

stops = np.array([0, 0.45, 0.75, 1.0])
cols = np.array([[13, 18, 27], [89, 107, 132], [130, 161, 192], [205, 220, 238]]) / 255.0
tint = np.stack([np.interp(L, stops, cols[:, c]) for c in range(3)], -1)
grey = L[:, None] + 0.25 * (rgb - L[:, None])
cold = np.clip(0.72 * tint + 0.28 * grey, 0, 1)

s = rgb * np.array([1.07, 1.0, 0.84]) + np.array([0.025, 0.012, -0.01])
s = s + 0.12 * (s - s.mean(1, keepdims=True))  # a little more saturation
s = s + 0.10 * np.sin((s - 0.5) * np.pi) * 0.5  # gentle S-curve
sunny = np.clip(s, 0, 1)

os.makedirs(OUT, exist_ok=True)
for name, data in (("bigshort_cold", cold), ("sunny_gold", sunny)):
    with open(os.path.join(OUT, name + ".cube"), "w", newline="\n") as f:
        f.write('TITLE "%s"\nLUT_3D_SIZE %d\n' % (name, N))
        f.writelines("%.6f %.6f %.6f\n" % tuple(v) for v in data)
    print("wrote", name)
