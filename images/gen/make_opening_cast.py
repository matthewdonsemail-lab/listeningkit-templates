"""The opening's people: an original cast (not likenesses of real people) playing the team that made GPT-3 in the
Pioneer Building loft (gpt3/loft.png). Round 1 draws the cast together (cast.png); round 2 draws every shot with
the cast sheet first as the reference, so faces stay the same. Locked-off stills, no motion.
  aerial        San Francisco from the air at golden hour (no cast)
  headshot_a/b/c  close headshots of three researchers mid-conversation, talking to one another
  macbook       all four round a MacBook on the long table
  keyboard      the founder pressing the key, the others behind him
  split         all four staring at the screen the moment it's done
  look_a/b      close-ups of two of them looking at each other
  scream        the founder, mouth wide open, screaming; the others round him, looking at him
Written to projects/opening/cast/<name>.png at 1920x1080 via treg / Nano Banana Pro."""
import concurrent.futures as cf
import json
import os
import re
import subprocess
import sys

from PIL import Image

OP = "C:/Users/0/.buzz/REPOS/listeningkit-templates/projects/opening/"
OUT = OP + "cast/"
CAST = ("THE CAST, original fictional characters (not any real person): the FOUNDER, a slim man in his mid-30s with "
        "short dark-blond hair, a grey crew-neck sweater; RESEARCHER A, a woman in her late 20s with long dark hair "
        "and glasses, a green cardigan; RESEARCHER B, a man in his early 30s with curly black hair and a short beard, "
        "a navy hoodie; RESEARCHER C, a man in his 40s with a shaved head, a denim shirt. ")
PLACE = ("Inside a converted 1900s timber factory loft used as an AI research office in 2020: exposed wooden posts "
         "and beams, brick, tall white sash windows, plain white desks and monitors. Warm low golden-hour sunlight "
         "through the windows, warm gold and amber grade. ")
STILL = "Real photograph, cinematic 35mm film still, 16:9, ONE single image, not a grid, no text, no logos."
SAME = "The SAME four people as in the first reference image: identical faces, hair and clothes. "
SHOTS = {
    "cast": CAST + "All four standing together round a long table in the loft, waist-up, looking at each other, "
            "talking. " + PLACE,
    "aerial": "Aerial shot of San Francisco at golden hour from a helicopter: the Mission District rooftops and streets "
              "in the foreground, downtown towers and the bay beyond, warm low sun, long shadows, light haze, "
              "hopeful. ",
    "headshot_a": SAME + "Close headshot of RESEARCHER A mid-sentence, talking to someone just off frame left, "
                  "animated, eyes bright, the loft soft behind her. " + PLACE,
    "headshot_b": SAME + "Close headshot of RESEARCHER B replying to someone off frame right, a half smile, "
                  "gesturing, the loft soft behind him. " + PLACE,
    "headshot_c": SAME + "Close headshot of RESEARCHER C listening, then speaking, leaning in, intent, the loft soft "
                  "behind him. " + PLACE,
    "macbook": SAME + "All four crowded round one open silver laptop on the long table, leaning in close, faces lit "
               "by the screen and the sun, expectant. " + PLACE,
    "keyboard": SAME + "Medium close-up of the FOUNDER pressing a key on the silver laptop with one finger, focused, "
                "the three others leaning in behind his shoulders watching the screen. " + PLACE,
    "split": SAME + "All four frozen staring at the laptop screen the instant it finished, the screen glow on their "
             "faces, stunned, silent. " + PLACE,
    "look_a": SAME + "Close-up of RESEARCHER A turning to look at RESEARCHER B beside her, wide-eyed, unsure, the "
              "others out of focus. " + PLACE,
    "look_b": SAME + "Close-up of RESEARCHER B looking back at RESEARCHER A, uneasy, doubtful, the others out of "
              "focus. " + PLACE,
    "scream": SAME + "The FOUNDER with his mouth wide open, screaming with his whole body, fists up, in front of the "
              "laptop; the three others around him turned to look at him, shocked. " + PLACE,
}


def host(path):
    out = subprocess.run(["treg", "host", path], capture_output=True, text=True).stdout
    return re.findall(r"https://treg\.to/m/\S+", out)[-1]


def gen(name, refs):
    dest = OUT + name + ".png"
    if os.path.exists(dest):
        return "exists " + name
    body = {"model": "gemini-3-pro-image-preview", "size": "16:9", "resolution": "2K", "image_urls": refs,
            "prompt": SHOTS[name] + STILL}
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
    loft = host(OP + "gpt3/loft.png")
    print(gen("cast", [loft]), flush=True)
    cast = host(OUT + "cast.png")
    jobs = [(n, [loft] if n == "aerial" else [cast, loft]) for n in SHOTS if n != "cast"]
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        for status in ex.map(lambda j: gen(*j), jobs):
            print(status, flush=True)
