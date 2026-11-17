"""B-roll cutaways in the opening's marble hall (projects/opening/), so the scene is set from inside the hall and not
only from the balcony: dust, the windows, feet, hands, faces, the marble that cracks. Each is drawn with
dawn_crowd.png as the reference for the building, the light and the grade, so they cut together.
Written to projects/opening/broll/<name>.png at 1920x1080. treg / Nano Banana Pro, as make_opening_dawn.py."""
import concurrent.futures as cf
import json
import os
import re
import subprocess

from PIL import Image

OP = "C:/Users/0/.buzz/REPOS/listeningkit-templates/projects/opening/"
OUT = OP + "broll/"
SAME = ("Inside the SAME grand marble hall as the reference image, at the same moment: the same polished grey-white "
        "marble with dark veins, the same tall windows, the same warm golden dawn sunlight in long beams, the same "
        "warm gold and amber grade. Real photograph, cinematic 35mm film still, shallow depth of field, 16:9, ONE "
        "single image, not a grid, no text, no watermark.")
COLD = ("Inside the SAME grand marble hall as the reference image, but it is cold night now: deep blue chiaroscuro, "
        "hard blue rim light, the warm light gone. Real photograph, cinematic 35mm film still, shallow depth of field, "
        "16:9, ONE single image, not a grid, no text, no watermark.")
SHOTS = [  # (name, reference, prompt)
    ("dust", "dawn_crowd", "Macro close-up of dust motes floating and glittering in one shaft of golden sunlight, "
     "the hall and the window soft and out of focus behind, almost dark around the beam. " + SAME),
    ("window", "dawn_crowd", "Looking straight up at one of the tall windows from the floor, the low sun blazing "
     "through the panes, a warm lens flare and light rays spilling down, the stone frame dark around it. " + SAME),
    ("feet", "dawn_crowd", "Low angle at floor level: several people's feet and legs walking across the polished "
     "marble, their reflections in it, long shadows, sunbeams across the floor, motion blur on the steps. " + SAME),
    ("phone", "dawn_crowd", "Close-up from the side of a young man's hands holding a phone, head bowed over it, the "
     "screen glow on his face, a sunbeam just catching his shoulder. " + SAME),
    ("lookup", "dawn_lookup", "Close-up of a young woman's face tilted up toward the windows, eyes wide, the golden "
     "light falling across her face and catching in her eyes, in awe, her phone lowered at the edge of frame. " + SAME),
    ("veins", "dawn_crowd", "Extreme close-up of the polished marble floor: the dark veins running through the "
     "grey-white stone, a sunbeam lying across it, a shoe just leaving the edge of frame. " + SAME),
    ("veins_cracked", "split_cold", "Extreme close-up of the polished marble floor, the dark veins running through "
     "the grey-white stone, and a deep jagged black crack has split the marble along one of the veins, chips of "
     "stone at its edges. " + COLD),
    ("turn", "split_cold", "Close-up of a man turning his head away over his shoulder, wary and distrustful, half his "
     "face in deep shadow, blue rim light on his cheek, another figure blurred behind him. " + COLD),
    ("railing", "dawn_crowd", "Shallow-focus shot along the carved stone balcony railing, the balusters sharp in the "
     "foreground, the bright marble hall and the small figures crossing it far below, soft and golden. " + SAME),
]


def host(path):
    out = subprocess.run(["treg", "host", path], capture_output=True, text=True).stdout
    return re.findall(r"https://treg\.to/m/\S+", out)[-1]


def gen(job):
    name, ref, prompt = job
    dest = OUT + name + ".png"
    if os.path.exists(dest):
        return "exists " + name
    body = {"model": "gemini-3-pro-image-preview", "size": "16:9", "resolution": "2K",
            "image_urls": [URLS[ref]], "prompt": prompt}
    r = subprocess.run(["treg", "call", "reapi.image-gen.gemini-3-pro-image", "--method", "POST", "--data",
                        json.dumps(body), "--await", "--timeout", "900"], capture_output=True, text=True)
    m = re.findall(r"https://file\.deepytb\.com/[^\"\s]+\.(?:png|jpg)", r.stdout + r.stderr)
    if not m:
        return "FAIL %s %s" % (name, (r.stdout + r.stderr)[:300].replace("\n", " "))
    raw = OUT + name + "_raw" + os.path.splitext(m[0])[1]
    subprocess.run(["curl.exe", "-sL", m[0], "-o", raw], check=True)
    Image.open(raw).convert("RGB").resize((1920, 1080), Image.LANCZOS).save(dest)
    return "ok " + name


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    URLS = {r: host(OP + r + ".png") for r in {s[1] for s in SHOTS}}
    with cf.ThreadPoolExecutor(max_workers=5) as ex:
        for status in ex.map(gen, SHOTS):
            print(status, flush=True)
