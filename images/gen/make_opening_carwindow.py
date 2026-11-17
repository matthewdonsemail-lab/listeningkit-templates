"""The Pioneer Building seen from the back seat of a moving car, through the rear side window, with motion blur, in the camera language of the A24 teaser
(projects/opening/ref/gptref.mp4). The 2012 Wikimedia photo is the reference for the building.
Written to projects/opening/gpt3/carwindow.png via treg / Nano Banana Pro."""
import json
import os
import re
import subprocess

from PIL import Image

OP = "C:/Users/0/.buzz/REPOS/listeningkit-templates/projects/opening/"
DEST = OP + "gpt3/carwindow_moving.png"
PROMPT = ("Shot from the BACK SEAT of a MOVING car driving past, looking out through the rear side window at the "
          "building in the reference photo across the street as it slides by: the three-storey grey-painted timber "
          "Italianate building on a corner, tall white sash windows with dark grey trim, a red band under the cornice, "
          "PIONEER BUILDING painted in red on the corner, street trees. In the foreground, soft and dark: the back of "
          "the front seat and headrest, the rear door's window frame and a passenger's shoulder at the edge of frame. "
          "The car is moving: horizontal motion blur streaking the trees, lamp posts and parked cars nearest the window, "
          "the building further away a little less blurred but still smeared sideways, faint reflections on the glass. "
          "Golden-hour 2020, warm low sun flaring through, observational A24 documentary look, fine film grain. Real "
          "photograph, cinematic 35mm film still, 16:9, ONE single image, not a grid, no other text.")


def host(path):
    out = subprocess.run(["treg", "host", path], capture_output=True, text=True).stdout
    return re.findall(r"https://treg\.to/m/\S+", out)[-1]


body = {"model": "gemini-3-pro-image-preview", "size": "16:9", "resolution": "2K",
        "image_urls": [host(OP + "gpt3/ref/pioneer_building_2012.jpg")], "prompt": PROMPT}
r = subprocess.run(["treg", "call", "reapi.image-gen.gemini-3-pro-image", "--method", "POST", "--data", json.dumps(body),
                    "--await", "--timeout", "900"], capture_output=True, text=True)
m = re.findall(r"https://file\.deepytb\.com/[^\"\s]+\.(?:png|jpg)", r.stdout + r.stderr)
assert m, (r.stdout + r.stderr)[:400]
raw = OP + "gpt3/carwindow_moving_raw" + os.path.splitext(m[0])[1]
subprocess.run(["curl.exe", "-sL", m[0], "-o", raw], check=True)
Image.open(raw).convert("RGB").resize((1920, 1080), Image.LANCZOS).save(DEST)
print("ok", DEST)
