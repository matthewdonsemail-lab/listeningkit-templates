"""Cyberpunk: style variations of the girl's close-up (projects/cyberpunk/eyes2.png), the same composition in other
genres, using Intro 1's styles (make_variants.py), so they cut and glitch in place over each other on the eye match
cuts. Writes projects/cyberpunk/variants/eyes2/<style>.png."""
import concurrent.futures as cf
import json
import os
import re
import subprocess

# the same style lines as make_variants.py (importing it would run its whole batch)
STYLES = {
    "ps2": "a PlayStation 2 era video game cutscene render: low-polygon models, blurry low-resolution textures, "
           "glossy stiff hair mesh, simple shading, jagged edges",
    "oil": "a baroque oil painting in the style of Caravaggio: dramatic chiaroscuro, visible brush strokes, craquelure",
    "magritte": "a surrealist painting in the style of Rene Magritte: flat clean paint, one impossible element "
                "(the sky inside a silhouette, a floating object), uncanny calm",
    "clay": "a claymation stop-motion frame: plasticine figures with fingerprints in the clay, miniature handmade set",
    "ukiyoe": "a Japanese ukiyo-e woodblock print: flat colour areas, bold outlines, paper grain, Prussian blue",
}


def host(path):
    out = subprocess.run(["treg", "host", path], capture_output=True, text=True).stdout
    return re.findall(r"https://treg\.to/m/\S+", out)[-1]

ROOT = "C:/Users/0/.buzz/REPOS/listeningkit-templates/projects/cyberpunk/"
OUT = ROOT + "variants/eyes2/"
PICK = ["ps2", "oil", "magritte", "clay", "ukiyoe"]
KEEP = ("Recreate the reference image in this style: {style}. Keep the exact composition of the reference: the same "
        "camera angle from above and to the left, the same framing, the same head tilt and turn, her eyes looking up "
        "and to the left into the lens, the eyes, nose, mouth, hair and headphones at the same positions and sizes in "
        "the frame, the same light direction. Same girl: long wavy black hair, blunt bangs, white over-ear headphones. "
        "16:9, no text, no watermark.")


def gen(style, url):
    dest = OUT + style + ".png"
    if os.path.exists(dest):
        return dest, "exists"
    body = {"model": "gemini-3-pro-image-preview", "size": "16:9", "resolution": "2K", "image_urls": [url],
            "prompt": KEEP.format(style=STYLES[style])}
    r = subprocess.run(["treg", "call", "reapi.image-gen.gemini-3-pro-image", "--method", "POST", "--data",
                        json.dumps(body), "--await", "--timeout", "900"], capture_output=True, text=True)
    m = re.findall(r"https://file\.deepytb\.com/[^\"\s]+\.png", r.stdout + r.stderr)
    if not m:
        return dest, "FAIL " + (r.stdout + r.stderr)[:300].replace("\n", " ")
    subprocess.run(["curl.exe", "-sL", m[0], "-o", dest], check=True)
    return dest, "ok"


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    url = host(ROOT + "eyes2.png")
    with cf.ThreadPoolExecutor(max_workers=5) as ex:
        for dest, status in ex.map(lambda s: gen(s, url), PICK):
            print(status, dest.replace(ROOT, ""), flush=True)
