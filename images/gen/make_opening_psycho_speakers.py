"""The cyberpsycho steps for the real footage (matt, 2026-11-15): the young Sam and young Dario clips in the opener's
alternating shots after the drop (projects/opening/ref/speakers/, make_opening_psycho_cut.py) go cyberpsycho in the
red sun_ae look, 12 steps each, the way the two stills did (make_opening_psycho.py, whose prompt and stages this uses).

References per step, in this order, all sent inline (Google's own API, google-ai.image-gen.gemini-3-pro-image, about
$0.15 each; nothing is hosted, so treg's daily hosting quota doesn't matter):
  1. his face frame from the clip, the composition (projects/opening/psycho/<who>/<who>_ref.png, 1920x1080, cut by
     the frame-grab in psycho/speaker_refs.json, which also holds his eyes there)
  2. matt's monster still for him, the expression it ends on
  3. the sun_ae frame for this step (projects/opening/psycho/styleref_sun/style_<i>.png)
Writes projects/opening/psycho/<who>/<who>_00-11.png (1920x1080). Skips a step that already exists."""
import base64
import concurrent.futures as cf
import importlib.util
import io
import json
import os
import subprocess
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("psycho", os.path.join(HERE, "make_opening_psycho.py"))
psycho = importlib.util.module_from_spec(spec)
spec.loader.exec_module(psycho)  # its PROMPT and STAGES (its own generation only runs under __main__)

OP = "C:/Users/0/.buzz/REPOS/listeningkit-templates/projects/opening/"
PS = OP + "psycho/"
WHO = {
    "sam": (OP + "mattgen/Furious Monster Behind Blinds.png", "the young man talking, in a grey t-shirt"),
    "dario": (OP + "mattgen/Monstrous Scream in the Classroom.png", "the young man with dark hair, in a grey t-shirt"),
}


def inline(path, side):
    im = Image.open(path).convert("RGB")
    im.thumbnail((side, side))
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=88)
    return {"inlineData": {"mimeType": "image/jpeg", "data": base64.b64encode(buf.getvalue()).decode()}}


def gen(job):
    who, i = job
    dest = PS + "%s/%s_%02d.png" % (who, who, i)
    if os.path.exists(dest):
        return dest, "exists"
    end, desc = WHO[who]
    prompt = psycho.PROMPT.format(who=desc, n=i + 1, stage=psycho.STAGES[i])
    body = {"contents": [{"parts": [{"text": prompt}, inline(PS + "%s/%s_ref.png" % (who, who), 1600),
                                    inline(end, 1024), inline(PS + "styleref_sun/style_%02d.png" % i, 768)]}],
            "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"imageSize": "2K", "aspectRatio": "16:9"}}}
    req = PS + "_%s_%02d_body.json" % (who, i)
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
    Image.open(io.BytesIO(base64.b64decode(data))).convert("RGB").resize((1920, 1080), Image.LANCZOS).save(dest)
    return dest, "ok"


if __name__ == "__main__":
    who = [w for w in sys.argv[1:] if w in WHO] or list(WHO)
    steps = [int(v) for v in sys.argv[1:] if v.isdigit()] or list(range(12))
    jobs = [(w, i) for w in who for i in steps]
    with cf.ThreadPoolExecutor(max_workers=12) as ex:
        for dest, status in ex.map(gen, jobs):
            print(status, dest.replace(PS, ""), flush=True)
