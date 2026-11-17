# Shot camera realism

> **First time?** This project's image generation and hosting run through [treg](https://treg.to/?ref=matthewdonse-aebsh).
> Sign up with [this link](https://treg.to/?ref=matthewdonse-aebsh), install the CLI
> (`curl -fsSL https://treg.to/install.sh | sh`), run `treg login`, then check it with `treg balance`.

## What it is

The launch film's opener is made of AI stills. On their own they play like a slideshow. This is the camera work that
makes them read as shots filmed on a real camera: a handheld shake and wobble measured from a real film, slow
push-ins and pull-outs on every shot, a rack focus on two of them, and one shot pushing in and morphing into the next.
It's all expressions and named effects on the layers in EffectCraft, so every number can still be changed. The same
idea, a camera that anticipates, overshoots and springs back, drives the 3D journey through the platform cards in
Intro 1.

## The reference: The Big Short's first minute

![The Big Short, reference frames](images/01_bigshort_reference_frames.jpg)
*The Big Short's opening, the frames kept in `projects/opening/ref/` (`bigshort_01`-`bigshort_12`, `bigshort_key`).
Spreadsheets and Christian Bale's face, all handheld, with slow push-ins and sudden crash zooms on the numbers.*

19 shots from its first minute were measured into `projects/opening/ref/bigshort_camera.json`: for each shot, the
drift, the amount and frequency of the shake, the push-in rate and the rotation wobble. Across them the medians are
8.7 px of shake at 1.65 Hz, a 0.78 %/s push and 0.23 degrees of wobble. Two profiles came out of it:

| | Shake | Wobble | Push |
|---|---|---|---|
| Faces (handheld) | about 6 px at ~1.7 Hz | ~0.2 degrees | a slow 1.2 %/s |
| Screens (crash push-in) | heavier, 14 px at 2.2 Hz | 0.6 degrees | 25 %/s, with a 70 px/s drift |

## How it works

### 1. The cut comes from FilmCraft

matt cuts the opener in FilmCraft. `sync_opening_from_filmcraft.py` reads his sequence and writes every clip with its
timing and framing to `assets/opening_edit.json`. `make_opening_comp.py` turns that into an EffectCraft script that
builds one precomp per shot inside the `opening` comp. Nothing is rendered in between.

### 2. Handheld on every face and screen

`openingHandheld.jsx` puts expressions on each shot's layer. The shake is three sine waves per axis at rates that
never line up, seeded differently per shot, so it never loops and no two shots shake the same. Faces get the gentle
handheld and a slow push. Screens get the crash push-in with a drift, softened so the chat message stays in frame.

### 3. A camera move inside each shot

`openingCamera.jsx` adds a move to the picture inside the shot's precomp: a push in (or a pull out) towards a chosen
point, eased over the shot, with its own small handheld shake and wobble. On sama3 and the shot through the blinds,
a lens blur starts soft and racks into focus, then breathes a little.

![The opener's shots with the camera on them](images/02_opening_camera_stills.jpg)
*The stills matt was shown before the camera went in (`textAnimations/assets/collage/opening_camera_stills.jpg`,
frame numbers in pink): the aerial, the morph into the car window (19-21), the faces, the screens.*

![Push-ins in the finished film](images/04_push_ins_in_the_film.jpg)
*In the finished film (`renders/launch_film_final_full.mp4`, frame and timecode on each): Sam's close-up, the chat
screen pushing in under "MAGICAL.", the push to sama3's eyes under "PROMISED", the push through the blinds under
"TIME". The VHS look and glitch cuts on top come from other scripts.*

### 4. The aerial morphs into the car window

The opener starts on San Francisco from the air, 00:00:00:00 to 00:00:00:23, pushing slowly in. Instead of cutting to
the car window, the car window comes in 6 frames early and both pictures go through a turbulent warp: the city tears
apart while the street fades in through it, and the street settles 3 frames after the cut.

![The morph, frame by frame](images/03_morph_aerial_to_car_window.jpg)
*Frames 14-29 of the film: the aerial (14-16), the warp as the car window comes through (17-25), the car window
settling (26-29).*

### 5. The journey camera (Intro 1)

In Intro 1's platform journey (`logPlayJourney`, 12.77-20.77 s of Intro 1) a 3D camera travels past seven platform
cards at different depths. `journeyCamera.jsx` changes its path so it drifts back before each move, runs past the
card, pulls out further mid-move, zooms in past the card on arrival and springs back, and pushes in a little just
before leaving. It also added a neon grid floor and ceiling for parallax, which a later script swapped for a particle
circuit wall. There's no rendered frame of this version of the journey in the repo.

## The result in the film

`textAnimations/renders/launch_film_final_full.mp4` (opener 0-10 s; the film's timecodes and the opener's are the
same). The spans below are read off the render's frames, so they're approximate at the edges:

| Timecode | What the camera does |
|---|---|
| 00:00:00:00-00:00:00:23 | the aerial pushes in on the city |
| 00:00:00:17-00:00:00:28 | the aerial morphs into the car window |
| 00:00:00:29-00:00:01:24 | the car window, handheld push in |
| 00:00:01:26-00:00:02:10 | Sam's close-up, push in and handheld |
| 00:00:02:12-00:00:04:00 | the chat screen, crash push-in |
| 00:00:04:16-00:00:04:28 | sama3, push to his eyes |
| 00:00:06:08-00:00:06:26 | through the blinds, push in |

## Files

| File | What it does |
|---|---|
| `projects/opening/ref/bigshort_camera.json` | The Big Short's first minute, measured per shot |
| `projects/opening/ref/bigshort_cuts60.txt` | its cut times |
| `textAnimations/assets/sync_opening_from_filmcraft.py` | matt's FilmCraft cut to `assets/opening_edit.json` |
| `textAnimations/assets/make_opening_comp.py` | writes `plugins/openingDawn.jsx`, which builds the shot precomps and `opening` |
| `textAnimations/plugins/openingHandheld.jsx` | handheld and push on the faces, crash push-ins on the screens |
| `textAnimations/plugins/openingCamera.jsx` | per-shot push/pull, handheld, rack focus, and the aerial-to-car-window morph |
| `textAnimations/plugins/journeyCamera.jsx` | the journey camera's anticipation, overshoot and spring, and the grid |
| `textAnimations/connectionPlays.mjs` | builds `logPlayJourney` and its base camera |
| `textAnimations/OPENING.md`, `textAnimations/PLAY_JOURNEY.md` | the opener's and the journey's notes |
| `textAnimations/launchFilm_final.ecproj` | the saved project with all of it in |

## Assets

Everything this skill needs to run again (scripts, plugins, LUTs, seeds, sprites, data) is copied into
[`assets/`](assets/MANIFEST.md) at the same paths it has in the repo. The manifest lists what's bundled, what's shared with
another skill, and which big media (renders, projects, reference videos) stays in the repo.
