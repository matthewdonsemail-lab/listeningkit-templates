"""One new Blue Noir image per VO beat in Intro 1 (33.40-45.45), via treg / Nano Banana Pro.
Chiaroscuro: one large lit subject against near-total darkness, the point of the line."""
import json
import os

REFS = [
    "https://treg.to/m/MaLh0A5vPjGqduwt0KCM52fwO19_xTd8.png",  # Blue Noir Headband Portraits
    "https://treg.to/m/Qfkukbkn-PXJRgFHYd6Kb3hLywvMx-8m.png",  # Midnight Blue Conspiracy
    "https://treg.to/m/uTd8JblSXnuUPq94To1pzVCdkR1W5qa9.png",  # Blue Noir Whisper Network
]
STYLE = ("Same character as the reference images: the anime girl with long wavy black hair, blunt bangs and the "
         "white headband with round ear clips. Same art style exactly: 90s cel-shaded anime, deep midnight blue "
         "monochrome, electric blue light. Strong chiaroscuro: one subject lit, everything else falling into "
         "near-total black, large negative space. 16:9 cinematic frame, no text, no watermark, no logos.")
BEATS = {
    # Log ingests every conversation you've ever had
    "01_log_ingests": "Low angle, she leans into her laptop in a pitch-black room, only the screen glow on her face and "
                      "hands; a thin stream of tiny glowing message bubbles is being pulled into the screen.",
    "02_every_conversation": "No character: a huge wall of hundreds of glowing chat message bubbles stacked in the dark, "
                             "receding into blackness, a few lit brightly in the foreground.",
    "03_youve_ever_had": "Extreme close-up of her eyes reflecting scrolling glowing messages, the rest of her face in "
                         "deep shadow.",
    # builds a voice profile of you
    "04_builds": "Her silhouette in profile against black, rim lit in electric blue, thousands of glowing particles "
                 "flowing from her lips and assembling into a shape in front of her.",
    "05_a_voice_profile": "No character: a glowing three-dimensional sculpture of a sound waveform made of blue "
                          "particles, floating alone in a black void, lit from within.",
    "06_of_you": "Close-up, her face half lit from the side, half lost in black; a faint particle copy of her face "
                 "glows just behind her, like a reflection made of light.",
    # Local models re-rank, embed and vector search
    "07_local_models": "Wide shot, she stands small in a vast dark chamber facing a monolithic block of glowing blue "
                       "machinery, the only light source, her shadow long behind her.",
    "08_re_rank": "No character: glowing rectangular cards of light hanging in the dark in a vertical column, "
                  "rearranging, one card pulled forward and brighter than the rest.",
    "09_embed": "No character: a single luminous point of light dropping into a dense three-dimensional cloud of "
                "glowing dots in the dark, ripples of light where it lands.",
    "10_vector_search": "She reaches a hand into the dark, a thin beam of blue light shooting from her fingertip "
                        "across a field of floating glowing points, connecting a few of them.",
    # the way you actually talk
    "11_the_way_you_actually": "Close-up of her lips mid-word, lit by a single blue light, the rest of the face in "
                               "shadow, faint glowing particles leaving her lips.",
    "12_talk": "Medium shot, she speaks into the dark with a slight smile, her words visible as a soft ribbon of "
               "glowing light curling away from her into the black.",
}
here = os.path.dirname(os.path.abspath(__file__))
for k, v in BEATS.items():
    body = {"model": "gemini-3-pro-image-preview", "prompt": v + " " + STYLE, "size": "16:9", "resolution": "2K",
            "image_urls": REFS}
    with open(os.path.join(here, "beat_" + k + ".json"), "w") as f:
        json.dump(body, f)
    print(k)
