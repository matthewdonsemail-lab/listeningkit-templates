"""The stamp girl on yellow (matt, 2026-11-15), for the blue diamond to morph out into after the busts' pull out:
the girl from images/rotating (ink anime, long black hair, blunt bangs, white headband) in her dress (projects/
cyberpunk/shot3.png, the one standing in the hall; projects/stamp/s2_stand.png, standing), full body, standing
small in the middle of a flat bright yellow backdrop, in blue and white, holding her hand out towards the camera,
framed like matt's reference (projects/cyberpunk/outro/ref_red_backdrop.png).
One image through Google's Gemini 3 Pro Image (google-ai.image-gen.gemini-3-pro-image, about $0.15), references inline.
Writes projects/cyberpunk/outro/stamp_girl_yellow.png (1920x1080).
  python images/gen/make_yellow_woman.py"""
import base64
import io
import json
import os
import subprocess

from PIL import Image

ROOT = "C:/Users/0/.buzz/REPOS/listeningkit-templates/projects/cyberpunk/"
OUT = ROOT + "outro/"
STAMP = "C:/Users/0/.buzz/REPOS/listeningkit-templates/projects/stamp/"
PROMPT = ("Image 1 is the girl and the drawing style: a bold ink anime illustration like a print, long wavy hair with "
          "blunt bangs, a white headband with round clips, the dress with white puffed short sleeves, a dark bodice, a "
          "full striped skirt, white socks and Mary Jane shoes. Image 2 is the same girl standing in a hall. Image 3 "
          "is the framing. Make ONE image: the SAME girl, drawn in exactly the style of image 1, full body, standing "
          "dead centre and small in the frame, framed like image 3 (wide, lots of empty space round her). She faces the "
          "camera and holds one arm straight out TOWARDS THE CAMERA, reaching at the viewer, the palm of her open hand "
          "facing us, the arm foreshortened, her hand bigger in front of her body. Colours: ONLY yellow and blue and "
          "white. The background is one perfectly flat, solid, even bright yellow (#ffd400): no texture, no gradient, "
          "no floor line, nothing else. She is inked in deep blue (#1438d8) instead of black, with white: her hair, "
          "line work, bodice and the dark skirt stripes are solid deep blue. 16:9, ONE single image, no text, no "
          "watermark, no border.")


def inline(path, side=1600):
    im = Image.open(path).convert("RGB"); im.thumbnail((side, side))
    buf = io.BytesIO(); im.save(buf, "JPEG", quality=92)
    return {"inlineData": {"mimeType": "image/jpeg", "data": base64.b64encode(buf.getvalue()).decode()}}


body = {"contents": [{"parts": [{"text": PROMPT}, inline(STAMP + "s2_stand.png"), inline(ROOT + "shot3.png"), inline(OUT + "ref_red_backdrop.png")]}],
        "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"imageSize": "2K", "aspectRatio": "16:9"}}}
req = OUT + "_stamp_girl.json"
json.dump(body, open(req, "w"))
r = subprocess.run(["treg", "call", "google-ai.image-gen.gemini-3-pro-image", "--method", "POST",
                    "--query", "model=gemini-3-pro-image",
                    "--query", "fields=candidates(content(parts(text,inlineData)),finishReason),usageMetadata",
                    "--data", "@" + req, "--await", "--timeout", "900"], capture_output=True, text=True)
os.remove(req)
resp = json.loads(r.stdout[r.stdout.index("{"):])
data = next(p["inlineData"]["data"] for p in resp["candidates"][0]["content"]["parts"] if "inlineData" in p)
Image.open(io.BytesIO(base64.b64decode(data))).convert("RGB").resize((1920, 1080), Image.LANCZOS).save(OUT + "stamp_girl_yellow.png")
print("ok", OUT + "stamp_girl_yellow.png")
