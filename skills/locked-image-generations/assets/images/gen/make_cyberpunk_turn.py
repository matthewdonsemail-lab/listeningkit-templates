"""Cyberpunk outro frames, through treg / Nano Banana Pro.
turn: the girl from the Nous logo turning her head away from camera, ~75 degrees in 7 steps, each step in a different
style, all on black with the same framing (her head centred, the same size), so they match-cut while the comp zooms in.
turn_0 is the logo's own pose and style, made from the logo; the rest are made from turn_0 so the framing holds.
portraits: blue-chiaroscuro headshots on black in the style of images/Blue Noir Headband Portraits.png, each an extreme
caricature of a different kind of person, rim-lit, faces half lost in shadow.
Writes projects/cyberpunk/outro/turn_<n>.png and portrait_<n>.png."""
import concurrent.futures as cf
import json
import os
import re
import subprocess
import sys

ROOT = "C:/Users/0/.buzz/REPOS/listeningkit-templates/"
OUT = ROOT + "projects/cyberpunk/outro/"
LOGO = ROOT + "textAnimations/assets/endcard/nous_logo_white.png"
NOIR = ROOT + "images/Blue Noir Headband Portraits.png"
FRAME = ("Framing for every image in this set: a head-and-shoulders shot on a pure black background, her head centred in "
         "the frame and filling the middle half of its height, the same size and position every time, camera at eye "
         "level. 16:9, no text, no watermark, no logo, no border.")
TURN = [  # degrees turned away from the first pose, style
    (0, "white ink line art on black exactly like the girl in the Nous logo reference: stark white strokes and white "
        "hair highlights on solid black, heavy black shadow across her face"),
    (12, "a 90s cel-shaded anime frame: white skin, solid black hair with sharp white highlights, crisp black line work, "
         "flat colours, clearly different from the white-on-black line art of the reference"),
    (25, "ONE single hyperrealistic 35mm film photograph (one image, not a grid, not a contact sheet, not multiple "
         "frames) of a real young woman, lit by one hard light from the side"),
    (37, "a PlayStation 2 era video game cutscene render: low-polygon head, blurry low-resolution textures, glossy stiff "
         "hair mesh"),
    (50, "a baroque oil painting in the style of Caravaggio: dramatic chiaroscuro, visible brush strokes, craquelure"),
    (62, "a Japanese ukiyo-e woodblock print: flat colour areas, bold outlines, paper grain, Prussian blue"),
    (75, "a noir anime illustration in deep blue and black with glowing blue rim light, like the Blue Noir references"),
]
GIRL = ("The same girl as the reference: blunt black bangs, long dark hair, the white headband. In the first pose her "
        "face is turned three-quarters to the viewer's left, like the girl in the Nous logo.")
PEOPLE = [
    "a huge broad macho man with a tiny head on a massive neck and jutting jaw",
    "a short very fat man with a round moon face, three chins and tiny eyes",
    "a gaunt skeletal man with an extremely long face, hollow cheeks and a long thin nose",
    "a heavy older woman with a huge puffed hairdo, sagging jowls and a pinched mouth",
    "a hunched bald old man with an enormous hooked nose and a heavy brow",
    "a wiry wide-eyed young man with a giant forehead, sticking-out ears and a manic grin",
]
PORTRAIT = ("A single close headshot portrait on a pure black background, exactly in the style of the reference image: "
            "noir anime illustration in deep blue and black, blue chiaroscuro, glowing blue rim light on the hair, cheek "
            "and shoulder, most of the face lost in deep shadow, seen from slightly below like the reference. The person "
            "is an extreme caricature: {who}. Head and shoulders filling the frame, slightly off centre. 16:9, no text, "
            "no watermark.")


def host(path):
    out = subprocess.run(["treg", "host", path], capture_output=True, text=True).stdout
    return re.findall(r"https://treg\.to/m/\S+", out)[-1]


def gen(name, urls, prompt):
    dest = OUT + name + ".png"
    if os.path.exists(dest):
        return dest, "exists"
    body = {"model": "gemini-3-pro-image-preview", "size": "16:9", "resolution": "2K", "image_urls": urls,
            "prompt": prompt}
    r = subprocess.run(["treg", "call", "reapi.image-gen.gemini-3-pro-image", "--method", "POST", "--data",
                        json.dumps(body), "--await", "--timeout", "900"], capture_output=True, text=True)
    m = re.findall(r"https://file\.deepytb\.com/[^\"\s]+\.png", r.stdout + r.stderr)
    if not m:
        return dest, "FAIL " + (r.stdout + r.stderr)[:300].replace("\n", " ")
    subprocess.run(["curl.exe", "-sL", m[0], "-o", dest], check=True)
    return dest, "ok"


def turn_prompt(i):
    deg, style = TURN[i]
    head = ("Her head in the first pose, exactly as in the reference." if deg == 0 else
            "Her head is turned %d degrees further away from the camera than in the reference image, rotating to her "
            "left, toward the darkness behind her%s." % (deg, ", so we now see mostly the back and side of her head and "
                                                               "hair, her face almost gone" if deg >= 62 else ""))
    return "%s %s Draw her as %s. %s" % (GIRL, head, style, FRAME)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    jobs = []
    if which in ("all", "first"):
        jobs.append(("turn_0", [host(LOGO)], turn_prompt(0)))
        noir = host(NOIR)
        for i, who in enumerate(PEOPLE):
            jobs.append(("portrait_%d" % i, [noir], PORTRAIT.format(who=who)))
    if which in ("all", "turn"):
        t0 = host(OUT + "turn_0.png")
        for i in range(1, len(TURN)):
            jobs.append(("turn_%d" % i, [t0], turn_prompt(i)))
    with cf.ThreadPoolExecutor(max_workers=8) as ex:
        for dest, status in ex.map(lambda j: gen(*j), jobs):
            print(status, dest.replace(OUT, ""), flush=True)
