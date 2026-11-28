"""Make a new video project, set up the way the Log launch film was built (matt, 2026-11-17).

Creates projects/<name>/ in listeningkit-templates with the folders every stage uses, a real EffectCraft project
(<name>.ecproj with a main comp at the size, fps and length given), and the priming docs:
  BRIEF.md    matt's brief, word for word (from --brief or --brief-file)
  RULES.md    the rules learned on the launch film (templates/RULES.md)
  PROMPTS.md  a ready prompt for every stage, each naming the skill to load (templates/PROMPTS.md)
  PLAN.md     the stages to tick off, with the skill for each
  README.md   what's where
  .gitignore  media stays local (stills, renders, references); scripts, prompts and docs are committed

  python skills/new-video-project/assets/new_project.py <name> --brief "what matt said" [--size 1920x1080]
         [--fps 30] [--seconds 60] [--no-ecproj]

Never overwrites: it stops if projects/<name>/ already exists."""
import argparse
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
CLI = "C:/Users/0/effectcraft/target/release/effectcraft-cli.exe"
FOLDERS = {
    "ref": "references matt gives: downloaded videos, frames he picked",
    "ref/sheets": "numbered frame sheets to pick from",
    "gen": "generated stills (and the prompts script that made them)",
    "assets/seeds": "numpy seeds pulled from the references",
    "assets/luts": "grades",
    "assets/sprites": "UI elements and other rebuilt pieces",
    "assets/collage": "generator output frames",
    "plugins": "the JSX that builds the EffectCraft comps (rerunnable)",
    "audio": "VO, music, sound",
    "frames": "stills and contact sheets for matt to look at",
    "renders": "quarter-quality checks and finals",
}
PLAN = [
    ("Kick-off: brief summarised back, stages picked", "-"),
    ("References downloaded, frame sheets made, frames picked", "numpy-fx-extraction"),
    ("Seeds pulled and generators built", "seed-path-generators"),
    ("Anchor still approved, then the chained stills", "locked-image-generations"),
    ("Screens and UI built live", "screen-ui-typing"),
    ("Camera moves and grade on every shot", "shot-camera-realism, grade-and-thermal-cuts"),
    ("The big moment", "cyberpsycho-cut, eye-echo"),
    ("Transitions on every cut", "glitch-cut-transitions"),
    ("VO type in the negative space", "crt-negative-space-type"),
    ("CRT / VHS look over it", "crt-vhs-look"),
    ("Ending, end card, outro audio", "end-card-and-outro"),
    ("Quarter render watched, then the full render + .srt", "filmcraft-talking-edit (render step)"),
    ("Process board and skills updated", "-"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("name")
    ap.add_argument("--brief", default="")
    ap.add_argument("--brief-file")
    ap.add_argument("--size", default="1920x1080")
    ap.add_argument("--fps", type=float, default=30)
    ap.add_argument("--seconds", type=float, default=60)
    ap.add_argument("--no-ecproj", action="store_true")
    a = ap.parse_args()
    root = os.path.join(REPO, "projects", a.name)
    if os.path.exists(root):
        sys.exit(f"{root} already exists: not touching it")
    brief = open(a.brief_file, encoding="utf-8").read() if a.brief_file else a.brief
    w, h = (int(v) for v in a.size.lower().split("x"))

    for f in FOLDERS:
        os.makedirs(os.path.join(root, f))
    put = lambda n, s: open(os.path.join(root, n), "w", encoding="utf-8").write(s)
    tpl = lambda n: open(os.path.join(HERE, "templates", n), encoding="utf-8").read().replace("{{NAME}}", a.name)

    put("BRIEF.md", f"# Brief: {a.name}\n\nmatt's words, unedited. Scope and options come only from here.\n\n"
                    + ("\n".join("> " + l for l in brief.strip().splitlines()) if brief.strip() else "> (paste it here)")
                    + f"\n\n- Size: {w}x{h}, {a.fps:g} fps, about {a.seconds:g} s\n")
    put("RULES.md", tpl("RULES.md"))
    put("PROMPTS.md", tpl("PROMPTS.md"))
    put("PLAN.md", f"# Plan: {a.name}\n\nTick each stage off when matt has seen it. Skip what the brief doesn't need.\n\n"
                   + "\n".join(f"- [ ] {s}  (skill: {k})" for s, k in PLAN) + "\n")
    put("README.md", f"# {a.name}\n\nStart with `RULES.md`, then `BRIEF.md`, then `PROMPTS.md`.\n"
                     f"Skills: `../../skills/README.md`. EffectCraft project: `{a.name}.ecproj`.\n\n"
                     + "\n".join(f"- `{f}/`: {d}" for f, d in FOLDERS.items()) + "\n")
    put(".gitignore", "# media stays local; scripts, prompts and docs are committed\n"
                      "ref/**/*.mp4\nref/**/*.png\nref/**/*.jpg\ngen/**/*.png\ngen/**/*.jpg\nassets/collage/\n"
                      "audio/\nframes/\nrenders/\n*.ecproj.bak*\n")
    for f in FOLDERS:
        open(os.path.join(root, f, ".keep"), "w").close()

    if not a.no_ecproj:
        proj = os.path.join(root, a.name + ".ecproj").replace("\\", "/")
        js = (f"app.newProject(); var c=app.project.items.addComp('{a.name}',{w},{h},1,{a.seconds},{a.fps});"
              f"app.project.save(new File('{proj}')); writeLn('saved');")
        r = subprocess.run([CLI, "script", "--eval", js], capture_output=True, text=True)
        print(("made " + proj) if os.path.exists(proj) else ("EffectCraft project not made: " + r.stdout[-300:] + r.stderr[-300:]))
    print("made", root)
    for n in sorted(os.listdir(root)):
        print("  ", n)


if __name__ == "__main__":
    main()
