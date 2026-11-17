"""The launch film's intro, before cyberpunk: the creation of AI, sunny and golden like the opening of the Edgerunners
2 trailer (its warm establishing city). The people who built it, the data centre, GPT-3, the first reply, then AI
reaching everyone in the sun. Text on screens and boards is left out of the stills and added as editable layers.
Written to projects/opening/creation/<name>.png at 1920x1080. treg / Nano Banana Pro, as make_opening_dawn.py; the
golden dawn hall (projects/opening/dawn_crowd.png) is the reference for the light and the grade."""
import concurrent.futures as cf
import json
import os
import re
import subprocess

from PIL import Image

OP = "C:/Users/0/.buzz/REPOS/listeningkit-templates/projects/opening/"
OUT = OP + "creation/"
LOOK = ("Warm golden-hour sunlight, long soft sunbeams, dust glowing in the light, warm gold and amber grade, hopeful "
        "and bright, the same light and colour as the reference image (use it for light and grade only, not its "
        "place). Real photograph, cinematic 35mm film still, shallow depth of field, 16:9, ONE single image, not a "
        "grid. No readable text, no logos, no brand names anywhere.")
SHOTS = [
    ("city", "Wide establishing shot of a city of glass towers and a big low data centre campus at golden hour, the "
     "sun low and blazing between the towers, warm haze, lens flare, seen from a high hill."),
    ("aisle", "Inside a data centre: a long aisle of tall black server racks with tiny blinking lights, warm golden "
     "sunlight pouring in from high windows at the end of the aisle in long beams, haze in the air."),
    ("engineers", "Two engineers at desks in a sunlit open-plan office late in the day, leaning in to large monitors "
     "showing a falling line graph, coffee cups, golden light through the windows across them."),
    ("board", "A large blank whiteboard covered in hand-drawn diagrams of boxes and arrows and neural network layers, "
     "with a large empty space in the middle of it, sunlight falling across it, a marker on the ledge."),
    ("typing", "Close-up of a person's hands typing on a laptop keyboard, a plain white text box glowing on the screen, "
     "golden sunlight across the hands and keys."),
    ("reply", "Extreme close-up of a computer screen in a dim room: a few lines of glowing text appearing on a dark "
     "background, the cursor blinking, warm sun flare across the glass, the pixels just visible."),
    ("team", "A small team of researchers crowded round one monitor in a sunlit office, faces lit by the screen and "
     "the sun, amazed, one with a hand over her mouth, one laughing, pure wonder."),
    ("servers", "Macro shot of glowing fibre-optic cables and server lights, warm gold and white points of light, "
     "sun flare, shallow depth of field, almost abstract."),
    ("street", "A sunlit city street at golden hour, people walking and stopping to look at their phones, smiling, "
     "relaxed, warm light and long shadows, the city glowing."),
    ("sun", "Close-up of a woman leaning back in a chair by a sunny window, eyes closed, smiling, the warm sun on her "
     "face, a laptop closed on the table, at ease, time on her hands."),
]


def host(path):
    out = subprocess.run(["treg", "host", path], capture_output=True, text=True).stdout
    return re.findall(r"https://treg\.to/m/\S+", out)[-1]


def gen(job):
    name, prompt = job
    dest = OUT + name + ".png"
    if os.path.exists(dest):
        return "exists " + name
    body = {"model": "gemini-3-pro-image-preview", "size": "16:9", "resolution": "2K", "image_urls": [REF],
            "prompt": prompt + " " + LOOK}
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
    REF = host(OP + "dawn_crowd.png")
    with cf.ThreadPoolExecutor(max_workers=5) as ex:
        for status in ex.map(gen, SHOTS):
            print(status, flush=True)
