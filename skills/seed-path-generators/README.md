# seed path generators

> **First time?** This project's image generation and hosting run through [treg](https://treg.to/?ref=matthewdonse-aebsh). Sign up with
> [this link](https://treg.to/?ref=matthewdonse-aebsh), install the CLI (`curl -fsSL https://treg.to/install.sh | sh`), run `treg login`,
> then check it with `treg balance`.


## What it is

A way to get the red lines, cracks, slashes and flashes of the Edgerunners 2 trailers into our film without copying a
single reference pixel. numpy reads the shapes out of the reference frames: red masks, thinned to one-pixel
skeletons and traced into paths. These are saved as **seeds** (JSON paths with width profiles, PNG masks), alongside
the measured colours, widths, run lengths and angles. Generators then draw a **new variation every frame**, either
along a path or round or out of a matte: a word, a face, the eyes, a bust, the girl. The output is transparent
layers that EffectCraft places as their own layers.

## The references

![Edgerunners 2 trailer, frames 1020-1139](images/01_trailer_red_lines_ref.jpg)
*The reference for the red lines: Edgerunners 2 trailer (`urV5GzXcXsQ`), frames 1020-1139
(`cyberpunk_edits/urV5GzXcXsQ/lines_1029_sheet.jpg`). It has glowing cracks running down through the title cards and
flat red slashes looping over the shots.*

![Edgerunners 2 Teaser #2 at 1:24](images/02_teaser_red_flash_ref.jpg)
*The reference for the red flash: Teaser #2 (`QBlPg818lGI`) at 1:24, frames 23-30 (`at124_tear.jpg`). It goes bar,
torn slabs, the eye in the slab, rings, full red.*

![The ECG line, the trailer's first second](images/05_ecg_line_sheet.jpg)
*The reference for the heartbeat line: the ECG line from the first second of the trailer, cut out onto transparency
frame by frame (`yt_line/line_sheet.jpg`, 19 frames).*

## How it works

### 1. Mask, skeleton, trace, seed

- **Red lines** (`plugins/redlines/redlines.py extract`): each trailer frame at 640x360 gets an HSV red mask. Dark
  title-card frames give crack seeds and shot frames give slash seeds. The mask is thinned to a skeleton (Zhang-Suen,
  in numpy) and walked into polylines. Each polyline is stored relative to its own chord: its wobble, its width
  profile (from the distance transform), its length and its angle.
- **Red flash** (`plugins/redflash/seed.py extract`): each teaser frame gives its red mask (`seed_NN.png`). The dark
  line work inside the red is skeletonised and traced into paths (`seed_NN.json`).

![Red lines: reference, seeds, generated](images/03_redlines_sheet.jpg)
*Steps 1-2 for the red lines (`plugins/redlines/redlines_sheet.jpg`). Row 1: the trailer frames. Row 2: the numpy
skeletons the seeds come from. Row 3: new cracks generated through a stand-in "THE ANIME" card. Row 4: new slashes
generated round a bust's matte.*

### 2. Generate along a path or out of a matte

- **cracks** follow a path down the frame. They use straight runs drawn from the measured length and angle quartiles,
  sharp kinks, now and then a "Z" fold back across, forks and a sideways scan tear, in glowing (236, 37, 58). Given
  the text matte, every point is pushed out of the letters, so the crack bends round each one.
- **slashes** loop round a matte: its outline is pushed out, an arc of it is taken, and the ribbon swoops off past
  the frame. Each ribbon carries a seed's wobble and width profile and is flat (231, 0, 58) with hard edges, thorns
  and tapered points.
- **red flash** takes each of the 7 seed masks and flips, tilts, scales and slides it. It then warps it with two
  random displacement fields (big folds plus a fine tear) and redraws its line paths with the cyberpsycho pen in red
  on near-black, with the CRT stripe, glow and noise.
- **heartbeat** draws an ECG path (P, Q, R, S, T) through each card's big word with the cyberpsycho pen. It is drawn
  on over 12 frames with a hot head, erased from the left from frame 18, and redrawn on twos.

![Red flash: teaser, seeds, generated](images/04_redflash_seeded.jpg)
*Steps 1-2 for the red flash (`assets/collage/redflash_seeded.jpg`). Row 1: teaser frames 23-29. Row 2: their numpy
seed masks. Rows 3-5: three generated flashes (a, b, c), each frame a new warp of its seed.*

![A new drawing every frame](images/07_lines_animated_check.jpg)
*Step 2: three consecutive frames of the slashes round "HUMANS". Each frame is a new drawing from the same seeds
(`assets/collage/lines_animated_check.jpg`).*

### 3. Into EffectCraft

Each generator writes RGBA PNG sequences (one folder per card or shot). A `plugins/*.jsx` script imports each folder
as a sequence and adds it as a named layer in the right comp: `card cracks N` under the type, `card slashes N` over
it, `end trans N` for the flashes. The type, background colour and CRT stay editable, and rerunning the script
replaces the layers. Card positions and the text matte are read from the project itself through the EffectCraft
CLI.

## The result in the film

![The ending cards with cracks and slashes](images/08_ending_redlines_stills.jpg)
*The ending cards (00:00:37:13 - 00:00:58:09 in the film): slashes looping round HUMANS, DEFEATS and YOU'VE, and
cracks down through WHEN and BECOMING. The top row is clean and the bottom row is under the CRT
(`assets/collage/ending_redlines_stills.jpg`).*

![Frames from the final render](images/10_film_frames.jpg)
*Frames from `textAnimations/renders/launch_film_final_full.mp4`. 00:31:00 and 00:31:12: a bust with its line wiping
round him in right-angle steps, then the face glitch at the apex (`make_bust_lines.py`). 00:38:06 and 00:42:15:
slashes round HUMANS and DEFEATS. 00:40:27 and 00:44:00: cracks on SYSTEMATICALLY and through BECOMING. 00:38:27: a frame
of the seeded red flash under the film's look. 00:45:15: the OPPORTUNITIES card.*

![The red flash between two cards](images/11_film_red_flash.jpg)
*The seeded red flash in the film, frames 1166-1170 (00:00:38:26 - 00:00:39:00), the second card change of the
ending. It shows bar, slab, eye, rings and fill, coloured by the film's look on top.*

![The girl's flash cuts with slashes round her](images/09_girl_inserts.jpg)
*The girl's flash cuts (00:00:38:20 - 00:00:57:18): her matte found with GrabCut, red slashes looping round her, a new
drawing every frame (`assets/collage/girl_inserts_sheet.jpg`).*

## Files

| File | Role |
|---|---|
| `textAnimations/plugins/redlines/redlines.py` | red-line extract, seeds, `cracks()`, `slashes()`, sheet |
| `textAnimations/plugins/redlines/seeds/` | `cracks.json`, `slashes.json`, `mask_NNNN.png` |
| `textAnimations/plugins/redflash/seed.py` | red-flash extract, seeds, `generate()`, `flash()`, sheet |
| `textAnimations/plugins/redflash/seeds/` | `seed_01-07.png` / `.json` |
| `textAnimations/plugins/redflash/redflash.py` | the earlier procedural (unseeded) red flash |
| `textAnimations/plugins/cyberpsycho/cyberpsycho.py` | the pen all line generators draw with |
| `textAnimations/assets/make_ending_redlines.py` | cracks/slashes per ending card -> `collage/redlines/` |
| `textAnimations/assets/make_ending_transitions.py` | red flash on every third card change -> `collage/endtrans/` |
| `textAnimations/assets/make_ending_girl_inserts.py` | slashes round the girl, cracks through giant words |
| `textAnimations/assets/make_heartbeat_lines.py` | the ECG line through the cards -> `collage/heartbeat/` |
| `textAnimations/assets/make_bust_lines.py` | the line round each bust + apex glitch -> `collage/bust_lines.mp4` |
| `textAnimations/assets/make_endcard_lines.py` | lines out of the Nous logo, round the Log mark |
| `textAnimations/plugins/endingCards.jsx`, `endingTransitions.jsx`, `endingCrazy.jsx`, `bustLines.jsx`, `endingCardSeq.jsx` | place the layers in EffectCraft |
| `projects/opening/ref/cyberpunk_edits/urV5GzXcXsQ/lines_1029/`, `QBlPg818lGI/at124/`, `projects/opening/ref/yt_line/` | the reference frames |

## Assets

Everything this skill needs to run again (scripts, plugins, LUTs, seeds, sprites, data) is copied into
[`assets/`](assets/MANIFEST.md) at the same paths it has in the repo. The manifest lists what's bundled, what's shared with
another skill, and which big media (renders, projects, reference videos) stays in the repo.
