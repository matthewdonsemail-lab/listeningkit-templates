"""The launch opener's shots, a few seconds on (matt, 2026-11-15): for every still in the opener (the clips listed in
textAnimations/assets/opening_edit.json, synced from matt's FilmCraft cut; not the cyberpsycho clip), the same shot a
few seconds later, so each pair can go to an image-to-video model as its first and last frame.
Same camera, lens, framing, light and people; only what would naturally have moved a few seconds on has moved.
Writes projects/opening/next/<shot>_next.png at the source still's own size (so the clip's Motion in FilmCraft and
EffectCraft still fits). Through treg / Nano Banana Pro, about $0.03 each; the reference is hosted as a small JPEG
(projects/opening/next/upload/) to stay inside treg's daily hosting quota. Skips a frame that already exists."""
import concurrent.futures as cf
import json
import os
import re
import subprocess
import sys

from PIL import Image

ROOT = "C:/Users/0/.buzz/REPOS/listeningkit-templates/"
OUT = ROOT + "projects/opening/next/"
EDIT = ROOT + "textAnimations/assets/opening_edit.json"
PROMPT = ("The reference image is one frame of a film shot. Make the frame of the SAME shot a few seconds later: the "
          "exact same camera position, lens, framing, crop, lighting, colour grade, location and people, so the two "
          "frames can be the first and last frame of one continuous video clip. Only what would naturally move in a "
          "few seconds has moved: people shift their gaze, expression, head or hands a little, anything in motion "
          "(cars, screens, text being typed, light, background figures) has moved on a little. No cut, no new camera "
          "angle, no zoom. ONE single image, not a grid, no added text, no watermark, no border.")


def host(path):
    out = subprocess.run(["treg", "host", path], capture_output=True, text=True).stdout
    return re.findall(r"https://treg\.to/m/\S+", out)[-1]


def ratio(w, h):
    r = w / h
    return "21:9" if r > 2.0 else "16:9" if r > 1.5 else "4:3" if r > 1.2 else "1:1"


def gen(shot):
    name = shot["name"].replace(" ", "_")
    dest = OUT + name + "_next.png"
    if os.path.exists(dest):
        return dest, "exists"
    src = Image.open(shot["src"])
    body = {"model": "gemini-3-pro-image-preview", "size": ratio(*src.size), "resolution": "2K",
            "image_urls": [host(OUT + "upload/" + name + ".jpg")], "prompt": PROMPT}
    r = subprocess.run(["treg", "call", "reapi.image-gen.gemini-3-pro-image", "--method", "POST", "--data",
                        json.dumps(body), "--await", "--timeout", "900"], capture_output=True, text=True)
    m = re.findall(r"https://file\.deepytb\.com/[^\"\s]+\.(?:png|jpg)", r.stdout + r.stderr)
    if not m:
        return dest, "FAIL " + (r.stdout + r.stderr)[:300].replace("\n", " ")
    tmp = dest + ".dl"
    subprocess.run(["curl.exe", "-sL", m[0], "-o", tmp], check=True)
    Image.open(tmp).convert("RGB").resize(src.size, Image.LANCZOS).save(dest)
    os.remove(tmp)
    return dest, "ok"


def gen_google(shot):
    """the same model on Google's own API (google-ai.image-gen.gemini-3-pro-image, about $0.15 each): the reference
    goes inline as base64, so nothing is hosted and treg's daily hosting quota doesn't matter"""
    import base64
    import io
    name = shot["name"].replace(" ", "_")
    dest = OUT + name + "_next.png"
    if os.path.exists(dest):
        return dest, "exists"
    src = Image.open(shot["src"]).convert("RGB")
    ref = src.copy()
    ref.thumbnail((1600, 1600))
    buf = io.BytesIO()
    ref.save(buf, "JPEG", quality=90)
    body = {"contents": [{"parts": [{"text": PROMPT},
                                    {"inlineData": {"mimeType": "image/jpeg", "data": base64.b64encode(buf.getvalue()).decode()}}]}],
            "generationConfig": {"responseModalities": ["IMAGE"],
                                 "imageConfig": {"imageSize": "2K", "aspectRatio": ratio(*src.size)}}}
    req = OUT + "upload/_%s_body.json" % name
    json.dump(body, open(req, "w"))
    r = subprocess.run(["treg", "call", "google-ai.image-gen.gemini-3-pro-image", "--method", "POST",
                        "--query", "model=gemini-3-pro-image",
                        "--query", "fields=candidates(content(parts(text,inlineData)),finishReason),usageMetadata",
                        "--data", "@" + req, "--await", "--timeout", "900"], capture_output=True, text=True)
    os.remove(req)
    try:
        resp = json.loads(r.stdout[r.stdout.index("{"):])
        cand = resp["candidates"][0]
        data = next(p["inlineData"]["data"] for p in cand["content"]["parts"] if "inlineData" in p)
    except (ValueError, KeyError, IndexError, StopIteration):
        return dest, "FAIL " + (r.stdout + r.stderr)[:300].replace("\n", " ")
    Image.open(io.BytesIO(base64.b64decode(data))).convert("RGB").resize(src.size, Image.LANCZOS).save(dest)
    return dest, "ok"


if __name__ == "__main__":
    args = [v for v in sys.argv[1:] if v != "--google"]
    run = gen_google if "--google" in sys.argv else gen
    shots = [s for s in json.load(open(EDIT))["shots"] if not s["video"]]
    if args:
        shots = [s for s in shots if s["name"] in args]
    with cf.ThreadPoolExecutor(max_workers=10) as ex:
        for dest, status in ex.map(run, shots):
            print(status, dest.replace(OUT, ""), flush=True)
