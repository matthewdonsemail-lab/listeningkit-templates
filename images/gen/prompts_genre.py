"""Genre swaps of frames from the anime-girl footage: the SAME composition (framing, pose, head position, horizon)
re-imagined in another genre, so they can be cut in as graphic matches. One source frame per image."""
import json
import os

KEEP = ("Keep the exact composition of the reference image: same framing, same camera angle, same position and size "
        "of the girl in the frame, same pose and head angle, same horizon line. Same girl: long wavy black hair, "
        "blunt bangs, white headband. 16:9, no text, no watermark.")
F = {
    "hill": "https://treg.to/m/8PwZ72d9QbWwcz4wsCOuiQ8nH7tdgO0n.png",
    "glance": "https://treg.to/m/wwJNp3-Vz6RBaESi7LH35zKjwGYGdqft.png",
    "front": "https://treg.to/m/caA_yZb9dd71oKFVBb9hxruaydYE0BOZ.png",
    "down": "https://treg.to/m/LPQGgCgYO7tu-7qV2-WQGEBMVybLA3EJ.png",
    "glance2": "https://treg.to/m/v2JA-ywkW6VMxiTwDh6jARTUIR3O9Wo8.png",
}
SHOTS = {
    "hill_hyperreal": ("hill", "Hyperrealistic photograph, 35mm film, a real young woman standing tiny on the crest "
                               "of a windswept grass hill under a vivid blue sky with white cumulus clouds, wind in "
                               "her hair and dress, natural light."),
    "glance_surreal": ("glance", "Surrealist painting in the manner of Magritte: the same over-the-shoulder glance, "
                                 "but her hair is made of the night sky with stars while the background is bright "
                                 "daytime clouds; the grass hill behind her is a calm sea of white paper."),
    "front_hyperreal": ("front", "Hyperrealistic studio-lit photograph portrait of a real young woman, skin texture, "
                                 "wind in her hair, the blue sky and clouds behind her, shallow depth of field."),
    "front_ps2": ("front", "A PlayStation 2 era video game cutscene render: low-polygon 3D character, blurry "
                           "low-resolution textures, stiff glossy hair mesh, simple gouraud shading, slight jagged "
                           "edges, early 2000s in-game look, mouth closed."),
    "down_nonsequitur": ("down", "A random non-sequitur juxtaposition: everything identical except she is underwater "
                                 "in a vast aquarium, eyes closed, a goldfish swimming past her headband, the clouds "
                                 "are now jellyfish; photographed realistically."),
    "glance_oil": ("glance2", "A baroque oil painting in the style of Caravaggio: dramatic chiaroscuro, dark "
                              "background replacing the sky, a single warm light on her face and hair, visible "
                              "brush strokes and craquelure."),
}
here = os.path.dirname(os.path.abspath(__file__))
for k, (src, v) in SHOTS.items():
    body = {"model": "gemini-3-pro-image-preview", "prompt": v + " " + KEEP, "size": "16:9", "resolution": "2K",
            "image_urls": [F[src]]}
    json.dump(body, open(os.path.join(here, "genre_" + k + ".json"), "w"))
    print(k)
