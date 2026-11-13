"""Shadow-clone pass (Intro 1). The clone is her SHADOW: one hard light (her screen) throws her shadow on the wall,
the shadow copies her, speaks for her, and stays working when she walks out. Chiaroscuro does the storytelling:
foreground vs background, what the light touches. Rules: RESEARCH/NEO_NOIR_SHOT_STYLE.md."""
import json
import os

BASE = [
    "https://treg.to/m/MaLh0A5vPjGqduwt0KCM52fwO19_xTd8.png",
    "https://treg.to/m/Qfkukbkn-PXJRgFHYd6Kb3hLywvMx-8m.png",
    "https://treg.to/m/uTd8JblSXnuUPq94To1pzVCdkR1W5qa9.png",
]
STYLE = ("Same girl as the reference images (long wavy black hair, blunt bangs, white headband with round ear clips), "
         "same 90s cel-shaded anime film style, midnight blue monochrome. NEO-NOIR CHIAROSCURO: a single hard light "
         "source and nothing else, no fill light, at least seventy percent of the frame pure black, hard-edged "
         "shadows, faint haze in the light beam. No glowing holograms, no particles, no visible text or user "
         "interface, no screens facing camera. 16:9 cinematic frame, no watermark.")
SHOTS = {
    "01_log_ingests": "The only light is her laptop screen (screen faces away from camera). Low angle from beside the "
                      "desk: the laptop lid in black silhouette in the near foreground; her face lit cold from below, "
                      "tired; behind her on the bare wall her shadow is cast huge, three times her size, filling the "
                      "background.",
    "02_every_conversation": "Dutch angle, tight close-up: the light from her screen falls across her face through the "
                             "slats of a half-closed blind, throwing hard horizontal bars of light and shadow over her "
                             "eyes and cheek, as if she is behind bars; most of her face in shadow.",
    "05_a_voice_profile": "Wide, flat, symmetrical: she sits at her desk in profile on the left, lit by the screen; on "
                          "the wall behind her, her shadow is cast in profile too, but the shadow has turned its head "
                          "and is looking at her, while she still looks at the screen.",
    "06_of_you": "She stands facing the wall in the near foreground, back to camera, a black silhouette; on the wall in "
                 "front of her the screen light throws TWO shadows of her, side by side, one copying her pose, one "
                 "slightly different, its head tilted.",
    "12_talk": "Extreme close-up profile of her face on the left, lips closed, lit by a thin slice of light; on the wall "
               "to the right her shadow's profile has its mouth open, speaking, the light sharp on the edge of the "
               "shadow's lips.",
    "13_time_back": "Deep wide shot of her dark room: on the right, the open door to a bright corridor; she walks out "
                    "through it, a small black silhouette against the white light, free. On the left, the desk lit by "
                    "the laptop, and on the wall above it her shadow sits hunched forward at the keyboard, still "
                    "working, though no one is at the desk.",
}
here = os.path.dirname(os.path.abspath(__file__))
for k, v in SHOTS.items():
    body = {"model": "gemini-3-pro-image-preview", "prompt": v + " " + STYLE, "size": "16:9", "resolution": "2K",
            "image_urls": BASE}
    with open(os.path.join(here, "shadow_" + k + ".json"), "w") as f:
        json.dump(body, f)
    print(k)
