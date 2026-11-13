"""Story pass for Intro 1 (33.40-57.15): her scene is the clone being made and then working for her.
Three new shots; continuity references are the shots they cut from."""
import json
import os

BASE = [
    "https://treg.to/m/MaLh0A5vPjGqduwt0KCM52fwO19_xTd8.png",  # Blue Noir Headband Portraits
    "https://treg.to/m/Qfkukbkn-PXJRgFHYd6Kb3hLywvMx-8m.png",  # Midnight Blue Conspiracy
]
LAPTOP = "https://treg.to/m/-oH2HxWTY5mhfQykRHTaXdNWEv36MlMS.png"  # 01 laptop reflection
DOUBLE = "https://treg.to/m/bDtiEHiN4J6HUG8H5xpQ1qZ7qwhrJkzr.png"  # 06 her particle double
EYES = "https://treg.to/m/c_6RqwGREiBiPQJ8hrepSoSTuoB--hHS.png"    # 03 eyes close-up
STYLE = ("Same character as the reference images: the anime girl with long wavy black hair, blunt bangs and the white "
         "headband with round ear clips. Her clone is the same girl made entirely of glowing blue particles, as in the "
         "reference with the particle double. Same art style: 90s cel-shaded anime film, deep midnight blue monochrome, "
         "electric blue light, hard chiaroscuro, most of the frame in true black, a deliberate cinematic layout like "
         "Satoshi Kon or Mamoru Oshii. 16:9 frame, no text, no watermark, no logos, no warning or error icons.")
SHOTS = {
    "02_every_conversation": (
        "Extreme low angle: she stands tiny at the bottom centre of the frame looking straight up into a towering "
        "canyon whose walls are thousands of glowing chat message windows; the messages stream DOWNWARD toward her "
        "like falling rain, converging to a vanishing point high above.", [LAPTOP, EYES]),
    "08_re_rank": (
        "Frame within a frame: through a dark doorway we see a long corridor of hanging glowing message cards; her "
        "particle clone stands in the corridor, reaching out and pulling one card forward so it glows brightest; the "
        "real girl stands in the near foreground in black silhouette, watching her clone.", [DOUBLE]),
    "13_time_back": (
        "Wide shot, deep space: the real girl walks away from her dark desk toward an open doorway of soft pale light, "
        "seen from behind, free; behind her at the desk her glowing particle clone sits at the laptop, working, small "
        "glowing social feed windows floating around it. The doorway frames her; the clone is the only other light.",
        [DOUBLE, LAPTOP]),
}
here = os.path.dirname(os.path.abspath(__file__))
for k, (v, extra) in SHOTS.items():
    body = {"model": "gemini-3-pro-image-preview", "prompt": v + " " + STYLE, "size": "16:9", "resolution": "2K",
            "image_urls": BASE + extra}
    with open(os.path.join(here, "story_" + k + ".json"), "w") as f:
        json.dump(body, f)
    print(k)
