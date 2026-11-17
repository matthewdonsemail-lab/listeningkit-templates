"""Cyberpunk opening: every crowd moment (projects/cyberpunk/open_a,c-g.png) redrawn in the intro's two other styles,
the anime ink girl (shot3.png) and the light being (shot1.png), keeping every person and the camera exactly where they
are, so all of them cycle in place behind her. open_b's versions are shot3.png and shot1.png themselves.
Writes projects/cyberpunk/styles/open_<k>_<anime|being>.png at 1920x1080."""
import concurrent.futures as cf
import json
import os
import re
import subprocess

from PIL import Image

CP = "C:/Users/0/.buzz/REPOS/listeningkit-templates/projects/cyberpunk/"
OUT = CP + "styles/"
KEEP = ("Keep the FIRST reference image's exact composition: the same locked-off camera angle from the balcony, the same "
        "railing, floor, columns and windows, and every person at exactly the same position, size and pose. 16:9, no "
        "text, no watermark.")
STYLE = {
    "anime": ("shot3", "Redraw the FIRST reference image in the exact style of the SECOND reference image: 90s anime, "
                       "every person in pure black and white ink with hard shadows, the building and marble floor in "
                       "deep electric blue, the same soft blue light shafts from the windows."),
    "being": ("shot1", "Redraw the FIRST reference image in the exact style of the SECOND reference image: a dark, "
                       "night-blue hall, and every person made of glowing electric-blue neural filaments and fine light "
                       "threads, like the being in the second image, with soft bloom, threads trailing off them across "
                       "the dark stone floor."),
}
FRAMES = ["a", "c", "d", "e", "f", "g"]


def host(path):
    out = subprocess.run(["treg", "host", path], capture_output=True, text=True).stdout
    return re.findall(r"https://treg\.to/m/\S+", out)[-1]


def gen(job):
    k, style, urls = job
    dest = OUT + "open_%s_%s.png" % (k, style)
    if os.path.exists(dest):
        return dest, "exists"
    body = {"model": "gemini-3-pro-image-preview", "size": "16:9", "resolution": "2K", "image_urls": urls,
            "prompt": STYLE[style][1] + " " + KEEP}
    r = subprocess.run(["treg", "call", "reapi.image-gen.gemini-3-pro-image", "--method", "POST", "--data",
                        json.dumps(body), "--await", "--timeout", "900"], capture_output=True, text=True)
    m = re.findall(r"https://file\.deepytb\.com/[^\"\s]+\.png", r.stdout + r.stderr)
    if not m:
        return dest, "FAIL " + (r.stdout + r.stderr)[:300].replace("\n", " ")
    tmp = dest + ".gen.png"
    subprocess.run(["curl.exe", "-sL", m[0], "-o", tmp], check=True)
    Image.open(tmp).convert("RGB").resize((1920, 1080), Image.LANCZOS).save(dest)
    os.remove(tmp)
    return dest, "ok"


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    refs = {s: host(CP + v[0] + ".png") for s, v in STYLE.items()}
    frames = {k: host(CP + "open_%s.png" % k) for k in FRAMES}
    jobs = [(k, s, [frames[k], refs[s]]) for k in FRAMES for s in STYLE]
    with cf.ThreadPoolExecutor(max_workers=12) as ex:
        for dest, status in ex.map(gen, jobs):
            print(status, dest.replace(CP, ""), flush=True)
