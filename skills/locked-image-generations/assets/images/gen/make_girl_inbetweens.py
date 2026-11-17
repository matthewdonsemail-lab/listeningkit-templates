"""In-between shots of the stamp girl in the lighting of matt's 1:05 reference (matt, 2026-11-15): the reference
(projects/opening/ref/yt_line/lighting/l_NN.png) goes from a small figure far off, to the figure turning, to a close-up
of the head with one eye and part of the face caught by the light. The same progression with her (images/rotating,
projects/stamp/s2_stand.png, projects/cyberpunk/outro/stamp_girl_yellow.png: long wavy hair, blunt bangs, the white
headband, the puffed-sleeve dress), so between the far shot and the close one she can be cut to, face partly seen.
Flat three-tone like the reference (backdrop, silhouette, hard light), so make_yellow_silhouette.py-style recolouring
to yellow and blue is a straight colour swap.
Through Google's Gemini 3 Pro Image (google-ai.image-gen.gemini-3-pro-image, about $0.15 each), references inline.
Writes projects/cyberpunk/outro/inbetween/<shot>.png (1920x1080). Skips existing.
  python images/gen/make_girl_inbetweens.py [shot ...]"""
import base64
import concurrent.futures as cf
import io
import json
import os
import subprocess
import sys

from PIL import Image

REPO = "C:/Users/0/.buzz/REPOS/listeningkit-templates/"
OUT = REPO + "projects/cyberpunk/outro/inbetween/"
LIGHT = REPO + "projects/opening/ref/yt_line/lighting/"
GIRL = [REPO + "projects/stamp/s2_stand.png", REPO + "images/rotating/rotate3.png"]
STYLE = ("Copy the LIGHTING and LOOK of the reference frames exactly: a flat, even, deep royal blue backdrop with "
         "nothing in it; the figure a solid flat black silhouette; the only light is hard, flat, cel-shaded shapes of "
         "bright orange (#ffaa14) along her top and left edges, catching strands of hair, the edge of her face, one eye, "
         "her shoulder, her hand; no gradients, no other colours, no outlines, no detail inside the black. The girl is "
         "the one in the girl references: long wavy hair with blunt straight bangs, a headband, a dress with puffed "
         "short sleeves and a full skirt. Anime film still, 16:9, ONE single image, no text, no watermark, no border.")
SHOTS = {
    "a_far_side": ("Shot: very wide, she stands small and low in the frame, near the bottom centre, seen side-on in "
                   "profile looking right, only her head and shoulders and the top of her body above the bottom edge, "
                   "lots of empty blue above her, like the far frames of the reference.", [LIGHT + "l_05.png"]),
    "b_turning": ("Shot: medium, her head and shoulders lower right of centre, she is turning towards the camera, her "
                  "long hair swinging out to the left in sharp flat shapes, the light catching the hair's edges and "
                  "the side of her face, like the reference's turning frame.", [LIGHT + "l_06.png"]),
    "c_close_eye": ("Shot: close-up, her head big and slightly tilted, filling most of the frame, her hair fanned out "
                    "in long sharp flat shapes, one eye lit orange and wide open looking into the camera, a sliver of "
                    "her cheek and jaw lit, the rest of her face in black, exactly like the reference close-up.",
                    [LIGHT + "l_12.png"]),
    "d_hand_out": ("Shot: medium close, centre frame, she reaches one open hand straight out at the camera, the hand big "
                   "and near us, her face behind it partly visible, one eye and the edge of her face lit orange, the "
                   "hand's edges and fingers lit orange.", [LIGHT + "l_12.png"]),
}


def inline(path, side=1600):
    im = Image.open(path).convert("RGB"); im.thumbnail((side, side))
    buf = io.BytesIO(); im.save(buf, "JPEG", quality=92)
    return {"inlineData": {"mimeType": "image/jpeg", "data": base64.b64encode(buf.getvalue()).decode()}}


def gen(name):
    dest = OUT + name + ".png"
    if os.path.exists(dest):
        return name, "exists"
    shot, refs = SHOTS[name]
    text = ("The first image(s) are the LIGHTING reference frames. The last two images are the GIRL reference. "
            + STYLE + " " + shot)
    parts = [{"text": text}] + [inline(p) for p in refs] + [inline(p) for p in GIRL]
    body = {"contents": [{"parts": parts}],
            "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"imageSize": "2K", "aspectRatio": "16:9"}}}
    req = OUT + "_%s.json" % name
    json.dump(body, open(req, "w"))
    r = subprocess.run(["treg", "call", "google-ai.image-gen.gemini-3-pro-image", "--method", "POST",
                        "--query", "model=gemini-3-pro-image",
                        "--query", "fields=candidates(content(parts(text,inlineData)),finishReason),usageMetadata",
                        "--data", "@" + req, "--await", "--timeout", "900"], capture_output=True, text=True)
    os.remove(req)
    try:
        resp = json.loads(r.stdout[r.stdout.index("{"):])
        data = next(p["inlineData"]["data"] for p in resp["candidates"][0]["content"]["parts"] if "inlineData" in p)
    except (ValueError, KeyError, IndexError, StopIteration):
        return name, "FAIL " + (r.stdout + r.stderr)[:300].replace("\n", " ")
    Image.open(io.BytesIO(base64.b64decode(data))).convert("RGB").resize((1920, 1080), Image.LANCZOS).save(dest)
    return name, "ok"


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    names = sys.argv[1:] or list(SHOTS)
    with cf.ThreadPoolExecutor(max_workers=4) as ex:
        for name, status in ex.map(gen, names):
            print(status, name, flush=True)
