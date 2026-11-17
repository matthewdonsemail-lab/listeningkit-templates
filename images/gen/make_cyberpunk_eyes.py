"""Cyberpunk: an extreme close-up of the eyes for each of the three overhead shots (projects/cyberpunk/shot1-3.png),
in that shot's own style, framed the same way every time so the cuts between them match on the eyes.
Hosts each shot with treg, runs the three generations in parallel, downloads to projects/cyberpunk/eyes<n>.png."""
import concurrent.futures as cf
import json
import os
import re
import subprocess

ROOT = "C:/Users/0/.buzz/REPOS/listeningkit-templates/projects/cyberpunk/"
FRAME = ("Camera, identical for every image in this set: the SAME high camera angle as the reference image, looking "
         "steeply DOWN from the balcony above onto the figure below, now zoomed in very close on the face, so we see "
         "the top of the head and the face foreshortened from above as the figure looks up toward the camera. "
         "Framing: the point between the eyes exactly at the centre of the frame, the eyes on one line through the "
         "centre, together spanning the middle half of the frame width; the floor of the reference just visible at "
         "the edges far below. 16:9, no text, no watermark, no logos, no symbols.")
SHOTS = {
    "eyes1": ("shot1", "The same being as the reference image: an amalgamation of glowing electric blue neural "
                       "filaments, a brain-like knot of light on a thin luminous spine, with no human face and no eyes. "
                       "Zoomed in close from above on the knot of its head: thousands of fine light threads tangling "
                       "into a dense core with a white-hot centre exactly at the centre of the frame, threads drifting "
                       "off it across the dark stone floor far below. Same deep blue palette, black background and "
                       "soft bloom as the reference."),
    "eyes2": ("shot2", "The same young woman as the reference image, a real photograph, 35mm film, natural skin "
                       "texture: long wavy black hair with blunt bangs, the white over-ear headphones, cold daylight "
                       "from tall windows, the muted grey palette of the reference, slight film grain. This is the "
                       "reference shot zoomed in on her face: the SAME camera position and angle as the reference, "
                       "high up on the balcony to the upper left, looking down at her at an angle (not straight down "
                       "from overhead). Her face is upright, exactly as in the reference: her head tilted back and "
                       "turned a little to the left, her eyes looking up and to the left straight into the lens, the "
                       "same expression as the reference. The grey marble floor behind her, out of focus. Zoomed in "
                       "tight on her eyes: the two eyes span the middle 45 percent of the frame width, bangs at the top "
                       "edge, nose at the bottom edge.", "own"),
    "eyes3": (["eyes2", "shot3"], "Redraw the FIRST reference image (a photo close-up) as the anime girl in the "
                       "SECOND reference image. Keep the first image's exact composition: the same camera angle from "
                       "above and to the left, the same head tilt and turn, her eyes looking up and to the left into "
                       "the lens, the same framing and the same position and size of her eyes, nose, mouth and hair "
                       "in the frame. Draw her exactly like the second image: pure black and white ink, no colour on "
                       "her at all, solid black hair with blunt bangs, the white headband instead of headphones, white "
                       "skin with black line work and hard black shadows, large anime eyes with white highlights. "
                       "The background behind her is the deep blue marble floor of the second image, out of focus.",
              "own"),
}


def host(path):
    out = subprocess.run(["treg", "host", path], capture_output=True, text=True).stdout
    return re.findall(r"https://treg\.to/m/\S+", out)[-1]


OWN = ("Framing: the point between the eyes exactly at the centre of the frame. 16:9, no text, no watermark, no "
       "logos, no symbols.")


def gen(job):
    name, url, prompt, own = job
    dest = ROOT + name + ".png"
    if os.path.exists(dest):
        return dest, "exists"
    body = {"model": "gemini-3-pro-image-preview", "size": "16:9", "resolution": "2K", "image_urls": url,
            "prompt": prompt + " " + (OWN if own else FRAME)}
    json.dump(body, open(os.path.join(os.path.dirname(__file__), "cyberpunk_" + name + ".json"), "w"))
    r = subprocess.run(["treg", "call", "reapi.image-gen.gemini-3-pro-image", "--method", "POST", "--data",
                        json.dumps(body), "--await", "--timeout", "900"], capture_output=True, text=True)
    m = re.findall(r"https://file\.deepytb\.com/[^\"\s]+\.png", r.stdout + r.stderr)
    if not m:
        return dest, "FAIL " + (r.stdout + r.stderr)[:300].replace("\n", " ")
    subprocess.run(["curl.exe", "-sL", m[0], "-o", dest], check=True)
    return dest, "ok"


todo = {name: v for name, v in SHOTS.items() if not os.path.exists(ROOT + name + ".png")}
urls = {name: [host(ROOT + s + ".png") for s in (v[0] if isinstance(v[0], list) else [v[0]])] for name, v in todo.items()}
jobs = [(name, urls[name], v[1], len(v) > 2) for name, v in todo.items()]
with cf.ThreadPoolExecutor(max_workers=3) as ex:
    for dest, status in ex.map(gen, jobs):
        print(status, dest.replace(ROOT, ""), flush=True)
