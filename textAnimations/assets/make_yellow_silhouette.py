"""The stamp girl lit like matt's lighting reference (projects/opening/ref/yt_line/lighting_sheet.jpg, the shot at
about 1:05 of yt_line/ref.mp4): a solid silhouette on a flat backdrop, lit only by hard flat shapes of light along
her top and left edges (hair, face, shoulder, the reaching hand), no other detail. Two shots to alternate between:
  wide   far out, small in the middle (what the busts melt into)
  close  her larger, centre frame
In two palettes: "ours" (yellow backdrop, blue silhouette, warm white light: matt's yellow and blue) and "ref" (the
reference's: deep blue backdrop, black silhouette, orange light). Fine vertical stripes and grain over both.
From projects/cyberpunk/outro/stamp_girl_yellow.png (images/gen/make_yellow_woman.py).
Writes projects/cyberpunk/outro/stamp_girl_<wide|close>_<ours|ref>.png
  python textAnimations/assets/make_yellow_silhouette.py"""
import os

import cv2
import numpy as np

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUTRO = os.path.join(ROOT, "projects", "cyberpunk", "outro")
W, H = 1920, 1080
SHOTS = {"wide": (0.5, 960, 520), "close": (1.6, 945, 395)}     # zoom, centre in the source
PALETTES = {  # BGR: backdrop, silhouette, light
    "ours": ((92, 206, 222), (105, 28, 14), (215, 240, 255)),
    "ref": ((150, 30, 10), (12, 8, 12), (20, 170, 255)),
}

src = cv2.imread(os.path.join(OUTRO, "stamp_girl_yellow.png"))


def her(zoom, cx, cy):
    """her mask and her brightness, framed for the shot"""
    M = cv2.getRotationMatrix2D((cx, cy), 0, zoom)
    M[0, 2] += W / 2 - cx; M[1, 2] += H / 2 - cy
    img = cv2.warpAffine(src, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    yel = (hsv[:, :, 0] > 15) & (hsv[:, :, 0] < 40) & (hsv[:, :, 1] > 110)
    fig = (~yel).astype(np.uint8) * 255
    fig = cv2.morphologyEx(fig, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(fig)
    fig = np.where(lab == 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA])), 255, 0).astype(np.uint8)
    fig = cv2.morphologyEx(fig, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    lum = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255
    return fig, lum


def light(fig, lum, zoom):
    """hard flat shapes of light from the top left: the band of her that the outline shifted down-right doesn't
    cover (the lit edge, wide, so hair tips, the shoulder and the hand's edge catch it), plus her own white areas
    (skin, sleeves) where they sit on that lit side; posterized hard, no gradients"""
    k = max(4, int(18 * zoom))
    sh = np.roll(np.roll(fig, k, axis=1), int(k * 0.8), axis=0)
    band = (fig > 0) & (sh == 0)
    k2 = max(3, int(40 * zoom))
    sh2 = np.roll(np.roll(fig, k2, axis=1), int(k2 * 0.8), axis=0)
    wide_band = (fig > 0) & (sh2 == 0)
    whites = (lum > 0.7) & wide_band
    m = (band | whites).astype(np.uint8) * 255
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    return m


def finish(out):
    cols = (np.arange(W) % 3)
    stripe = np.stack([(cols == 0), (cols == 1), (cols == 2)], -1).astype(np.float32)
    out = out * (0.94 + 0.08 * stripe[None, :, :])
    out = out + np.random.default_rng(3).normal(0, 4, (H, W, 1))
    return np.clip(out, 0, 255).astype(np.uint8)


for shot, (zoom, cx, cy) in SHOTS.items():
    fig, lum = her(zoom, cx, cy)
    lit = light(fig, lum, zoom)
    f = cv2.GaussianBlur(fig.astype(np.float32) / 255, (0, 0), 0.7)[:, :, None]
    l = cv2.GaussianBlur(lit.astype(np.float32) / 255, (0, 0), 0.6)[:, :, None]
    for pal, (bg, ink, li) in PALETTES.items():
        body = np.array(ink, np.float32) * (1 - l) + np.array(li, np.float32) * l
        out = np.array(bg, np.float32) * (1 - f) + body * f
        cv2.imwrite(os.path.join(OUTRO, "stamp_girl_%s_%s.png" % (shot, pal)), finish(out))
        print("wrote", shot, pal)
