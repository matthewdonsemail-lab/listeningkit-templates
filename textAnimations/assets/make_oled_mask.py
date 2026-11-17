"""The OLED / LED subpixel mask for the ending's screen (plugins/endingOled.jsx), matt 2026-11-15: a 1920x1080 tile of
pixels PITCH px wide, each one three vertical subpixel bars (red, green, blue) with a dark gap round them, as on a
real panel seen close up. Multiplied over the picture after it's been mosaicked to the same pixel grid (Mosaic
1920/PITCH x 1080/PITCH), so every screen pixel lights its own three subpixels.
Writes assets/oled_subpixels.png
  python textAnimations/assets/make_oled_mask.py"""
import os

import cv2
import numpy as np

PITCH = 8
W, H = 1920, 1080
cell = np.zeros((PITCH, PITCH, 3), np.float32)             # BGR
bars = [(2, 1), (1, 3), (0, 5)]                            # (channel, x): red, green, blue, each 2 px wide
for ch, x in bars:
    cell[1:PITCH - 1, x:x + 2, ch] = 1.0
cell = cv2.GaussianBlur(cell, (0, 0), 0.45)                 # soft subpixel edges
tile = np.tile(cell, (H // PITCH, W // PITCH, 1))
cv2.imwrite(os.path.join(os.path.dirname(os.path.abspath(__file__)), "oled_subpixels.png"),
            np.clip(tile / tile.max() * 255, 0, 255).astype(np.uint8))
print("wrote assets/oled_subpixels.png, pitch", PITCH)
