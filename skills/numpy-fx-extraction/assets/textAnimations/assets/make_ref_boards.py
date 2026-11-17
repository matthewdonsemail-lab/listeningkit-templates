"""Design boards from the reference edits (matt, 2026-11-15): one board per technique, the clearest frames of it
side by side at a readable size, labelled with the video and frame, so matt can say yes or no to each look.
BOARDS below lists the technique, then (video id, frame) pairs, read off the contact sheets
(projects/opening/ref/cyberpunk_edits/<id>/sheet_NN.jpg).
Writes projects/opening/ref/cyberpunk_edits/boards/NN_<name>.jpg
  python textAnimations/assets/make_ref_boards.py [board-name ...]"""
import os
import sys

import cv2
from PIL import Image, ImageDraw

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
REF = os.path.join(ROOT, "projects", "opening", "ref", "cyberpunk_edits")
OUT = os.path.join(REF, "boards")
BOARDS = [
    ("neon_title_words", [("5p4wnTR6s04", 15), ("5p4wnTR6s04", 22), ("5p4wnTR6s04", 487), ("5p4wnTR6s04", 510)]),
    ("sandevistan_echo", [("iXgwnM6g4ls", 300), ("iXgwnM6g4ls", 380), ("iXgwnM6g4ls", 450), ("iXgwnM6g4ls", 720)]),
    ("hud_ring_zoom", [("5p4wnTR6s04", 178), ("5p4wnTR6s04", 188), ("5p4wnTR6s04", 370), ("5p4wnTR6s04", 382)]),
    ("word_by_word_type", [("eOb7dCUrP9Q", 35), ("eOb7dCUrP9Q", 395), ("eOb7dCUrP9Q", 515), ("eOb7dCUrP9Q", 690)]),
    ("whip_smear_cuts", [("5p4wnTR6s04", 81), ("5p4wnTR6s04", 84), ("5p4wnTR6s04", 275), ("5p4wnTR6s04", 310)]),
    ("yellow_silhouette_datamosh", [("olq9HVHHlpE", 300), ("olq9HVHHlpE", 316), ("olq9HVHHlpE", 340), ("olq9HVHHlpE", 430)]),
    ("tracking_tear_rgb", [("UqgNmYl_5Hw", 45), ("UqgNmYl_5Hw", 51), ("UqgNmYl_5Hw", 57), ("olq9HVHHlpE", 310)]),
    ("window_inserts", [("eOb7dCUrP9Q", 70), ("eOb7dCUrP9Q", 220), ("eOb7dCUrP9Q", 240), ("eOb7dCUrP9Q", 340)]),
    ("micro_caps", [("5p4wnTR6s04", 40), ("5p4wnTR6s04", 422), ("5p4wnTR6s04", 465), ("AYA8DdWe4U8", 80)]),
    ("logo_resolve", [("UqgNmYl_5Hw", 360), ("UqgNmYl_5Hw", 380), ("5p4wnTR6s04", 620), ("olq9HVHHlpE", 820)]),
    # from the official trailers and the opening-titles tutorial
    ("rgb_bar_flash_cuts", [("JtqIas3bYhg", 503), ("JtqIas3bYhg", 506), ("JtqIas3bYhg", 1718), ("JtqIas3bYhg", 1721)]),
    ("teal_statement_cards", [("ax5YUmkWf_Y", 1160), ("ax5YUmkWf_Y", 2050), ("ax5YUmkWf_Y", 2470), ("ax5YUmkWf_Y", 2630)]),
    ("light_streak_wipe", [("ax5YUmkWf_Y", 767), ("ax5YUmkWf_Y", 1074), ("ax5YUmkWf_Y", 1900), ("ax5YUmkWf_Y", 2231)]),
    ("lime_name_callouts", [("ax5YUmkWf_Y", 1500), ("ax5YUmkWf_Y", 1555), ("ax5YUmkWf_Y", 1730), ("ax5YUmkWf_Y", 1810)]),
    ("countdown_glitch_type", [("JtqIas3bYhg", 543), ("JtqIas3bYhg", 560), ("JtqIas3bYhg", 565), ("JtqIas3bYhg", 598)]),
    ("giant_word_shout", [("JtqIas3bYhg", 1342), ("JtqIas3bYhg", 1348), ("JtqIas3bYhg", 1355), ("JtqIas3bYhg", 1361)]),
    ("red_line_tagline", [("urV5GzXcXsQ", 1046), ("urV5GzXcXsQ", 1080), ("urV5GzXcXsQ", 1110), ("urV5GzXcXsQ", 1129)]),
    ("impact_frames", [("JtqIas3bYhg", 1495), ("JtqIas3bYhg", 1907), ("JtqIas3bYhg", 2142), ("JtqIas3bYhg", 2356)]),
    ("logo_colourways_streaks", [("ax5YUmkWf_Y", 3405), ("ax5YUmkWf_Y", 3430), ("ax5YUmkWf_Y", 3865), ("JtqIas3bYhg", 2875)]),
]
W, H = 960, 540


def frame(vid, n):
    cap = cv2.VideoCapture(os.path.join(REF, vid, "video.mp4"))
    cap.set(cv2.CAP_PROP_POS_FRAMES, n)
    ok, f = cap.read()
    return Image.fromarray(cv2.cvtColor(f, cv2.COLOR_BGR2RGB)).resize((W, H)) if ok else Image.new("RGB", (W, H))


os.makedirs(OUT, exist_ok=True)
want = set(sys.argv[1:])
for i, (name, shots) in enumerate(BOARDS):
    if want and name not in want:
        continue
    b = Image.new("RGB", (2 * W, 2 * H + 40), (12, 12, 14))
    d = ImageDraw.Draw(b)
    d.text((10, 12), "%02d  %s" % (i + 1, name.replace("_", " ")), fill=(255, 220, 0))
    for k, (vid, n) in enumerate(shots):
        im = frame(vid, n)
        ImageDraw.Draw(im).rectangle((0, 0, 170, 16), fill=(0, 0, 0))
        ImageDraw.Draw(im).text((4, 2), "%s  f%d" % (vid, n), fill=(255, 255, 255))
        b.paste(im, ((k % 2) * W, 40 + (k // 2) * H))
    b.save(os.path.join(OUT, "%02d_%s.jpg" % (i + 1, name)), quality=86)
    print("board", i + 1, name)
