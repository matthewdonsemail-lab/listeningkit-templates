"""Round 3 (matt, 2026-11-14): the opening's conversation shots as shot/reverse-shot over-the-shoulder close-ups, the
camera of the A24 "You Can See Everything" teaser (projects/opening/ref/gptref.mp4): a tight close-up of one person
past the blurred back of the other's head in the foreground, then the reverse. The teaser frames are the composition
reference only; the faces are the original cast (projects/opening/cast/cast.png), never the teaser's people.
Written to projects/opening/ots/<name>.png at 1920x1080 via treg / Nano Banana Pro."""
import concurrent.futures as cf
import json
import os
import re
import subprocess

from PIL import Image

OP = "C:/Users/0/.buzz/REPOS/listeningkit-templates/projects/opening/"
OUT = OP + "ots/"
CAST = ("The faces, hair and clothes are EXACTLY the people in the first reference image (the cast): the FOUNDER (slim, "
        "mid-30s, short dark-blond hair, grey crew-neck sweater), RESEARCHER A (late 20s, long dark hair, glasses, "
        "green cardigan), RESEARCHER B (early 30s, curly black hair, short beard, navy hoodie). Take ONLY the camera "
        "framing, lens and light from the second reference image; none of its people. ")
LOOK = ("Inside a 1900s timber-beamed loft office in 2020, warm low window light and practical lamp light, long lens, "
        "very shallow depth of field, the foreground head a soft dark blur, real photograph, cinematic 35mm film still, "
        "fine grain, 16:9, ONE single image, not a grid, no text, no logos.")
HER, HIM = "teaser_ots_her.png", "teaser_ots_him.png"
SHOTS = [  # (name, framing reference, prompt)
    ("a_talks", HER, "Over-the-shoulder close-up of RESEARCHER A talking, her face sharp, framed past the blurred back of "
     "the FOUNDER's head and shoulder filling the left third of frame, bright-eyed, mid-sentence. "),
    ("founder_talks", HIM, "Reverse over-the-shoulder close-up of the FOUNDER leaning in, talking, intense, his face sharp, "
     "framed past RESEARCHER A's blurred dark hair filling the right third of frame. "),
    ("a_listens", HER, "Over-the-shoulder close-up of RESEARCHER A listening, a slight smile, eyes on him, framed past the "
     "blurred back of the FOUNDER's head on the left. "),
    ("b_looks", HER, "Over-the-shoulder close-up of RESEARCHER B looking at RESEARCHER A, uneasy, doubtful, framed past "
     "her blurred dark hair and shoulder on the left. "),
    ("a_looks", HIM, "Reverse over-the-shoulder close-up of RESEARCHER A looking back at RESEARCHER B, wide-eyed, unsure, "
     "framed past his blurred curly hair on the right. "),
    ("founder_screams", HIM, "Close-up of the FOUNDER with his mouth wide open, screaming with joy and disbelief, fists "
     "up, framed past RESEARCHER A's blurred hair and shoulder on the right, the laptop glow under his face. "),
]


def host(path):
    out = subprocess.run(["treg", "host", path], capture_output=True, text=True).stdout
    return re.findall(r"https://treg\.to/m/\S+", out)[-1]


def gen(job):
    name, ref, prompt = job
    dest = OUT + name + ".png"
    if os.path.exists(dest):
        return "exists " + name
    body = {"model": "gemini-3-pro-image-preview", "size": "16:9", "resolution": "2K", "image_urls": [CASTURL, REFS[ref]],
            "prompt": CAST + prompt + LOOK}
    r = subprocess.run(["treg", "call", "reapi.image-gen.gemini-3-pro-image", "--method", "POST", "--data",
                        json.dumps(body), "--await", "--timeout", "900"], capture_output=True, text=True)
    m = re.findall(r"https://file\.deepytb\.com/[^\"\s]+\.(?:png|jpg)", r.stdout + r.stderr)
    if not m:
        return "FAIL %s %s" % (name, (r.stdout + r.stderr)[:300].replace("\n", " "))
    raw = OUT + name + "_raw" + os.path.splitext(m[0])[1]
    subprocess.run(["curl.exe", "-sL", m[0], "-o", raw], check=True)
    Image.open(raw).convert("RGB").resize((1920, 1080), Image.LANCZOS).save(dest)
    return "ok " + name


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    CASTURL = host(OP + "cast/cast.png")
    REFS = {r: host(OP + "ref/" + r) for r in (HER, HIM)}
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        for status in ex.map(gen, SHOTS):
            print(status, flush=True)
