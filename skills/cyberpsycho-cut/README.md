# Cyberpsycho cut

> **First time?** The image generations here run through [treg](https://treg.to/?ref=matthewdonse-aebsh). Sign up with
> [this link](https://treg.to/?ref=matthewdonse-aebsh), install the CLI (`curl -fsSL https://treg.to/install.sh | sh`), run `treg login`,
> then check it with `treg balance`.


## What it is

Two men shouting at each other in the launch opener, cut against each other on the beat from the drop at
00:00:10:08. Each one turns step by step from a photograph into the red, black and white "cyberpsycho" look. His
cyberpsycho face breaks through his real face in rectangles over his eyes, brows, nose, mouth and cheeks. His eyes
echo outwards, white jagged lines shoot out of his eyes, and other backgrounds are glitch-cut in behind him. Built
2026-11-15 for the comp `opening` in `textAnimations/textAnimations.ecproj`.

## The reference

![sun_ae reference frames](images/01_reference_sun_ae.jpg)
*The influence: the red sun_ae TikTok (`projects/opening/ref/sun_ae`), frames 177-224 as matt picked them. Hard red,
black and white, white jagged outlines, screaming faces multiplied and echoing outwards, glitch blocks, the cyberware
HUD. (`textAnimations/assets/collage/process/sun_ae_picked.jpg`)*

![The 12 style references](images/02_style_refs_per_step.jpg)
*One sun_ae frame per step (`projects/opening/psycho/styleref_sun/style_00-11.png`), given to the image model as the
look for that step.*

## How it works

### Step 1: 12 cyberpsycho steps per man, camera locked

`images/gen/make_opening_psycho.py` asks Nano Banana Pro (through [treg](https://treg.to/?ref=matthewdonse-aebsh)) for 12 versions of each shot. Each call gets
three images: the real shot (keep this composition exactly), matt's monster still (the expression it ends on) and that
step's sun_ae frame (the look). The prompt walks through 12 stages, from "still a real photograph; his jaw clenches"
to "the final cyberpsycho: the monster scream at its widest, a fan of many screaming copies of his face". The camera
stays put, so every step cuts straight from the one before.

![The blinds man in 12 steps](images/03_steps_blinds.jpg)
*Step 1 result for the man behind the blinds, `projects/opening/psycho/blinds/blinds_00-11.png`.*

![The chalkboard man in 12 steps](images/03_steps_chalk.jpg)
*Step 1 result for the man at the chalkboard, `projects/opening/psycho/chalk/chalk_00-11.png`.*

The same was done for real footage of the two men talking (`images/gen/make_opening_psycho_speakers.py`), with a frame
grabbed from the clip as the composition reference:

![Sam's steps](images/04_steps_sam.jpg)
*Step 1 on footage: the grabbed clip frame (`sam_ref.png`, top left), then his steps 00-10
(`projects/opening/psycho/sam/`).*

### Step 2: each man cut off his background

`textAnimations/assets/make_opening_psycho_matte.py` draws a head ellipse and a shoulders polygon round each man, and
uses it to seed OpenCV GrabCut: the shrunk shape is sure foreground, the shape probable foreground, a band round it
probable background, the rest sure background. Then it keeps the biggest piece, fills holes and softens the edge.
With the matte, the effects stay on him and the background can be cut up separately.

![GrabCut mattes](images/05_grabcut_mattes.jpg)
*Step 2: each shot, its matte (`projects/opening/psycho/<shot>_matte.png`) and the man cut out over red.*

### Step 3: the cut

`textAnimations/assets/make_opening_psycho_cut.py` builds every frame:

1. **Before the drop**, the original edit: the blinds shot from 8.43 s, the chalkboard from 9.37 s. These are the
   real frames with no cyberpsycho, but now and then their real eyes echo outwards, more often as the drop comes.
2. **Everything aligned on the eyes.** Each of the 12 stills is scaled and moved so his eyes sit where they are in
   the real shot, so a rectangle cut from any step lands on his face in place.
3. **From the drop**, a hard cut between the two men on every half-beat of the music (0.39 s beats), every
   quarter-beat in the last 40%. The step climbs from 1 to 12 over time.
4. **Over his face**, rectangles cut from his steps over the face parts (measured from the eye distance: eye band,
   eyes, brows, forehead, nose, mouth, cheeks, jaw, halves, the whole face). Each cut starts with big pieces and
   breaks into small ones, and each cut is crazier than the last. Some pieces get a red/blue split.
5. **His eyes echo outwards**: 2-4 copies of an eye, each from a different step, in different sizes, stepping out
   (see the `eye-echo` skill).
6. **Behind him**, through his matte, his own background with blocks of the other man's background and the red
   stills cut in.
7. **The lines**: white jagged cyberpsycho lines (`textAnimations/plugins/cyberpsycho/cyberpsycho.py`) start inside
   his eyes and shoot outward, redrawn every 2 frames, glitched in the last 40%. That part also adds band slips,
   dropouts and a white flash frame on the beats.

![Frames from the cut](images/06_cut_frames_v9.jpg)
*Step 3: 24 frames evenly through `textAnimations/assets/collage/opening_psycho_v9.mp4`. The top row is before the
drop (with the first frame of the second row), showing the real shots and real eye echoes. After that it alternates between the two men, with face
rectangles from the red steps, the lines out of the eyes and background blocks, getting denser towards the end.*

### Step 4: into EffectCraft

The clip goes into the pre-comp `opening 12 opening_psycho_vN` on track 2 of comp `opening` (frames 253-450).
`textAnimations/plugins/openingPsychoSwap.jsx` swaps in a new render without touching the inserts, the VHS look or
the CRT. From the drop the CRT-Emulator build (style 10) runs over it, and the switches get the thermogram transition
(`plugins/openingThermal.jsx`). The cut itself is a rendered clip, not editable layers.

## In the film

![The cut in the final film](images/07_in_the_film.jpg)
*`textAnimations/renders/launch_film_final_full.mp4` from 00:00:10:24 to 00:00:13:10, under the CRT with the
captions: the two men alternating, the red face rectangles and the white lines out of the eyes. The CRT turns it blue.*

| Timecode (launch film) | What |
| --- | --- |
| 00:00:08:13 (8.43 s) | the clip starts: the blinds shot, real |
| 00:00:09:11 (9.37 s) | the chalkboard shot |
| 00:00:10:08 (frame 308) | the beat drops: the cyberpsycho cut starts, the CRT starts |
| 00:00:15:00 | cyberpunk takes over |

The same treatment on the outro busts (`textAnimations/assets/make_bust_lines.py`) adds a quadrant swap: one or two
quarters of the frame cut to his other versions every couple of frames.

![The busts with the quadrant swap](images/08_busts_quadrants.jpg)
*`textAnimations/assets/collage/bust_lines.mp4`, bust 2: frame 44 is the line wiping round him. From frame 47 (the
apex) the quadrants flip to his low-poly / dither versions, with face rectangles, eye echoes and the lines out of his
eyes.*

## Files

| File | What it does |
| --- | --- |
| `images/gen/make_opening_psycho.py` | the 12 steps for each still shot |
| `images/gen/make_opening_psycho_speakers.py` | the 12 steps for each speaker clip |
| `textAnimations/assets/make_opening_psycho_matte.py` | the GrabCut mattes |
| `textAnimations/assets/make_opening_psycho_cut.py` | the cut (mp4, or `--frames` stills) |
| `textAnimations/plugins/cyberpsycho/cyberpsycho.py` | the jagged lines |
| `textAnimations/plugins/openingPsychoSwap.jsx` | swaps the clip in the EffectCraft project |
| `textAnimations/assets/make_bust_lines.py` | the busts version, with quadrants |
| `textAnimations/OPENING.md` | the opener's docs |
| `projects/opening/psycho/` | the steps, mattes and style references |

## Assets

Everything this skill needs to run again (scripts, plugins, LUTs, seeds, sprites, data) is copied into
[`assets/`](assets/MANIFEST.md) at the same paths it has in the repo. The manifest lists what's bundled, what's shared with
another skill, and which big media (renders, projects, reference videos) stays in the repo.
