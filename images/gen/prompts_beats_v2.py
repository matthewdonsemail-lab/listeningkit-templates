"""Second pass at the Intro 1 beat images (33.40-45.45): composed shots, not pin-ups.
Each beat is built on one device from dark-composition practice: frame within a frame, reflection/doubling
(Perfect Blue), extreme negative space with a tiny figure, overhead symmetry, split light, foreground occlusion.
Kept from v1 (matt liked them): 03 eyes close-up, 06 particle double, 11 lips close-up."""
import json
import os

REFS = [
    "https://treg.to/m/MaLh0A5vPjGqduwt0KCM52fwO19_xTd8.png",
    "https://treg.to/m/Qfkukbkn-PXJRgFHYd6Kb3hLywvMx-8m.png",
    "https://treg.to/m/uTd8JblSXnuUPq94To1pzVCdkR1W5qa9.png",
]
STYLE = ("Same character as the reference images: the anime girl with long wavy black hair, blunt bangs and the white "
         "headband with round ear clips. Same art style: 90s cel-shaded anime film, deep midnight blue monochrome, "
         "electric blue light. Layout like a cinematic anime film by Satoshi Kon or Mamoru Oshii: a deliberate, "
         "unusual composition, hard chiaroscuro, most of the frame in true black, one hard light source. "
         "16:9 frame, no text, no watermark, no logos.")
BEATS = {
    "01_log_ingests": "REFLECTION: we look at the black glass of her laptop screen; her face is only a dim reflection in it, "
                      "and over the reflection the glowing message bubbles slide down into the screen like rain into a "
                      "drain. The physical laptop edge cuts diagonally across the left of the frame in silhouette.",
    "02_every_conversation": "TINY FIGURE, HUGE SCALE: extreme low angle from the floor of a canyon whose two walls are "
                             "built entirely of thousands of glowing message windows, converging to a vanishing point "
                             "high above; she is a tiny silhouette at the bottom of the frame looking up.",
    "04_builds": "PROJECTION ON FACE: lines of glowing text are projected across her face and the wall behind her by a "
                 "single beam from off-frame, like a film projector; half of her face is lost in black, the light text "
                 "wrapping over the contours of her cheek and eye.",
    "05_a_voice_profile": "SILHOUETTE CUT-OUT: her exact side profile in pure black silhouette, cut out against a backlit "
                          "wall of thin vertical glowing bars of different heights like an audio spectrogram; the bars "
                          "trace the shape of her face; only a thin rim of light on her lips and lashes.",
    "07_local_models": "OVERHEAD SYMMETRY: straight top-down god's-eye shot; she sits small in the exact centre of a dark "
                       "floor, inside a perfect ring of glowing monitors and cables laid out like a clock face, the "
                       "light pooling only inside the ring, everything outside is black.",
    "08_re_rank": "FRAME WITHIN A FRAME: seen through a narrow gap in a half-open dark door; beyond it, a long dark "
                  "corridor lined with hanging glowing cards in rows; one card sharp and bright in the near foreground, "
                  "she is small and out of focus at the far end of the corridor.",
    "09_embed": "MACRO, HANDS: extreme close-up of her open palm in the dark, a single drop of light falling into it and "
                "spreading as rings of tiny glowing dots across her skin; her fingers in silhouette, nothing else lit.",
    "10_vector_search": "LAYERED THROUGH GLASS: her face behind a dark pane of glass covered in glowing points connected "
                        "by fine lines like a star chart drawn on the glass; one of the points sits exactly over her "
                        "iris; her face lit only by the points.",
    "12_talk": "THE DOUBLE: she stands facing a dark mirror; her reflection is speaking, a ribbon of light leaving the "
               "reflection's lips, while the real her, in silhouette in the foreground, has her mouth closed.",
}
here = os.path.dirname(os.path.abspath(__file__))
for k, v in BEATS.items():
    body = {"model": "gemini-3-pro-image-preview", "prompt": v + " " + STYLE, "size": "16:9", "resolution": "2K",
            "image_urls": REFS}
    with open(os.path.join(here, "beat2_" + k + ".json"), "w") as f:
        json.dump(body, f)
    print(k)
