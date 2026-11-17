"""The launch film's new opening, before the split (textAnimations/NARRATIVE_SCRIPT.md, lines 1-4): the same marble hall
from above as cyberpunk's opening (projects/cyberpunk/open_a.png), locked to its composition, in warm dawn light.
Chained so the people stay put from still to still:
  dawn_empty   open_a's hall, warm gold dawn, almost empty, long sunbeams across the floor
  dawn_crowd   the same, people walking across it, heads down on their phones
  dawn_light   dawn_crowd with every person a glowing gold light-being, same people, same places
  dawn_lookup  dawn_crowd with everyone stopped, phones lowered, looking up into the light
  split_cold   dawn_lookup gone cold blue night, a black crack through the marble, people turned away from each other
Written to projects/opening/<name>.png at 1920x1080. treg / Nano Banana Pro, as make_cyberpunk_opening.py."""
import json
import os
import re
import subprocess

from PIL import Image

ROOT = "C:/Users/0/.buzz/REPOS/listeningkit-templates/projects/"
OUT = ROOT + "opening/"
LOCK = ("This is the SAME locked-off camera shot as the reference image: identical camera position, high overhead angle, "
        "lens and framing, the same stone balcony railing blurred in the bottom-left foreground, the same marble floor "
        "with the same veins, the same column base at the top, the same tall windows casting light. Real photograph, "
        "35mm film, 16:9, ONE single image, not a grid, no text, no watermark.")
SHOTS = [  # (name, reference still, prompt)
    ("dawn_empty", ROOT + "cyberpunk/open_a.png",
     "The hall at dawn, almost empty: only two or three people far apart. Warm golden early-morning sunlight pours "
     "through the tall windows in long soft beams across the marble, dust glowing in the beams, warm gold and amber "
     "grade, gentle and hopeful."),
    ("dawn_crowd", OUT + "dawn_empty.png",
     "The same golden dawn light and beams, now with a crowd of about twelve people walking across the hall in "
     "different directions, mid-stride, most of them looking down at their phones. The people are in the same places "
     "as the people in the reference where there are people, plus more."),
    ("dawn_light", OUT + "dawn_crowd.png",
     "Exactly the same people in exactly the same positions, poses and sizes, but every person is now a glowing being "
     "made of warm golden light: translucent, radiant, softly blooming, their outlines and phones still readable. The "
     "hall, floor and beams are unchanged."),
    ("dawn_lookup", OUT + "dawn_crowd.png",
     "Exactly the same people in the same positions and sizes, but every one of them has stopped walking: they stand "
     "still, phones lowered, faces turned up toward the windows and the light, lit warm gold, in awe. The hall, "
     "floor and beams are unchanged."),
    ("split_cold", OUT + "dawn_lookup.png",
     "Exactly the same people in the same positions and sizes, but it is now cold night: deep blue chiaroscuro, the "
     "warm light gone, hard blue rim light. A deep jagged black crack runs right across the marble floor from the top "
     "right corner to the bottom left, following the marble's veins, splitting the hall in two. The people on either "
     "side have turned away from each other, wary, looking over their shoulders."),
]


def host(path):
    out = subprocess.run(["treg", "host", path], capture_output=True, text=True).stdout
    return re.findall(r"https://treg\.to/m/\S+", out)[-1]


def gen(name, ref, prompt):
    dest = OUT + name + ".png"
    if os.path.exists(dest):
        return "exists"
    body = {"model": "gemini-3-pro-image-preview", "size": "16:9", "resolution": "2K", "image_urls": [host(ref)],
            "prompt": prompt + " " + LOCK}
    r = subprocess.run(["treg", "call", "reapi.image-gen.gemini-3-pro-image", "--method", "POST", "--data",
                        json.dumps(body), "--await", "--timeout", "900"], capture_output=True, text=True)
    m = re.findall(r"https://file\.deepytb\.com/[^\"\s]+\.(?:png|jpg)", r.stdout + r.stderr)
    if not m:
        return "FAIL " + (r.stdout + r.stderr)[:300].replace("\n", " ")
    raw = OUT + name + "_raw" + os.path.splitext(m[0])[1]
    subprocess.run(["curl.exe", "-sL", m[0], "-o", raw], check=True)
    Image.open(raw).convert("RGB").resize((1920, 1080), Image.LANCZOS).save(dest)
    return "ok"


if __name__ == "__main__":
    import sys
    os.makedirs(OUT, exist_ok=True)
    only = sys.argv[1:]
    for name, ref, prompt in SHOTS:  # in order: each one is drawn from the one before
        if only and name not in only:
            continue
        print(gen(name, ref, prompt), name, flush=True)
