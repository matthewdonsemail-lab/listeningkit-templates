"""Stamp scene clean-up: whatever background the generator draws, make it one flat brand blue (#2a8cff).
The girl, the silhouettes and the dithered shadows are black, white and grey; the background is blue. So every pixel
with little colour is kept, everything else becomes flat blue; a soft edge blends the two so the ink lines stay clean.
    python flatten_stamp_bg.py <in.png> [<out.png>]   (writes over the input when no output is given)"""
import sys

import cv2
import numpy as np

BLUE_BGR = np.array([255, 140, 42], np.float32)


def flatten(path, out=None):
    im = cv2.imread(path)
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV).astype(np.float32)
    sat, val = hsv[:, :, 1] / 255.0, hsv[:, :, 2] / 255.0
    keep = np.clip((0.42 - sat) / 0.18, 0, 1)  # neutral (black, white, grey): kept
    keep = np.maximum(keep, np.clip((0.22 - val) / 0.1, 0, 1))  # anything near black: kept
    # only the figures and their shadow pools: grow the kept pixels into clusters (so a dither pool joins up with its
    # figure) and drop the small clusters left over from whatever background the generator drew
    grown = cv2.dilate((keep > 0.5).astype(np.uint8), np.ones((31, 31), np.uint8))
    n, labels, stats, _ = cv2.connectedComponentsWithStats(grown)
    big = np.zeros(n, bool)
    big[1:] = stats[1:, cv2.CC_STAT_AREA] > 0.004 * keep.size
    keep = keep * big[labels]
    keep = cv2.GaussianBlur(keep, (3, 3), 0)[:, :, None]
    flat = im.astype(np.float32) * keep + BLUE_BGR * (1 - keep)
    cv2.imwrite(out or path, np.clip(flat, 0, 255).astype(np.uint8))


if __name__ == "__main__":
    flatten(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
    print("flattened", sys.argv[-1])
