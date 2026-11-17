"""The cyberpunk outro's six busts (projects/cyberpunk/outro/portrait_0-5.png) in three more styles each (matt,
2026-11-15): realistic, low-poly, 1-bit dither. The camera, crop, pose and face position are kept exactly, so the
versions line up and the busts scene can cut between them and glitch-collage them (make_bust_lines.py).
Writes projects/cyberpunk/outro/styles/portrait_<i>_<style>.png at the source's size. Through Google's own Gemini 3 Pro
Image (google-ai.image-gen.gemini-3-pro-image, about $0.15 each), the reference inline (no hosting). Skips existing.
  python images/gen/make_bust_styles.py [portrait index ...]"""
import base64
import concurrent.futures as cf
import io
import json
import os
import subprocess
import sys

from PIL import Image

OUT = "C:/Users/0/.buzz/REPOS/listeningkit-templates/projects/cyberpunk/outro/"
STYLES = {
    "realistic": "a real photograph: a real person, real skin and hair, shot on a 35mm film camera, the same low-key blue "
                 "rim light on a black background",
    "polygon": "a low-poly 3D render: flat-shaded triangles, visible faceted polygons on the face and body, like a 1998 "
               "PlayStation character, the same blue rim light on a black background",
    "dither": "a 1-bit black and white dithered image: only pure black and pure white pixels, ordered Bayer dither "
              "for the shading, like an old Macintosh screen",
}
PROMPT = ("Redraw the reference image as {style}. Keep the reference's composition EXACTLY: the same person, the same "
          "pose, head angle and expression, the face at exactly the same position and size in the frame, the same crop "
          "and camera, so it lines up with the reference pixel for pixel. 16:9, ONE single image, not a grid, no text, "
          "no watermark, no border.")


def gen(job):
    i, style = job
    dest = OUT + "styles/portrait_%d_%s.png" % (i, style)
    if os.path.exists(dest):
        return dest, "exists"
    src = Image.open(OUT + "portrait_%d.png" % i).convert("RGB")
    ref = src.copy(); ref.thumbnail((1600, 1600))
    buf = io.BytesIO(); ref.save(buf, "JPEG", quality=90)
    body = {"contents": [{"parts": [{"text": PROMPT.format(style=STYLES[style])},
                                    {"inlineData": {"mimeType": "image/jpeg", "data": base64.b64encode(buf.getvalue()).decode()}}]}],
            "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"imageSize": "2K", "aspectRatio": "16:9"}}}
    req = OUT + "styles/_%d_%s.json" % (i, style)
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
        return dest, "FAIL " + (r.stdout + r.stderr)[:300].replace("\n", " ")
    Image.open(io.BytesIO(base64.b64decode(data))).convert("RGB").resize(src.size, Image.LANCZOS).save(dest)
    return dest, "ok"


if __name__ == "__main__":
    os.makedirs(OUT + "styles", exist_ok=True)
    which = [int(v) for v in sys.argv[1:]] or list(range(6))
    jobs = [(i, s) for i in which for s in STYLES]
    with cf.ThreadPoolExecutor(max_workers=9) as ex:
        for dest, status in ex.map(gen, jobs):
            print(status, dest.replace(OUT, ""), flush=True)
