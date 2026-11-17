# numpy fx extraction

> **First time?** This project's image generation and hosting run through [treg](https://treg.to/?ref=matthewdonse-aebsh). Sign up with
> [this link](https://treg.to/?ref=matthewdonse-aebsh), install the CLI (`curl -fsSL https://treg.to/install.sh | sh`), run `treg login`,
> then check it with `treg balance`.


## What it is

A way to reuse the look of a reference edit without copying the reference. The video is broken into numbered frame
sheets so matt can point at the frames he likes. The picked frames are then read with OpenCV and the effect (glitch
colour, smears, noise, bright lines) is pulled out with HSV colour and brightness masks. Everything else becomes
transparent. The result is a set of transparent layers (RGBA PNG and ProRes 4444) that go over our own shots in
EffectCraft as normal, editable layers.

## Where it came from

- **TikTok 1** (`projects/opening/ref/tt_elements/tiktok_7705499377023995169.mp4`), an Edgerunners-style glitch edit.
- **The Cyberpunk trailers and fan edits** in `projects/opening/ref/cyberpunk_edits/<youtube id>/video.mp4`: the
  Edgerunners 2 trailer (`urV5GzXcXsQ`), Edgerunners 2 Teaser #2 (`QBlPg818lGI`) and the fan edits and
  opening-titles tutorial listed in `textAnimations/assets/make_ref_boards.py`.

![TikTok 1, every frame numbered](images/01_tiktok_elements_sheet.jpg)
*Step 1: TikTok 1 as a numbered sheet (54 frames, one every 0.25 s). matt named effects by number from this: 02-03 the
RGB glitch blocks, 16 the eye noise, 29 the pink pixel blocks, 39 the blue eye close-up.*

## How it works

### 1. Break the edit down (`break_down_edits.py`)

Every frame is read at 320x180. Cuts are found where the frame difference jumps (above 28 and above 2.2x the local
median). The script writes `cuts.txt`, contact sheets with each thumbnail labelled by its source frame, and
`stats.json` with each shot's colours, saturation, brightness and edge density. Short edits (70 s or less) are
sampled at 6 fps. For trailers the sheet shows each cut frame plus the frame on either side.

![Edgerunners 2 trailer contact sheet](images/02_trailer_contact_sheet.jpg)
*Step 1: `cyberpunk_edits/urV5GzXcXsQ/sheet_00.jpg`, the Edgerunners 2 trailer around its cuts, with source frame
numbers in the corners.*

### 2. Boards to say yes or no to (`make_ref_boards.py`)

Frame numbers read off the sheets go into the script's `BOARDS` list. Each technique gets a 2x2 board of its four
clearest frames. matt's verdicts are in `boards/VERDICTS.md`.

![Board: red line tagline](images/03_board_red_line_tagline.jpg)
*Step 2: board 18, "red line tagline", from the Edgerunners 2 trailer frames 1046-1129. Its red lines became the
seeds of the `seed-path-generators` skill.*

### 3. Pull the effect out (`extract_fx.py`)

The picked frames for each effect go into a folder (`f_01.png`, `f_02.png`, ...). Each frame is split four ways:

- **chroma**: the saturated glitch colour. Alpha comes from HSV saturation (0.45-0.8) times value (0.3-0.6).
- **streaks**: horizontal smears and pixel-sort runs. These are strong vertical edges with almost no horizontal
  change, spread along the rows.
- **noise**: the fine noise, scanlines and tearing. This is the frame minus its 5 px median blur.
- **lines**: thin bright strokes. This is a 15 px white top-hat of the brightness.
- **fx**: all four together.

Each layer keeps the frame's own colour and changes only the alpha. It is saved as an RGBA PNG sequence and as a
ProRes 4444 `.mov` with alpha.

![TikTok effects split into layers](images/04_tiktok_fx_layers.jpg)
*Step 3: the four TikTok effects (rows) split into source, chroma, streaks, noise, lines and fx on transparency
(`tt_elements/assets/fx/layers_sheet.jpg`).*

![Trailer effects lifted onto transparent](images/05_trailer_fx_layers.jpg)
*Step 3: trailer effects (rgb bar flash, light streak wipe, tracking tear, Sandevistan echo, datamosh bars, logo
streaks), each shown as source and extracted (`cyberpunk_edits/boards/00_extracted_fx_layers.jpg`).*

### 4. Into EffectCraft

`make_cut_fx.py` writes `plugins/launchCutFx.jsx`. That script puts one extracted effect on every cut of `launch film`
as its own layer, from 2 frames before the cut to 2 frames after, at Screen and 55% opacity. It rotates through four
effects: RGB glitch chroma, pixel blocks chroma, eye-noise streaks and eye close-up lines. A pixel-sort burst and an
exposure ramp are added with it. All of these are layers that can still be moved or turned off.

## The result in the film

![A cut in the final film](images/06_film_cut_fx.jpg)
*The cut at frame 48 (00:00:01:18) of `textAnimations/renders/launch_film_final_full.mp4`, frames 46-49: the
extracted glitch and the pixel sort over the car-window shot on either side of the cut, under the VHS/CRT look.*

The layers go on all 24 cuts listed in `launchCutFx.jsx`: frames 23, 48, 64, 82, 109, 128, 153, 181, 215, 253, 281,
308, 450, 510, 711, 826, 922, 956, 989, 1022, 1056, 1090, 1123 and 1749 at 30 fps.

## Files

| File | Role |
|---|---|
| `textAnimations/assets/break_down_edits.py` | cuts, contact sheets, shot stats per reference video |
| `textAnimations/assets/make_ref_boards.py` | one 2x2 board per technique for matt's yes/no |
| `textAnimations/assets/extract_fx.py` | chroma / streaks / noise / lines / fx layers, PNG + ProRes 4444 |
| `textAnimations/assets/make_cut_fx.py` | writes `plugins/launchCutFx.jsx` (effects + pixel sort per cut) |
| `textAnimations/plugins/launchCutFx.jsx` | places the layers in `launch film` |
| `projects/opening/ref/tt_elements/` | TikTok 1, its frames, `elements_sheet.jpg`, `assets/fx/` layers |
| `projects/opening/ref/cyberpunk_edits/` | trailers and edits, sheets, `boards/`, `fx_src/` |
| `textAnimations/assets/make_process_board.py` | the process board, whose note sums up the method |

## Assets

Everything this skill needs to run again (scripts, plugins, LUTs, seeds, sprites, data) is copied into
[`assets/`](assets/MANIFEST.md) at the same paths it has in the repo. The manifest lists what's bundled, what's shared with
another skill, and which big media (renders, projects, reference videos) stays in the repo.
