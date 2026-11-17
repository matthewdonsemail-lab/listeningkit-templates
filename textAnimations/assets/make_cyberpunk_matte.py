"""Cyberpunk opening: the girl on her own layer. open_a is the same locked-off shot with her spot empty, so inside a box
around her the difference between open_b and open_a is her; GrabCut, seeded with that difference, cleans the edge.
Writes projects/cyberpunk/girl.png: open_b with her alpha (1920x1080, transparent everywhere else)."""
import cv2
import numpy as np

CP = "C:/Users/0/.buzz/REPOS/listeningkit-templates/projects/cyberpunk/"
b = cv2.imread(CP + "open_b.png")
a = cv2.imread(CP + "open_a.png")
H, W = b.shape[:2]
x0, y0, x1, y1 = int(0.42 * W), int(0.30 * H), int(0.58 * W), int(0.92 * H)  # the box she stands in

diff = cv2.absdiff(cv2.GaussianBlur(b, (5, 5), 0), cv2.GaussianBlur(a, (5, 5), 0)).max(axis=2)
mask = np.full((H, W), cv2.GC_BGD, np.uint8)
box = diff[y0:y1, x0:x1]
seed = np.full(box.shape, cv2.GC_PR_BGD, np.uint8)
seed[box > 28] = cv2.GC_PR_FGD
seed[box > 70] = cv2.GC_FGD
mask[y0:y1, x0:x1] = seed
bgd, fgd = np.zeros((1, 65), np.float64), np.zeros((1, 65), np.float64)
cv2.grabCut(b, mask, None, bgd, fgd, 6, cv2.GC_INIT_WITH_MASK)
alpha = np.where((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 255, 0).astype(np.uint8)

# keep the biggest piece (her), fill holes, soften the edge a touch
n, labels, stats, _ = cv2.connectedComponentsWithStats(alpha)
if n > 1:
    big = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
    alpha = np.where(labels == big, 255, 0).astype(np.uint8)
alpha = cv2.morphologyEx(alpha, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
# around her feet keep only the dark shoes and trousers, not the light floor GrabCut pulled in with them
# and not her shadow: the shoes and trousers are near-black, the shadowed floor mid-gray, so over her lower legs keep
# only the dark pixels, then the biggest piece again
ys, xs = np.where(alpha > 0)
feet = int(ys.max()) - 170
lum = cv2.cvtColor(cv2.GaussianBlur(b, (3, 3), 0), cv2.COLOR_BGR2GRAY)
alpha[feet:][lum[feet:] > 62] = 0
alpha = cv2.morphologyEx(alpha, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
alpha = cv2.morphologyEx(alpha, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)))
n, labels, stats, _ = cv2.connectedComponentsWithStats(alpha)
if n > 1:
    big = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
    alpha = np.where(labels == big, 255, 0).astype(np.uint8)
alpha = cv2.GaussianBlur(alpha, (5, 5), 0)
out = np.dstack([b, alpha])
cv2.imwrite(CP + "girl.png", out)
ys, xs = np.where(alpha > 128)
print("girl.png", int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max()), int((alpha > 128).sum()), "px")
