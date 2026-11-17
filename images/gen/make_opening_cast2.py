"""Round 2 (matt, 2026-11-14): the opening's cast shots redrawn in the camera language of the A24 trailer "You Can
See Everything" (tight off-centre close-ups, long lens, dirty foregrounds, low-key window light). Round 1 was
make_opening_cast.py; this keeps its cast sheet.
Original: an original cast (not likenesses of real people) playing the team that made GPT-3 in the
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
OUT = OP + "cast2/"
CAST_SHEET = OP + "cast/cast.png"  # the cast from round 1, so the faces stay the same
CAST = ("THE CAST, original fictional characters (not any real person): the FOUNDER, a slim man in his mid-30s with "
        "short dark-blond hair, a grey crew-neck sweater; RESEARCHER A, a woman in her late 20s with long dark hair "
        "and glasses, a green cardigan; RESEARCHER B, a man in his early 30s with curly black hair and a short beard, "
        "a navy hoodie; RESEARCHER C, a man in his 40s with a shaved head, a denim shirt. ")
PLACE = ("Inside a converted 1900s timber factory loft used as an AI research office in 2020: exposed wooden posts "
         "and beams, brick, tall white sash windows, plain white desks and monitors. Warm low golden-hour sunlight "
         "through the windows, warm gold and amber grade. ")
STILL = ("Camera language of an A24 observational documentary: long telephoto lens, very shallow depth of field, "
         "tight off-centre framing that crops the face, low-key natural window light with faces half in shadow, muted "
         "teal shadows against warm skin, fine film grain, observational and unposed, never looking at the camera. "
         "Real photograph, cinematic 35mm film still, 16:9, ONE single image, not a grid, no text, no logos.")
SAME = "The SAME four people as in the first reference image: identical faces, hair and clothes. "
SHOTS = {
    "desk": SAME + "Observed from across the loft through a gap between two wooden posts, the four of them talking "
            "round the long table, small in frame, a post soft and dark in the foreground. " + PLACE,
    "headshot_a": SAME + "Extreme close-up of RESEARCHER A talking, framed off-centre to the right, cropped at the "
                  "forehead and chin, her glasses catching the window, a blurred dark shoulder of RESEARCHER B filling "
                  "the left third of the frame in the foreground. " + PLACE,
    "headshot_b": SAME + "Tight close-up of RESEARCHER B in three-quarter profile replying, framed at the left edge, "
                  "half his face in shadow, the window bright and blurred behind him. " + PLACE,
    "headshot_c": SAME + "Close-up of RESEARCHER C listening, shot over the out-of-focus shoulder and hair of "
                  "RESEARCHER A, his face small and sharp in the right of frame, eyes moving. " + PLACE,
    "macbook": SAME + "Tight insert from the side: hands resting on a silver laptop keyboard, the screen glow on the "
               "fingers, a coffee cup blurred in the foreground, the others' bodies soft and dark beyond. " + PLACE,
    "keyboard": SAME + "Extreme close-up of the FOUNDER in profile, cropped at the forehead, lit only by the laptop "
                "screen, his finger just pressing a key soft in the bottom of frame, the others dark blurs behind. "
                + PLACE,
    "split": SAME + "Extreme close-up of RESEARCHER A's eye and cheek lit by the laptop screen, the reflection of "
             "scrolling text in her glasses, stunned, still. " + PLACE,
    "look_a": SAME + "Tight close-up of RESEARCHER B's eyes turning to look at someone off frame left, uneasy, the "
              "frame cropped across his brow, the rest dark. " + PLACE,
    "look_b": SAME + "Tight close-up of RESEARCHER C looking back, cropped off-centre, half in shadow, doubtful, a "
              "blurred shoulder in the foreground. " + PLACE,
    "scream": SAME + "Close-up of the FOUNDER with his mouth wide open, screaming, framed off-centre and cropped at "
              "the top of his head, shot past the blurred shoulders of two of the others turned toward him in the "
              "foreground, shocked. " + PLACE,
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
    cast = host(CAST_SHEET)
    jobs = [(n, [cast, loft]) for n in SHOTS]
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        for status in ex.map(lambda j: gen(*j), jobs):
            print(status, flush=True)
