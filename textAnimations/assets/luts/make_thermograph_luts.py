"""Thermograph LUTs for the cuts in Intro 1: brightness flipped (dark reads hot) through a heat ramp."""
import os
import numpy as np

N = 33
LOOKS = {
    "thermograph_orange": [(0, (30, 8, 4)), (0.25, (120, 30, 10)), (0.5, (215, 80, 20)),
                           (0.7, (245, 150, 45)), (0.87, (252, 220, 110)), (1, (255, 250, 225))],
    "thermograph_green": [(0, (14, 30, 20)), (0.3, (45, 80, 55)), (0.55, (100, 140, 105)),
                          (0.78, (185, 210, 170)), (1, (242, 246, 228))],
}

here = os.path.dirname(os.path.abspath(__file__))
g = np.linspace(0, 1, N)
for name, stops in LOOKS.items():
    xs = [s[0] for s in stops]
    lines = ['TITLE "%s"' % name, "LUT_3D_SIZE %d" % N]
    for b in g:
        for gg in g:
            for r in g:
                y = 0.2126 * r + 0.7152 * gg + 0.0722 * b
                v = 0.1 + 0.62 * (1 - y) ** 1.4 + 0.25 * (1 - y) ** 8
                rgb = [np.interp(v, xs, [s[1][ch] / 255 for s in stops]) for ch in range(3)]
                lines.append("%.6f %.6f %.6f" % tuple(rgb))
    with open(os.path.join(here, name + ".cube"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print(name)

