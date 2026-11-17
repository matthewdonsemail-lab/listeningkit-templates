"""The outro's last shot (projects/cyberpunk/outro/back_11.png, the blue chiaroscuro girl facing away) on its own layer:
OpenCV GrabCut, seeded with a box round her (she fills the middle of the frame, cut off at the bottom) and her bright
rim light as sure foreground, then the biggest piece kept and the edge softened.
Writes projects/cyberpunk/outro/back_11_girl.png (RGBA)."""
import cv2
import numpy as np

CP = "C:/Users/0/.buzz/REPOS/listeningkit-templates/projects/cyberpunk/outro/"
im = cv2.imread(CP + "back_11.png")
H, W = im.shape[:2]
mask = np.full((H, W), cv2.GC_BGD, np.uint8)
x0, x1, y0 = int(0.26 * W), int(0.74 * W), int(0.02 * H)
mask[y0:, x0:x1] = cv2.GC_PR_FGD
hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
rim = (hsv[:, :, 2] > 170) & (hsv[:, :, 1] > 90)  # the glowing blue rim light on her outline
rim[:, :x0] = False
rim[:, x1:] = False
mask[rim] = cv2.GC_FGD
mask[int(0.85 * H):, int(0.40 * W):int(0.60 * W)] = cv2.GC_FGD  # her back, at the bottom centre
bgd, fgd = np.zeros((1, 65), np.float64), np.zeros((1, 65), np.float64)
cv2.grabCut(im, mask, None, bgd, fgd, 6, cv2.GC_INIT_WITH_MASK)
alpha = np.where((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 255, 0).astype(np.uint8)
n, labels, stats, _ = cv2.connectedComponentsWithStats(alpha)
if n > 1:
    alpha = np.where(labels == 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA])), 255, 0).astype(np.uint8)
alpha = cv2.morphologyEx(alpha, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15)))
alpha[int(0.66 * H):int(0.82 * H), :int(0.32 * W)] = 0  # a piece of the city caught by her left side
alpha = cv2.GaussianBlur(alpha, (5, 5), 0)
cv2.imwrite(CP + "back_11_girl.png", np.dstack([im, alpha]))
print("girl matte", int((alpha > 128).mean() * 100), "% of the frame")
