"""Cyberpunk opening: the realistic overhead (projects/cyberpunk/shot2.png) as three moments of one locked-off shot.
A: before she arrives, her spot empty, everyone else elsewhere walking toward it. B: shot2 itself, her standing there.
C: a few seconds later, her still in the same spot and pose, everyone else moved on. Then all three are written at
1920x1080 (open_a/b/c.png) so they cut together exactly. Generated through treg / Nano Banana Pro like make_variants.py."""
import concurrent.futures as cf
import json
import os
import re
import subprocess

from PIL import Image

CP = "C:/Users/0/.buzz/REPOS/listeningkit-templates/projects/cyberpunk/"
LOCK = ("This is the SAME locked-off camera shot as the reference image: identical camera position, angle, lens and "
        "framing, the same balcony railing in the foreground, the same marble floor, columns, windows, light, shadows "
        "and colour grade, everything in the building exactly where it is in the reference. Only the people change. "
        "Real photograph, 35mm film, 16:9, no text, no watermark.")
SHOTS = {
    "open_a_gen": "A few seconds BEFORE the reference moment: the young woman with the white headphones is NOT in the "
                  "frame at all; the spot in the centre of the floor where she stands in the reference is empty marble. "
                  "All the other people are in different positions from the reference, mid-stride, walking across the "
                  "hall, several of them heading toward that centre spot.",
    "open_c_gen": "A few seconds AFTER the reference moment: the young woman with the white headphones, black hoodie "
                  "and backpack is still standing exactly where she is in the reference, the same size, the same pose, "
                  "looking up at the camera. All the other people have moved to different positions, mid-stride, "
                  "walking past and around her across the hall.",
}
STAY = ("The young woman with the white headphones, black hoodie and backpack is still standing exactly where she is in "
        "the reference, the same size, the same pose, looking up at the camera; she has not moved at all. ")
for name, crowd in [
    ("open_d_gen", "Later still: a different crowd, two people passing close by on her left and one on her right, others "
                   "spread far across the hall, everyone mid-stride, motion blur on their legs."),
    ("open_e_gen", "Later still: a busier moment, a group of four walking past just below her, a man with a phone "
                   "crossing above her, people near the columns at the top, everyone mid-stride."),
    ("open_f_gen", "Later still: a quieter moment, only three other people in the hall, far from her, one walking out "
                   "of frame at the bottom right, one at the top left, one by the column."),
    ("open_g_gen", "Later still: people streaming past her on both sides in a long diagonal line from the top right to "
                   "the bottom left, close to her, with motion blur, as if she is the only still point in the hall."),
]:
    SHOTS[name] = STAY + crowd


def host(path):
    out = subprocess.run(["treg", "host", path], capture_output=True, text=True).stdout
    return re.findall(r"https://treg\.to/m/\S+", out)[-1]


def gen(name, url):
    dest = CP + name + ".png"
    if os.path.exists(dest):
        return dest, "exists"
    body = {"model": "gemini-3-pro-image-preview", "size": "16:9", "resolution": "2K", "image_urls": [url],
            "prompt": SHOTS[name] + " " + LOCK}
    r = subprocess.run(["treg", "call", "reapi.image-gen.gemini-3-pro-image", "--method", "POST", "--data",
                        json.dumps(body), "--await", "--timeout", "900"], capture_output=True, text=True)
    m = re.findall(r"https://file\.deepytb\.com/[^\"\s]+\.png", r.stdout + r.stderr)
    if not m:
        return dest, "FAIL " + (r.stdout + r.stderr)[:300].replace("\n", " ")
    subprocess.run(["curl.exe", "-sL", m[0], "-o", dest], check=True)
    return dest, "ok"


if __name__ == "__main__":
    url = host(CP + "shot2.png")
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        for dest, status in ex.map(lambda n: gen(n, url), SHOTS):
            print(status, dest.replace(CP, ""), flush=True)
    for src, dst in [("open_a_gen", "open_a"), ("shot2", "open_b"), ("open_c_gen", "open_c"), ("open_d_gen", "open_d"),
                     ("open_e_gen", "open_e"), ("open_f_gen", "open_f"), ("open_g_gen", "open_g")]:
        if os.path.exists(CP + src + ".png"):
            Image.open(CP + src + ".png").convert("RGB").resize((1920, 1080), Image.LANCZOS).save(CP + dst + ".png")
            print("wrote", dst + ".png")
