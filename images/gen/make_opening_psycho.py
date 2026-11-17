"""The opening's last two shots going cyberpsycho (matt, 2026-11-15): the man behind the blinds and the man at the
chalkboard, 12 steps each, the camera frame locked, the two of them turning step by step from the photo into the red
sun_ae edit look (projects/opening/ref/sun_ae: hard red, black and white, white jagged outlines, the screaming face
multiplied) while they shout. Cut against each other on the beat with the glitch blocks (make_opening_psycho_cut.py).

References per step, in this order:
  1. the original shot, the composition (projects/opening/mattgen/...)
  2. matt's monster still for that shot, the expression it ends on
  3. one sun_ae frame, the look for this step (projects/opening/psycho/styleref_sun/style_<i>.png)
Writes projects/opening/psycho/<shot>/<shot>_00-11.png (1920x1080). Through treg / Nano Banana Pro, about $0.03 each.
Skips a still that already exists: delete one to redo it."""
import concurrent.futures as cf
import json
import os
import re
import subprocess
import sys

from PIL import Image

OP = "C:/Users/0/.buzz/REPOS/listeningkit-templates/projects/opening/"
MG = OP + "mattgen/"
OUT = OP + "psycho/"
SHOTS = {
    "blinds": (MG + "Through the Blinds, Wired In Silence.png", MG + "Furious Monster Behind Blinds.png",
               "the man behind the window blinds, with white earphones"),
    "chalk": (MG + "Intense Gaze Before the Chalkboard.png", MG + "Monstrous Scream in the Classroom.png",
              "the man with glasses in front of the chalkboard"),
}
# how far along each step is: the face, and how much of the sun_ae look has taken over
STAGES = [
    "still a real photograph; his jaw clenches, his eyes narrow, a faint red cast creeps into the shadows",
    "still mostly a photograph; he starts to shout, teeth showing, the light turning red, thin white jagged lines at the edges of the frame",
    "he is shouting hard; the shadows crush to black, the highlights go red, the first white jagged outlines trace his face",
    "shouting with veins standing out; half of the image is now flat red and black, posterised, white jagged outlines round his head",
    "screaming, mouth wide; the image is now mostly flat red, black and white anime shapes, only his eyes still photographic",
    "screaming, his teeth starting to sharpen; fully drawn now as flat red, black and white anime, thick white jagged outlines",
    "screaming, fangs coming through, the mouth stretching wider; hard red, black and white, white zig-zag edges, pink only in the mouth and eyes",
    "a monstrous scream, rows of fangs, the eyes wide and white; a second faint copy of his face echoes behind him",
    "the full monster scream from the second reference; two or three copies of his screaming face fan out behind him",
    "the monster scream, the screaming face repeated in a ring of copies with white zig-zag outlines, black and red",
    "the monster scream, many copies of the screaming face fanning out, white jagged outlines everywhere, the background gone to red and black",
    "the final cyberpsycho: the monster scream at its widest, a fan of many screaming copies of his face, pure red, black and white",
]
PROMPT = ("Three reference images. The FIRST is the shot: keep its composition EXACTLY, the same camera, the same crop, "
          "{who} at exactly the same position and size in the frame, the same head angle, so it cuts straight from it. "
          "The SECOND is where he ends up: his face turning into this monster, screaming. The THIRD is ONLY the visual "
          "style to move towards (the colours, the flat anime shapes, the white jagged outlines), none of its people or "
          "its layout. This is step {n} of 12 of him going cyberpsycho: {stage}. The same man, recognisable. "
          "16:9, ONE single image, not a grid, no text, no numbers, no watermark, no border.")


def host(path):
    out = subprocess.run(["treg", "host", path], capture_output=True, text=True).stdout
    return re.findall(r"https://treg\.to/m/\S+", out)[-1]


def gen(job):
    dest, urls, prompt = job
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
    Image.open(tmp).convert("RGB").resize((1920, 1080), Image.LANCZOS).save(dest)
    os.remove(tmp)
    return dest, "ok"


if __name__ == "__main__":
    which = sys.argv[1:] or list(SHOTS)
    # small JPEG copies are hosted (psycho/upload/: styles 384 px, shots 1024 px), to stay inside treg's daily
    # hosting quota; the composition still comes through, and the output is 2K regardless
    style = [host(OUT + "upload/style_%02d.jpg" % i) for i in range(12)]
    jobs = []
    for shot in which:
        src, end, who = SHOTS[shot]
        os.makedirs(OUT + shot, exist_ok=True)
        a, b = host(OUT + "upload/%s_src.jpg" % shot), host(OUT + "upload/%s_end.jpg" % shot)
        for i in range(12):
            jobs.append((OUT + "%s/%s_%02d.png" % (shot, shot, i), [a, b, style[i]],
                         PROMPT.format(who=who, n=i + 1, stage=STAGES[i])))
    with cf.ThreadPoolExecutor(max_workers=12) as ex:
        for dest, status in ex.map(gen, jobs):
            print(status, dest.replace(OUT, ""), flush=True)
