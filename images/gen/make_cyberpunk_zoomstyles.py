"""Cyberpunk outro: the 12 frames of the push into the girl in the Nous logo (projects/cyberpunk/outro/zoomref/
zoom_00-11.png, frames 28-39 of the outro) redrawn one by one, each in a random style and its own scene, keeping that
frame's composition exactly (her position, size, pose and the camera), so they match-cut one into the next.
Then 12 frames of the back of her head in the same framings, each from its front frame, the last one in blue
chiaroscuro on black (the shot that holds before the caricature busts).
Writes projects/cyberpunk/outro/front_00-11.png and back_00-11.png. Through treg / Nano Banana Pro."""
import concurrent.futures as cf
import json
import os
import re
import subprocess
import sys

from PIL import Image

OUT = "C:/Users/0/.buzz/REPOS/listeningkit-templates/projects/cyberpunk/outro/"
STYLES = [
    "a hyperrealistic 35mm film photograph of a real young woman in a dim city street at night, neon reflections",
    "a PlayStation 2 era video game cutscene render in an empty school corridor: low-polygon, blurry textures",
    "a baroque oil painting in the style of Caravaggio, a dark room lit by one candle, visible brush strokes",
    "a surrealist Magritte painting, a calm blue sky with clouds behind her, flat clean paint",
    "a claymation stop-motion frame on a miniature handmade set, plasticine with fingerprints",
    "a Japanese ukiyo-e woodblock print with a great wave behind her, flat colours, bold outlines, paper grain",
    "a 1-bit MacPaint image, dithered patterns, pixelated, black and white only",
    "a watercolour painting on rough paper in a rainy garden, soft bleeding colours",
    "a stained glass window, thick black leading, glowing jewel colours",
    "a pop-art comic panel with Ben-Day dots and a bright yellow and red background",
    "a graphite pencil sketch on cream paper, cross-hatching, an unfinished background",
    "a noir anime illustration in deep blue and black with glowing blue rim light, a dark city skyline behind her",
]
LAST_BACK = "a noir anime illustration in deep blue chiaroscuro with glowing blue rim light on a pure black background"
FRONT = ("Redraw the reference image as {style}. Keep the reference's composition EXACTLY: the girl at the same position "
         "and size in the frame, the same pose, the same head angle, the same crop and camera, so it cuts straight from "
         "the reference. Leave out the NOUS lettering and the rounded frame border of the reference: put her in this "
         "style's own scene instead of on black. The same girl: blunt bangs, long hair, a headband. 16:9, no text, no "
         "watermark, no border.")
BACK = ("The same shot as the reference, the same camera, the same crop, the girl at exactly the same position and size, "
        "but she has turned fully round: we see the back of her head, her long hair and the headband from behind, her "
        "face hidden, looking away into the scene. Drawn as {style}. 16:9, no text, no watermark, no border.")


def host(path):
    out = subprocess.run(["treg", "host", path], capture_output=True, text=True).stdout
    return re.findall(r"https://treg\.to/m/\S+", out)[-1]


def gen(job):
    name, urls, prompt = job
    dest = OUT + name + ".png"
    if os.path.exists(dest):
        return dest, "exists"
    body = {"model": "gemini-3-pro-image-preview", "size": "16:9", "resolution": "2K", "image_urls": urls,
            "prompt": prompt}
    r = subprocess.run(["treg", "call", "reapi.image-gen.gemini-3-pro-image", "--method", "POST", "--data",
                        json.dumps(body), "--await", "--timeout", "900"], capture_output=True, text=True)
    m = re.findall(r"https://file\.deepytb\.com/[^\"\s]+\.(?:png|jpg)", r.stdout + r.stderr)
    if not m:
        return dest, "FAIL " + (r.stdout + r.stderr)[:300].replace("\n", " ")
    tmp = dest + ".dl"
    subprocess.run(["curl.exe", "-sL", m[0], "-o", tmp], check=True)
    Image.open(tmp).convert("RGB").save(dest)
    os.remove(tmp)
    return dest, "ok"


def run(jobs):
    with cf.ThreadPoolExecutor(max_workers=12) as ex:
        for dest, status in ex.map(gen, jobs):
            print(status, dest.replace(OUT, ""), flush=True)


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if which in ("all", "front"):
        run([("front_%02d" % i, [host(OUT + "zoomref/zoom_%02d.png" % i)], FRONT.format(style=STYLES[i]))
             for i in range(12)])
    if which in ("all", "back"):
        run([("back_%02d" % i, [host(OUT + "front_%02d.png" % i)],
              BACK.format(style=LAST_BACK if i == 11 else STYLES[i])) for i in range(12)])
