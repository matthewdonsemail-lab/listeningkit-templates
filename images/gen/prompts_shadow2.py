"""Shadow-clone pass, retakes: 05 (the shadow must visibly turn to her) and 08 re-rank (her shadow sorting)."""
import json
import os

from prompts_shadow import BASE, STYLE

SHOTS = {
    "05_a_voice_profile": "Wide, flat, symmetrical side view: she sits at her desk on the left, facing right toward her "
                          "screen, lit by it. Her shadow is cast large on the wall to the RIGHT of her, and the shadow "
                          "is NOT copying her: the shadow faces LEFT, back toward her, looking straight at the real "
                          "girl, the two profiles nose to nose across the frame, as if the shadow is studying her face.",
    "08_re_rank": "A wall in the dark with a single hard beam of light raking across it. Between the light and the wall "
                  "hang rows of small cards on strings, so the wall is covered in their hard rectangular shadows. Her "
                  "shadow's hand reaches in from the edge of the frame and pulls one card-shadow forward, out of line; "
                  "only her real hand's fingertips are visible in the near foreground, in black silhouette.",
}
here = os.path.dirname(os.path.abspath(__file__))
for k, v in SHOTS.items():
    body = {"model": "gemini-3-pro-image-preview", "prompt": v + " " + STYLE, "size": "16:9", "resolution": "2K",
            "image_urls": BASE}
    with open(os.path.join(here, "shadow2_" + k + ".json"), "w") as f:
        json.dump(body, f)
    print(k)
