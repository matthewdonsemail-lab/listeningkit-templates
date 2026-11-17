"""The opening's click inserts, like The Big Short's (projects/opening/ref/bigshort_mouse.png at 52.7 s, a hand on a
silver mouse; bigshort_key.png at 26.7 s, a finger pressing a key): the reference frames give the framing, lens and
light only. Hands only, no faces. Written to projects/opening/inserts/<name>.png via treg / Nano Banana Pro."""
import concurrent.futures as cf
import json
import os
import re
import subprocess

from PIL import Image

OP = "C:/Users/0/.buzz/REPOS/listeningkit-templates/projects/opening/"
OUT = OP + "inserts/"
LOOK = ("Late night office, lit only by a "
        "computer screen, cold blue-grey monochrome grade (The Big Short), very shallow depth of field, film grain, real "
        "photograph, cinematic 35mm film still, 16:9, ONE single image, not a grid, no text, no logos, no faces.")
SHOTS = [("mouse", "ref/bigshort_mouse.png", "Macro close-up of a man's right hand on a silver computer mouse on a dark "
          "desk, index finger pressing down on the left button, mid-click, the screen glow along the knuckles. "),
         ("enter", "ref/bigshort_key.png", "Extreme macro close-up of a fingertip pressing down hard on the Enter key of "
          "a silver laptop keyboard, the key half pressed, the rest of the keys soft and dark, the screen glow on the "
          "keys. ")]


def host(path):
    out = subprocess.run(["treg", "host", path], capture_output=True, text=True).stdout
    return re.findall(r"https://treg\.to/m/\S+", out)[-1]


def gen(job):
    name, ref, prompt = job
    dest = OUT + name + ".png"
    if os.path.exists(dest):
        return "exists " + name
    body = {"model": "gemini-3-pro-image-preview", "size": "16:9", "resolution": "2K", "prompt": prompt + LOOK}  # text only: treg hosting quota was used up
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
    with cf.ThreadPoolExecutor(max_workers=2) as ex:
        for status in ex.map(gen, SHOTS):
            print(status, flush=True)
