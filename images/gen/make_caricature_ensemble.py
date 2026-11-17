"""The caricature ensemble: images/Blue Noir Headband Portraits.png with each superimposed girl replaced by one of the
six caricatures (projects/cyberpunk/outro/portrait_0-5.png), keeping every figure's position, size, crop and angle.
Writes projects/cyberpunk/outro/ensemble.png. Through treg / Nano Banana Pro."""
import json
import re
import subprocess

ROOT = "C:/Users/0/.buzz/REPOS/listeningkit-templates/"
OUT = ROOT + "projects/cyberpunk/outro/ensemble.png"
PROMPT = (
    "The FIRST image is the composition: copy it exactly. It shows six figures superimposed on black at different "
    "sizes: a huge one cropped at the far left, a large one top centre, a smaller one lower left of centre, one lower "
    "right of centre, and a huge one cropped at the far right. Keep every figure's exact position, size, crop, head "
    "angle and the way they overlap, the same black background, the same deep blue chiaroscuro and glowing blue rim "
    "light, the same noir anime ink style. Replace each girl with one of the caricatured people from the other "
    "reference images (images 2 to 7), drawn in the same style and lit the same way: the huge macho man with the tiny "
    "head on the far left, the fat moon-faced man top centre, the gaunt long-faced man lower left of centre, the woman "
    "with the giant puffed hairdo lower right of centre, the hunched bald old man with the hooked nose, and the manic "
    "grinning wide-eyed man huge on the far right. No headbands. Faces half lost in shadow. 16:9, no text, no watermark.")


def host(path):
    out = subprocess.run(["treg", "host", path], capture_output=True, text=True).stdout
    return re.findall(r"https://treg\.to/m/\S+", out)[-1]


urls = [host(ROOT + "images/Blue Noir Headband Portraits.png")] + \
       [host(ROOT + "projects/cyberpunk/outro/portrait_%d.png" % i) for i in range(6)]
body = {"model": "gemini-3-pro-image-preview", "size": "16:9", "resolution": "2K", "image_urls": urls, "prompt": PROMPT}
r = subprocess.run(["treg", "call", "reapi.image-gen.gemini-3-pro-image", "--method", "POST", "--data", json.dumps(body),
                    "--await", "--timeout", "900"], capture_output=True, text=True)
m = re.findall(r"https://file\.deepytb\.com/[^\"\s]+\.(?:png|jpg)", r.stdout + r.stderr)
if not m:
    raise SystemExit("FAIL " + (r.stdout + r.stderr)[:300])
tmp = OUT + ".dl"
subprocess.run(["curl.exe", "-sL", m[0], "-o", tmp], check=True)
from PIL import Image  # noqa: E402
Image.open(tmp).convert("RGB").save(OUT)
import os  # noqa: E402
os.remove(tmp)
print("ok", OUT)
