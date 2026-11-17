# New video project

> **First time?** This project's image generation and hosting run through [treg](https://treg.to/?ref=matthewdonse-aebsh).
> Sign up with [this link](https://treg.to/?ref=matthewdonse-aebsh), install the CLI
> (`curl -fsSL https://treg.to/install.sh | sh`), run `treg login`, then check it with `treg balance`.

One command sets up a new video the way the Log launch film was made. That means the folders for every stage, an
EffectCraft project ready to open, and docs that prime whoever works on it:

| File | What's in it |
|---|---|
| `BRIEF.md` | matt's brief, word for word. Scope comes only from here |
| `RULES.md` | 19 rules from the launch film: frames before renders, one EffectCraft window, assets that match the style, no Envato or tutorials, read references with numpy and never copy them, editable layers not baked frames, type and transitions under the CRT, 3D as real depth, ask before spending, the render settings, the treg link |
| `PROMPTS.md` | A ready prompt for each stage (references, stills, screens, shots, the big moment, cuts and type, the look, the ending, delivery, the write-up), each naming its skill |
| `PLAN.md` | The stages as a checklist |
| `<name>.ecproj` | An EffectCraft project with the main comp at the right size, fps and length |

```bash
python skills/new-video-project/assets/new_project.py my-new-film --brief "what matt said" --seconds 60
```

It can also be primed from a past session. `session_facts.py` pulls every message matt typed out of a Claude Code
transcript and picks out the rules and corrections ("never", "stop", "why is", "looks bad"...). The agent then turns
those into lines in `RULES.md` and prompts in `PROMPTS.md`. On the launch film's session that was 287 messages and
86 candidates.

```bash
python skills/new-video-project/assets/session_facts.py <session.jsonl> projects/my-new-film
```

## Files
- `assets/new_project.py`: makes the project
- `assets/session_facts.py`: pulls a session's messages and corrections
- `assets/templates/RULES.md` and `assets/templates/PROMPTS.md`: the priming docs every project gets
