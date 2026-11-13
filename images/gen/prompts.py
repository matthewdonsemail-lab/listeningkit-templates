"""Four new Blue Noir shots of the headband girl for Intro 1 (33.5-57 s), via treg / Nano Banana Pro.
References: the three existing Blue Noir stills."""
import json
import os

REFS = [
    "https://treg.to/m/MaLh0A5vPjGqduwt0KCM52fwO19_xTd8.png",  # Blue Noir Headband Portraits
    "https://treg.to/m/Qfkukbkn-PXJRgFHYd6Kb3hLywvMx-8m.png",  # Midnight Blue Conspiracy
    "https://treg.to/m/uTd8JblSXnuUPq94To1pzVCdkR1W5qa9.png",  # Blue Noir Whisper Network
]
STYLE = ("Same character as the reference images: the anime girl with long wavy black hair, blunt bangs and the "
         "white headband with round ear clips. Same art style exactly: 90s cel-shaded anime, deep midnight blue "
         "monochrome, near-black shadows, electric blue rim light, film grain. 16:9 cinematic frame, no text, "
         "no watermark, no logos.")
SHOTS = {
    "A_ingest": "She sits at her laptop in a dark room, face lit from below by the screen. Dozens of small glowing "
                "chat bubbles and message cards stream off the screen and swirl up around her like a current of "
                "light, dissolving into blue particles. Wide shot, camera slightly low.",
    "B_voiceprint": "Extreme close-up of her face in three-quarter profile, eyes half closed, calm. The right half of "
                    "her face and hair dissolves into thousands of tiny glowing blue particles that drift away and "
                    "form a horizontal audio waveform across the frame.",
    "C_vectorspace": "She stands alone in total darkness, seen from behind and slightly to the side, looking up. "
                     "All around her floats a vast three-dimensional constellation of glowing blue points connected "
                     "by faint thin lines, some clustered tightly together, like a map of thoughts. Wide shot, deep "
                     "perspective.",
    "D_moat": "Hero portrait: she looks back over her shoulder straight into camera, confident, slight smirk, strong "
              "electric blue rim light outlining her hair and headband, the rest of the frame falling into black. "
              "Medium close-up, shallow depth of field.",
}
here = os.path.dirname(os.path.abspath(__file__))
for k, v in SHOTS.items():
    body = {"model": "gemini-3-pro-image-preview", "prompt": v + " " + STYLE, "size": "16:9", "resolution": "2K",
            "image_urls": REFS}
    with open(os.path.join(here, k + ".json"), "w") as f:
        json.dump(body, f)
    print(k)
