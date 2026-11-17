"""8 style variations of every story still in Intro 1 (same composition, different genre), via treg / Nano Banana Pro.
Hosts each source still, runs the generations in parallel, downloads to images/variants/<still>/<style>.png."""
import concurrent.futures as cf
import json
import os
import re
import subprocess
import urllib.request

ROOT = "C:/Users/0/.buzz/REPOS/listeningkit-templates/images/"
STILLS = ["shadow/01_log_ingests", "shadow/02_every_conversation", "beats/03_youve_ever_had",
          "shadow/05_a_voice_profile", "shadow/06_of_you", "beats/07_local_models", "shadow/08_re_rank",
          "beats/09_embed", "beats/10_vector_search", "beats/11_the_way_you_actually", "shadow/12_talk",
          "shadow/13_time_back", "Blue Noir Only Moat"]
STYLES = {
    "hyperreal": "a hyperrealistic 35mm film photograph with real people and real materials, natural skin texture",
    "ps2": "a PlayStation 2 era video game cutscene render: low-polygon models, blurry low-resolution textures, "
           "glossy stiff hair mesh, simple shading, jagged edges",
    "oil": "a baroque oil painting in the style of Caravaggio: dramatic chiaroscuro, visible brush strokes, craquelure",
    "magritte": "a surrealist painting in the style of Rene Magritte: flat clean paint, one impossible element "
                "(the sky inside a silhouette, a floating object), uncanny calm",
    "clay": "a claymation stop-motion frame: plasticine figures with fingerprints in the clay, miniature handmade set",
    "ukiyoe": "a Japanese ukiyo-e woodblock print: flat colour areas, bold outlines, paper grain, Prussian blue",
    "macpaint": "a 1-bit black and white early Macintosh MacPaint image: dithered patterns, pixelated, no greys",
    "crtcollage": "a blue CRT phosphor image built from glowing pixels, with rectangular cut-out patches of the "
                  "face (one eye enlarged, the mouth shifted) pasted back slightly misaligned, like a glitch collage",
}
KEEP = ("Recreate the reference image in this style: {style}. Keep the exact composition of the reference: same "
        "framing, camera angle, positions and sizes of everything in the frame, same pose and gaze, same light "
        "direction. Same girl (long wavy black hair, blunt bangs, white headband). 16:9, no text, no watermark.")


def host(path):
    out = subprocess.run(["treg", "host", path], capture_output=True, text=True).stdout
    return re.findall(r"https://treg\.to/m/\S+", out)[-1]


def gen(job):
    still, url, style = job
    stem = still.split("/")[-1].replace(" ", "_")
    dest = ROOT + "variants/%s/%s.png" % (stem, style)
    if os.path.exists(dest):
        return dest, "exists"
    body = {"model": "gemini-3-pro-image-preview", "size": "16:9", "resolution": "2K", "image_urls": [url],
            "prompt": KEEP.format(style=STYLES[style])}
    r = subprocess.run(["treg", "call", "reapi.image-gen.gemini-3-pro-image", "--method", "POST", "--data",
                        json.dumps(body), "--await", "--timeout", "900"], capture_output=True, text=True)
    m = re.findall(r"https://file\.deepytb\.com/[^\"\s]+\.png", r.stdout + r.stderr)
    if not m:
        return dest, "FAIL " + (r.stdout + r.stderr)[:200].replace("\n", " ")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    # the image host refuses urllib (403); curl works
    subprocess.run(["curl.exe", "-sL", m[0], "-o", dest], check=True)
    return dest, "ok"


urls = {s: host(ROOT + s + ".png") for s in STILLS}
jobs = [(s, urls[s], st) for s in STILLS for st in STYLES]
def safe(job):
    try:
        return gen(job)
    except Exception as e:  # one failure must not stop the batch
        return job[0], "FAIL %s" % e


with cf.ThreadPoolExecutor(max_workers=16) as ex:
    for dest, status in ex.map(safe, jobs):
        print(status, dest.replace(ROOT, ""), flush=True)

