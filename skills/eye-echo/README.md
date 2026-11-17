# Eye echo

> **First time?** This project's image generation and hosting run through [treg](https://treg.to/?ref=matthewdonse-aebsh). Sign up with
> [this link](https://treg.to/?ref=matthewdonse-aebsh), install the CLI (`curl -fsSL https://treg.to/install.sh | sh`), run `treg login`,
> then check it with `treg balance`.


## What it is

A face's eyes break out sideways. Copies of each eye, in different sizes and often taken from the face's other style
versions, step outwards (the left eye to the left, the right eye to the right) and overlap like stacked frames. On
the opener and the busts, white jagged cyberpsycho lines also shoot out of the eyes. It runs on the opener's two men,
the outro busts and the girl's flash cuts in the ending of the launch film.

## The reference

![sun_ae reference row](images/00_reference_sun_ae.jpg)
*What it's based on: the red sun_ae TikTok (`projects/opening/ref/sun_ae`), frames 185, 188, 193 and 195 from matt's
pick of 177-224, where the faces multiply and echo outwards. (Top row of
`textAnimations/assets/collage/process/eye_effect.jpg`.)*

![cyberpsycho line references](images/08_cyberpsycho_line_refs.jpg)
*The lines: two of the five reference frames in `references/cyberpsycho/` and their red lines isolated by colour
(`ref<n>_iso.png`). `cyberpsycho.py` is measured from these: thin jittery strokes about 7 px wide (at 1242 px) that
swell into tapering blades, stepped right angles, drips and ticks, 9-38 pieces, redrawn on twos.*

## How it works

Each row below is one scene from `eye_effect.jpg`, left to right: **1** the shot, **2** its eyes found (boxes),
**3** the eye echoes alone on black, **4** the echoes on the shot, **5** the same moment in the final film under the
CRT. That sheet is made by `textAnimations/assets/make_eye_effect_sheet.py`, which redraws the echoes the way the
scene scripts do.

### Step 1: find the eyes

For stills, the eyes of every image are read off a grid by hand and written into the script as a table. For moving
footage (the young Sam and Dario clips in the opener) the eyes are marked on the first frame, then OpenCV template
matching follows them frame by frame. Every style version of a face is warped so its eyes land on the base shot's
eyes, so a copy cut from any version lands in the right place.

### Step 2: echo them outwards

For each eye, a box round it (half the eye distance wide) is cut from one of the versions. It is pasted 2-4 times
(2-6 on the girl), each copy scaled 0.7-1.7x and stepped a bit further out, so the copies fan away from the face and
overlap. A new arrangement comes every 2 frames.

### Step 3: lines out of the eyes

An ellipse over each eye becomes the matte for `textAnimations/plugins/cyberpsycho/cyberpsycho.py`. The lines start
inside the eyes and shoot outward: near-white with a thin dark edge, redrawn on twos, glitched (pixel-sorted, band
slips, colour split) as the scene gets crazier.

## The scenes

### The opener's two men

![Opener, blinds](images/01_opener_blinds.jpg)
*The man at the blinds (step 6 of his cyberpsycho): the shot, eyes boxed, the echoes alone, on the shot, and in the
film at 00:00:10:24.*

![Opener, chalkboard](images/02_opener_chalk.jpg)
*The man at the chalkboard (step 8), the same four steps, and in the film at 00:00:12:06.*

![Pre-drop real eye echoes](images/09_predrop_real_eye_echoes.jpg)
*Before the drop at 00:00:10:08 only the real eyes echo, cut from the real frame (`opening_psycho_v9.mp4` frames 10 and
50). From the drop (frame 55 of the clip, frame 60) the lines come out of his eyes and the red cyberpsycho rectangles start.*

### The busts going into the outro

![Bust 2](images/03_bust2.jpg)
*Bust 2: the echoes are cut from his realistic, low-poly and dither versions (the dither shows as the checker
texture). In the film at 00:00:32:15.*

![Bust 4](images/04_bust4.jpg)
*Bust 4, in the film at 00:00:34:19.*

![Bust animation frames](images/10_busts_echo_and_lines.jpg)
*`textAnimations/assets/collage/bust_lines.mp4`, bust 2. Frame 44 is the blue line wiping round him. From frame 47,
where the line closes, his eyes echo outwards, white lines come out of them and the frame's quadrants cut to his
other versions.*

### The girl's flash cuts in the ending

![Girl, eyes2](images/05_girl_eyes2.jpg)
*The photo close-up, in the film at 00:00:38:21.*

![Girl, eyes3_v1](images/06_girl_eyes3_v1.jpg)
*The anime close-up, in the film at 00:00:42:08.*

![Girl, oil](images/07_girl_oil.jpg)
*The oil-painting variant, in the film at 00:00:41:18.*

![Girl inserts](images/11_girl_inserts.jpg)
*The finished inserts (`textAnimations/assets/collage/girlins/ins_01-06/f_02.jpg`): the echoes, face rectangles from
her other shots, and on some a quadrant from another shot. On the girl the lines are the red slashes from
`plugins/redlines` looping round her, not the cyberpsycho lines.*

## Timecodes in the launch film

These are the frames `make_eye_effect_sheet.py` samples from `textAnimations/renders/launch_film_final_full.mp4`:

| Timecode | Scene |
| --- | --- |
| 00:00:10:24 | opener, the blinds man |
| 00:00:12:06 | opener, the chalkboard man |
| 00:00:32:15 | bust 2 |
| 00:00:34:19 | bust 4 |
| 00:00:38:21 | girl, photo close-up |
| 00:00:41:18 | girl, oil |
| 00:00:42:08 | girl, anime |

## Files

| File | What it does |
| --- | --- |
| `textAnimations/assets/make_opening_psycho_cut.py` | opener: `eye_echoes()`, the speaker tracking (`Speaker`), `peak_glitch()` |
| `textAnimations/assets/make_bust_lines.py` | busts: `glitch()` with echoes, quadrants and lines |
| `textAnimations/assets/make_ending_girl_inserts.py` | girl: `eye_glitch()` |
| `textAnimations/plugins/cyberpsycho/cyberpsycho.py` | the lines |
| `textAnimations/assets/make_cyberpunk_closeups.py` | `aligned()`: aligning versions on the eyes |
| `textAnimations/assets/make_cyberpunk_closeup_lines.py` | thin lines in three depth layers, kept off the face |
| `textAnimations/plugins/cyberpunkEyes.jsx` | places the close-ups and the depth line layers in EffectCraft |
| `textAnimations/plugins/bustLines.jsx`, `endingCrazy.jsx`, `openingPsychoSwap.jsx` | put each scene's clip in its comp |
| `textAnimations/assets/make_eye_effect_sheet.py` | the process sheet these pictures come from |

## Assets

Everything this skill needs to run again (scripts, plugins, LUTs, seeds, sprites, data) is copied into
[`assets/`](assets/MANIFEST.md) at the same paths it has in the repo. The manifest lists what's bundled, what's shared with
another skill, and which big media (renders, projects, reference videos) stays in the repo.
