"""The launch film's opening, accurate to where and how GPT-3 was made (RESEARCH/GPT3_ORIGIN_FOR_LAUNCH_FILM.md):
OpenAI's office in the Pioneer Building (3180 18th St at Folsom, Mission District, San Francisco: a 1902 grey timber
Italianate factory with "PIONEER BUILDING" painted in red), its timber-beamed loft inside, and the Azure supercomputer
it was trained on (10,000 NVIDIA V100 GPUs, undisclosed Microsoft data centre). Sunny and golden like the
Edgerunners 2 trailer's opening. The people are never recognisable: from behind, in silhouette, or hands only.
Prompts follow the SCLCAM order (subject, context, lens/framing, atmosphere, mood/colour, output) from
fal-ai-community/skills cinematography/SKILL.md. The building photo (Wikimedia Commons, 2012) is the reference for
the building shots. Written to projects/opening/gpt3/<name>.png at 1920x1080 via treg / Nano Banana Pro."""
import concurrent.futures as cf
import json
import os
import re
import subprocess

from PIL import Image

OP = "C:/Users/0/.buzz/REPOS/listeningkit-templates/projects/opening/"
OUT = OP + "gpt3/"
REAL = ("Real photograph, cinematic 35mm film still, 16:9, ONE single image, not a grid. No readable text except "
        "where asked, no logos, no brand names. Any people are seen from behind, in silhouette or out of focus, never "
        "a recognisable face.")
WARM = "Warm low golden-hour sunlight, long soft shadows, gentle haze, warm gold and amber grade, hopeful. "
BUILDING = ("The building in the reference photo, exactly: the three-storey grey-painted timber Italianate building on "
            "a street corner, tall white-framed double-hung sash windows with dark grey trim, a red band under the "
            "cornice, the words PIONEER BUILDING painted in red across the corner, street trees along the pavement. ")
SHOTS = [  # (name, reference: 'building' or 'warm', prompt)
    ("building", "building", BUILDING + "Low-angle wide establishing shot from across the intersection in 2020, the "
     "sun low behind the camera lighting the grey timber facade gold, long tree shadows across it, a lens flare at "
     "the frame edge, an empty quiet street. " + WARM),
    ("windows", "building", BUILDING + "Medium shot looking up at three of its tall sash windows on the second floor "
     "at dusk, the warm lights on inside, the soft glow of computer monitors and the silhouettes of people at desks "
     "seen through the glass, golden sky reflected in the panes. " + WARM),
    ("loft", "warm", "Inside a converted 1900s timber factory loft used as an AI research office in 2020: exposed "
     "wooden posts and ceiling beams, tall white sash windows, plain white desks with big monitors and laptops. A "
     "small team gathered round one long table, seen from behind and in silhouette against the windows, leaning in, "
     "talking. Wide, eye level, slight depth of field. " + WARM),
    ("aisle", "warm", "Inside a hyperscale cloud data centre in 2020: a long cold aisle between tall black server "
     "racks full of GPU servers, thousands of tiny white and blue status lights, bundled cables overhead, a raised "
     "white floor, a perspective vanishing point, a faint warm glow at the far end. Wide, symmetrical, deep focus, "
     "cool white light with the warm glow at the end."),
    ("gpus", "warm", "Macro close-up of a GPU server tray in a data centre: eight high-end data-centre GPU modules with "
     "large finned heatsinks on a green circuit board, thick copper and gold contacts, tiny status lights, shallow "
     "depth of field, a warm rim light catching the fins."),
    ("whiteboard", "warm", "A whiteboard in the timber-beamed loft office covered in hand-drawn log-scale plots: "
     "several straight descending lines of loss against compute, axes, arrows and small notes in marker, a big "
     "clear space in the middle, sunlight falling across it from a sash window, a marker on the ledge. " + WARM),
    ("laptop", "warm", "Over-the-shoulder shot of a researcher at a laptop in the timber-beamed loft, the back of their "
     "head and shoulder soft in the foreground, the screen showing a two-column academic paper title page as soft "
     "blurred text, a mug, sunlight across the desk. " + WARM),
    ("first", "warm", "Three researchers crowded round one monitor in the timber-beamed loft office, seen from behind "
     "and over their shoulders, their faces turned to the screen and out of view, one with a hand on her head, the "
     "screen glowing with lines of text appearing, sunlight from the sash windows, a moment of wonder. " + WARM),
]


def host(path):
    out = subprocess.run(["treg", "host", path], capture_output=True, text=True).stdout
    return re.findall(r"https://treg\.to/m/\S+", out)[-1]


def gen(job):
    name, ref, prompt = job
    dest = OUT + name + ".png"
    if os.path.exists(dest):
        return "exists " + name
    body = {"model": "gemini-3-pro-image-preview", "size": "16:9", "resolution": "2K", "image_urls": [URLS[ref]],
            "prompt": prompt + " " + REAL}
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
    URLS = {"building": host(OUT + "ref/pioneer_building_2012.jpg"), "warm": host(OP + "creation/city.png")}
    with cf.ThreadPoolExecutor(max_workers=5) as ex:
        for status in ex.map(gen, SHOTS):
            print(status, flush=True)
