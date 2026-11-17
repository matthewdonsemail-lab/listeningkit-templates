"""The founder (the opening's original cast, projects/opening/cast/cast.png) at his laptop, framed and lit like shot 3
of The Big Short style sheet (projects/opening/ref/bigshort_02.png, described in words only so no face carries over): a tight three-quarter close-up, off-centre,
cold blue monitor light, blinds behind. Written to projects/opening/cast3/founder_laptop.png via treg / Nano Banana Pro."""
import json
import os
import re
import subprocess

from PIL import Image

OP = "C:/Users/0/.buzz/REPOS/listeningkit-templates/projects/opening/"
DEST = OP + "cast3/founder_laptop.png"
PROMPT = ("The FOUNDER from the first reference image (slim man, mid-30s, short dark-blond hair, grey crew-neck sweater): "
          "exactly his face, hair and clothes, nobody else's. "
          "Tight three-quarter close-up of him sitting at his laptop late at night, staring "
          "intently at the screen just off camera left, framed off-centre, his face lit cold blue-white by the monitor, "
          "window blinds and dark office blurred behind, cold blue-grey monochrome grade, shallow depth of field, film "
          "grain. Real photograph, cinematic 35mm film still, 16:9, ONE single image, not a grid, no text, no logos.")


def host(path):
    out = subprocess.run(["treg", "host", path], capture_output=True, text=True).stdout
    return re.findall(r"https://treg\.to/m/\S+", out)[-1]


os.makedirs(os.path.dirname(DEST), exist_ok=True)
body = {"model": "gemini-3-pro-image-preview", "size": "16:9", "resolution": "2K",
        "image_urls": [host(OP + "cast/cast.png")], "prompt": PROMPT}
r = subprocess.run(["treg", "call", "reapi.image-gen.gemini-3-pro-image", "--method", "POST", "--data", json.dumps(body),
                    "--await", "--timeout", "900"], capture_output=True, text=True)
m = re.findall(r"https://file\.deepytb\.com/[^\"\s]+\.(?:png|jpg)", r.stdout + r.stderr)
assert m, (r.stdout + r.stderr)[:400]
raw = DEST.replace(".png", "_raw" + os.path.splitext(m[0])[1])
subprocess.run(["curl.exe", "-sL", m[0], "-o", raw], check=True)
Image.open(raw).convert("RGB").resize((1920, 1080), Image.LANCZOS).save(DEST)
print("ok", DEST)
