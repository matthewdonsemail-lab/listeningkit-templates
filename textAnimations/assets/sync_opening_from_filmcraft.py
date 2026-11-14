"""The launch film's opener from matt's FilmCraft cut (matt, 2026-11-15): reads the FilmCraft project
(C:/Users/0/filmcraft/projects/launchIntro/launchIntro-v1.fcproj, sequence "intro") and writes assets/opening_edit.json
with every picture clip at its own timestamps and Motion (anchor, position, scale), so make_opening_comp.py rebuilds the
EffectCraft "opening" comp as the same edit. Nothing is rendered: each clip comes in as its own still or video.
The sound is not copied: "launch film" already plays the VO (projects/cyberpunk/audio.mp3) and the music
(assets/audio/launch_music.wav) from 0, the way the FilmCraft sequence does.
Usage:
  python assets/sync_opening_from_filmcraft.py [path/to/project.fcproj]
  python assets/make_opening_comp.py
  effectcraft-cli --project textAnimations.ecproj script plugins/openingDawn.jsx --save"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FC = sys.argv[1] if len(sys.argv) > 1 else "C:/Users/0/filmcraft/projects/launchIntro/launchIntro-v1.fcproj"
EDIT = os.path.join(HERE, "opening_edit.json")
TICKS = 254016000000  # FilmCraft ticks per second

d = json.load(open(FC, encoding="utf8"))
items = d["project"]["items"]
seq = next(it for it in items.values() if it["name"] == "intro" and "Sequence" in it["kind"])["kind"]["Sequence"]
fr = seq["settings"]["frame_rate"]
fps = fr["num"] / fr["den"]
frame = TICKS / fps


def plain(path):
    """forward slashes, without the long-path prefix (//?/) FilmCraft keeps on files imported through its control port"""
    path = path.replace("\\", "/")
    return path[4:] if path.startswith("//?/") else path


def val(params, k):
    return list(params[k]["value"].values())[0]


shots = []
for ti, track in enumerate(seq["video_tracks"]):
    if not track.get("enabled", True):
        continue
    for c in track["items"]:
        if not c.get("enabled", True):
            continue
        media = items[str(c["item"])]["kind"]["Media"]
        m = next(e for e in c["effects"] if e["effect"] == "motion")["params"]
        a, p = val(m, "anchor"), val(m, "position")
        shots.append({
            "name": os.path.splitext(c["name"])[0],
            "in": int(round(c["start"] / frame)),
            "out": int(round((c["start"] + c["duration"]) / frame)),
            "src": plain(media["media"]["File"]["path"]),
            "video": media["info"]["kind"] == "Movie",
            "sourceIn": int(round(c.get("source_in", 0) / frame)) if media["info"]["kind"] == "Movie" else 0,
            "track": ti + 1,
            "anchor": [a["x"], a["y"]],
            "position": [p["x"], p["y"]],
            "scale": val(m, "scale"),
        })
shots.sort(key=lambda s: (s["track"], s["in"]))
frames = max(s["out"] for s in shots)
old = json.load(open(EDIT, encoding="utf8")) if os.path.exists(EDIT) else {}
out = {
    "about": "The launch film's opener, matt's FilmCraft cut (%s, sequence intro), synced by "
             "assets/sync_opening_from_filmcraft.py: every picture clip at its timestamps and Motion, track 2 on top "
             "(the cyberpsycho shout, make_opening_psycho_cut.py). cyberStart: the frame cyberpunk's own time 0 sits at."
             % os.path.basename(FC),
    "fps": int(fps) if math.isclose(fps, round(fps)) else fps,
    "frames": frames,
    "cyberStart": old.get("cyberStart", frames),
    "flash": None,
    "shots": shots,
}
json.dump(out, open(EDIT, "w", encoding="utf8"), ensure_ascii=True, indent=1)
print("%d clips, %d frames -> %s" % (len(shots), frames, EDIT))
