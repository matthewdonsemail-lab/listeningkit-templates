"""Stamp scene (after the cyberpunk outro's blue): the girl in the black-ink and blue-halftone print style of images/rotating on flat brand blue, and three
huddled groups of silhouette caricatures around her, each on a white dithered shadow pool like Intro 1's dither.
Round 1 makes her standing shot from images/rotating/rotate3.png and rotate1.png; round 2 makes the feet close-up and the
group shots from that, so she stays the same. Writes projects/stamp/<shot>.png. Through treg / Nano Banana Pro."""
import concurrent.futures as cf
import json
import os
import re
import subprocess
import sys

ROOT = "C:/Users/0/.buzz/REPOS/listeningkit-templates/projects/stamp/"
ROT = "C:/Users/0/.buzz/REPOS/listeningkit-templates/images/rotating/"
CROWD_REF = "C:/Users/0/.buzz/REPOS/listeningkit-templates/images/Blue Noir Headband Portraits.png"  # the crowd style
OUTFIT = "C:/Users/0/.buzz/REPOS/listeningkit-templates/projects/cyberpunk/shot3.png"  # her dress
STYLE = ("The girl is drawn exactly in the style of the reference images: bold black and white ink anime illustration "
         "like a print, solid black hair with sharp white highlights, white skin with black line work. The same girl: "
         "long wavy black hair with blunt bangs and the white headband with round clips. She wears the dress from the "
         "outfit reference (the anime girl in the blue marble hall): white puffed short sleeves, a black bodice, a "
         "full black-and-white striped skirt, white socks and black Mary Jane shoes. The background is one perfectly "
         "flat, solid, even blue (#2a8cff): no texture, no dots, no halftone, no grain, no gradient anywhere in the "
         "background, and nothing else in the world: no hills, no clouds, no walls, no floor lines, no horizon.")
DITHER = ("The ONLY dithering in the image is each person's shadow: under their feet a pool of white chunky square-pixel "
          "ordered dither, big white pixels, dense right under them and breaking up into the flat blue further out, "
          "like a 1-bit dithered gradient. Everywhere else the blue is completely flat and clean.")
CROWD = ("Around her, three separate huddled groups of people, each group 4 to 7 figures crowded tightly together, "
         "overlapping each other like the packed crowd in the CROWD STYLE reference image, all turned toward her. Draw "
         "the crowd exactly in the style of that reference: bold inked anime figures with flowing hair and clothes, "
         "solid black masses with sharp rim-light edges picking out their shoulders, hair and outlines, overlapping in "
         "depth, the front ones bigger. But they stay faceless and unrecognisable: their faces are lost in solid black "
         "shadow, only the rim light on their outlines. They are caricatures with exaggerated, varied builds: huge broad "
         "macho figures, short fat round ones, tall thin lanky ones, hunched ones, all different heights and widths. "
         "The crowd is black, white and grey only (white rim light, no blue on them). She is the only one with a "
         "visible face.")
SHOTS = {
    "s2_stand": ("ref", "A high-angle shot from above, the girl standing alone in the exact centre of the frame, full body, "
                        "small in the frame, hands in her pockets, looking up toward the camera. Her shadow under her is "
                        "the dither pool. " + STYLE + " " + DITHER),
    "s0_ots": ("s2", "The FIRST reference image is the composition and crowd style: copy its composition exactly. Like "
                     "it, the frame is filled with five or six huge superimposed busts (heads and shoulders) floating at "
                     "very different scales, overlapping each other, some enormous and cropped by the frame edges, some "
                     "smaller in between, seen from slightly below, all turned toward the girl, on a flat brand blue "
                     "(#2a8cff) background instead of black. Draw them exactly in the FIRST reference's style: noir anime "
                     "ink, deep blue and black, glowing blue rim light on hair, cheeks and shoulders. But instead of the same "
                     "girl, these busts are exaggerated caricatures of different people: a huge broad macho man with a thick "
                     "neck, a fat round-faced man, a gaunt thin long-faced man, a heavy older woman, a hunched bald man, "
                     "their eyes and faces sunk in deep shadow so none is recognisable. On the RIGHT third of the frame, in "
                     "front of them and closest to camera, the girl from the other references in a close over-the-shoulder: "
                     "her face in three-quarter profile from behind, her ear, cheek, the corner of her eye, long wavy black "
                     "hair with the white headband and round clip, her white puffed sleeve at the bottom right, drawn in her "
                     "own bold black and white ink. 16:9."),
    "s1_feet": ("s2", "An extreme close-up of the same girl's feet from the reference: her shoes and the hems of her "
                      "trousers, from the same high angle, filling the lower middle of the frame, standing on the blue, "
                      "the dither shadow round them. " + STYLE + " " + DITHER),
    "s3_groups_wide": ("s2", "The same high-angle shot as the reference, the girl standing in exactly the same place and "
                             "size in the centre. " + CROWD + " The groups are spaced round her at a distance: one upper "
                             "left, one right, one lower left. " + STYLE + " " + DITHER),
    "s4_groups_low": ("s2", "A low, closer shot from just behind one huddled group: their big silhouette backs fill the "
                            "left and bottom of the frame, out of focus, and through the gap between them the girl stands "
                            "small in the centre, the other two groups beyond her. " + CROWD + " " + STYLE + " " + DITHER),
    "s5_groups_top": ("s2", "Straight down from directly overhead: the girl in the exact centre seen from above, the "
                            "three groups in a loose ring round her, everyone's heads and shoulders from above. " + CROWD +
                            " " + STYLE + " " + DITHER),
}


def host(path):
    out = subprocess.run(["treg", "host", path], capture_output=True, text=True).stdout
    return re.findall(r"https://treg\.to/m/\S+", out)[-1]


def gen(name, url):
    dest = ROOT + name + ".png"
    if os.path.exists(dest):
        return dest, "exists"
    body = {"model": "gemini-3-pro-image-preview", "size": "16:9", "resolution": "2K", "image_urls": url if isinstance(url, list) else [url],
            "prompt": SHOTS[name][1] + " 16:9, no text, no watermark, no logos."}
    r = subprocess.run(["treg", "call", "reapi.image-gen.gemini-3-pro-image", "--method", "POST", "--data",
                        json.dumps(body), "--await", "--timeout", "900"], capture_output=True, text=True)
    m = re.findall(r"https://file\.deepytb\.com/[^\"\s]+\.png", r.stdout + r.stderr)
    if not m:
        return dest, "FAIL " + (r.stdout + r.stderr)[:300].replace("\n", " ")
    subprocess.run(["curl.exe", "-sL", m[0], "-o", dest], check=True)
    return dest, "ok"


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if which in SHOTS:  # one shot on its own, from her standing shot; the crowd reference goes first
        print(*gen(which, [host(CROWD_REF), host(ROOT + "s2_stand.png"), host(ROT + "rotate3.png"), host(OUTFIT)]))
        sys.exit(0)
    if which in ("all", "round1"):
        print(*gen("s2_stand", [host(ROT + "rotate3.png"), host(ROT + "rotate1.png"), host(OUTFIT)]))
    if which in ("all", "round2"):
        url = [host(ROOT + "s2_stand.png"), host(ROT + "rotate3.png"), host(OUTFIT), host(CROWD_REF)]
        names = [n for n, v in SHOTS.items() if v[0] == "s2"]
        with cf.ThreadPoolExecutor(max_workers=len(names)) as ex:
            for dest, status in ex.map(lambda n: gen(n, url), names):
                print(status, dest.replace(ROOT, ""), flush=True)
