"""Abstract sigils flashed on the cuts of Intro 1, one per cut, each the idea of the VO at that point.
A matched set: thin glowing line symbols centred on pure black."""
import json
import os

STYLE = ("A single abstract sigil centred on a pure black background, drawn in thin precise glowing electric-blue lines "
         "with a few white-hot points, like an occult diagram crossed with a signal-processing schematic: concentric "
         "circles, tick marks, fine construction lines, small dots and coordinates-like marks, slight CRT phosphor "
         "glow and faint scanline noise. Flat, symmetrical, minimal, lots of black space around it. No text, no "
         "letters, no numbers, no people, no watermark. 16:9 frame.")
SIGILS = {
    "s0600_hourglass": "An hourglass whose sand runs upward, inside a circle of tick marks like a clock face.",
    "s1197_eye": "A single eye drawn as two arcs, half open, with a radar sweep for an iris.",
    "s1927_lone_node": "One small node alone at the centre of an empty orbit ring, broken lines reaching toward it.",
    "s2200_two_faces": "Two face profiles facing each other drawn as one continuous line, sharing a single eye.",
    "s2497_radial_network": "Seven nodes arranged in a ring, all wired to one centre node, signal pulses on the wires.",
    "s3340_inward_spiral": "A spiral of fine dots funnelling inward into a tiny bright point at the centre.",
    "s3667_index": "A grid of short vertical marks of different heights like a barcode wrapped into a circle.",
    "s3800_voiceprint": "A sound waveform folded into a closed loop, forming a ring like a fingerprint.",
    "s4025_lattice": "A wireframe cube made of connected nodes, one node lit brighter than all others.",
    "s4345_mouth": "A mouth drawn as two thin arcs, with three concentric sound arcs leaving it.",
    "s4545_mirror": "A vertical line of symmetry with the same figure mirrored on both sides, one side solid, one dotted.",
    "s4970_key": "A key whose bit is a circuit trace, inside a square frame of corner brackets.",
    "s5290_door": "A tall rectangle of light, a doorway, with thin rays fanning out from it across the black.",
    "s5470_moat": "A small single point inside a thick ring, inside a second ring, like a fortress surrounded by a moat.",
}
here = os.path.dirname(os.path.abspath(__file__))
for k, v in SIGILS.items():
    body = {"model": "gemini-3-pro-image-preview", "prompt": v + " " + STYLE, "size": "16:9", "resolution": "2K"}
    with open(os.path.join(here, "sigil_" + k + ".json"), "w") as f:
        json.dump(body, f)
    print(k)
