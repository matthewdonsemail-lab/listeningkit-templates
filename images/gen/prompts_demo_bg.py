"""One background plate behind every 3D demo shot in Intro 1: her dark room, so the demos sit in her story."""
import json
import os

body = {
    "model": "gemini-3-pro-image-preview",
    "size": "16:9", "resolution": "2K",
    "prompt": ("An empty dark room wall at night, no people, no objects in the centre: cold blue light from an unseen "
               "screen falls through the slats of a half-closed window blind, throwing long diagonal bars of light "
               "across the wall from the upper left, faint haze in the beams, the rest of the frame falling into "
               "deep black. 90s cel-shaded anime film background painting, midnight blue monochrome, hard "
               "chiaroscuro, lots of empty dark space in the middle. No text, no watermark."),
}
here = os.path.dirname(os.path.abspath(__file__))
json.dump(body, open(os.path.join(here, "demo_bg.json"), "w"))
print("demo_bg")
