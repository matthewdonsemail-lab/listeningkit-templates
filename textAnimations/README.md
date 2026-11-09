# Text Animations

ListeningKit text effects for EffectCraft, all set in Schoolbell (`fonts/Schoolbell-Regular.ttf`) with the
cv-bluekey look (see cvBluekey below): brand blue, white then navy outline, -3° tilt, blue glow.

- `textAnimations.ecproj` — one 1920×1080, 30 fps, 4 s comp per effect.
- `effects/<name>/effect.json` — the EffectCraft CLI commands that build that effect.
- `effects/<name>/<name>.ectemplate` — the effect as a template, with its Essential Graphics controls.

## Typewriter overshoot variations

Two scales run together, both 0 to full size with overshoot, and no fades:

- **The whole text** scales from its centre over the full marker duration.
- **Each letter (or word)** pops in one after another from its own centre, inside that.

On the way out both swell slightly, then scale back to 0.

**Markers on the `text` layer set the timing:**

- `in` marker — where the type-on starts. Its duration is how long until the last unit has landed.
- `out` marker — where the type-off starts. Its duration is how long until the last unit is gone.
  Delete it to keep the text on screen.

Drag a marker to move that half. Stretch it to make that half slower or faster.

**Slider controls on the layer (also in Essential Graphics):**

- `Letter Overshoot` — how far past full size each letter (or word) goes. 0 = none.
- `Pop Time` — seconds for one letter (or word) to scale in or out.
- `Whole Overshoot` — how far past full size the whole text goes. 0 = none.

- `Continuous Scale` — % the whole text keeps growing per second from the `in` marker on. 0 = none,
  negative shrinks. Default 6.

Position is the centre of the text.

| Effect | Unit | In | Out | Pop Time | Letter Overshoot | Whole Overshoot | Extra |
| --- | --- | --- | --- | --- | --- | --- | --- |
| typewriterOvershoot | letter | 0.6 s | 0.5 s | 0.25 s | 2 | 1.7 | — |
| typewriterOvershootFast | letter | 0.35 s | 0.3 s | 0.16 s | 2.6 | 2 | — |
| typewriterOvershootWords | word | 0.4 s | 0.35 s | 0.28 s | 2 | 1.7 | — |
| typewriterOvershootRotate | letter | 0.6 s | 0.5 s | 0.28 s | 2 | 1.7 | swings in from -20° |

`continuousScale` is typewriterOvershoot with the same default Continuous Scale, kept as its own effect.

`typewriter` is the plain hard-cut version. fadeUpCharacters is the other effect. These two
also have a `Continuous Scale` slider (default 6), growing from the start of the comp around the text's centre.

## cvBluekey

Every effect uses this look; cvBluekey adds its motion. The ListeningKit sticker look, from log-cli's `.lk-bluekey` and the word stickers in the looksmaxxing
project: Schoolbell in brand blue `#2a8cff`, a white outline inside a dark navy `#0d2a4c` outline
(text stroke + Stroke layer style), tilted -3°, with a blue Outer Glow.

It pops in from the `in` marker like the looksmaxxing words (0 → 126% → 94% → 100% over 4 frames),
pops out in reverse from the `out` marker, and wobbles and bobs while on screen.

Sliders: `Continuous Scale` (% per second, default 6), `Wobble` (degrees, default 2), `Bob` (pixels, default 6).

## introCard

A title card precomp (1920×1080, 5 s):

- **background** — the cloudBackground precomp (below).

- **Introducing** — Satoshi Bold (the ListeningKit site font), navy, the overshoot typewriter. Its own
  `in` / `out` markers and Letter Overshoot, Pop Time, Whole Overshoot and Continuous Scale sliders.
- **listening kit** — below it, cv-bluekey look with the overshoot typewriter (same four sliders as
  Introducing), on top of the lines above and below it.
- **Subtext** — "no dashboards, no SaaS, / just your accounts and your agent." from the site, on two lines, one text layer
  per word (`word 01`–`word 12`). Each word scales in from its centre with overshoot, one after another.
  "no dashboards" and "no SaaS" are highlighted as on the site (Satoshi Black, brand blue, dashed
  underline that draws on with the words); "your agent." is a small cv-bluekey sticker.

The subtext is driven by the `controls` null: its `in` marker (start, and how long until the last word
lands), `out` marker, and Overshoot, Pop Time, Word Spacing and Continuous Scale sliders. Continuous Scale grows
the whole subtext block from its centre: the words spread apart and scale up together, underlines included. The words lay themselves out
from their own widths, each line centred on its own, so editing a word's text (in Essential Graphics or on its layer) reflows the line
and moves the underlines with it.

## cloudBackground

3D clay clouds drifting over the ditherGradientBackground sky, rebuilt from log-cli's landing page hero
(`site/apps/web/src/landing/ClayClouds.tsx`). The site uses Claybound's `cloud.glb`, which isn't licensed to
ListeningKit, so each cloud here is our own: six 3D spheres under a null.

- `clayClouds` — an Advanced 3D comp with a 30° camera, ambient, warm key (casting shadows) and blue fill lights,
  and 30 clouds in 4 depth layers (12 far and small down to 3 near and big), as on the site. Each cloud drifts
  right at its layer's speed and wraps around, bobs and turns slowly (expressions on its null). Far clouds are
  tinted toward the sky to stand in for the site's fog. Positions come from a fixed seed.
- `cloudBackground` — `sky` (the ditherGradientBackground precomp), then `clayClouds` through the site's clay
  dither: Black & White, Levels (black 0.3, white 0.92), Craft Halftone & Dither (3 px cells), Tint (shade
  light blue, lit white).

Essential Graphics: Cloud Dither Size, Cloud Shade, Cloud Lit.
build.sh builds ditherGradientBackground, then cloudBackground, then the rest, because introCard uses cloudBackground.

## ditherGradientBackground

Brand blue breaking into light blue, then into white, in big square pixels (ordered dither), wiping up the frame
from fully blue to fully white. Two bands, each a black-to-white Gradient Ramp through Craft Halftone & Dither
(18 px cells) and Tint: `upper` goes blue to light blue over 378 px, `lower` light blue to white over the next
491 px.

**Wipe** is a slider on the `controls` null that moves both bands together: 0 is fully blue (the fade sits below
the frame), 100 is fully white (the fade has gone off the top). It's keyframed 0 → 100 over the 5 s comp with easy
ease, so the fade comes up slowly, speeds up, and lands on white at the end. Move the keyframes to retime it, or
remove them and set one value for a still gradient (about 45 gives the original look).

Essential Graphics: Wipe, Top Color, Middle Color, Bottom Color, Pixel Size. The lower band follows the upper
band's Middle Color and Pixel Size by expression. cloudBackground and introCard use this precomp, so they wipe too.

## Building

- `node typewriterVariations.mjs` writes every generated effect's `effect.json` (overshoot variations, presets, cvBluekey). Edit the
  table at its top to add or change one.
- `bash build.sh` rebuilds the project, names the slider controls and re-applies their expressions (`nameControls.jsx`), and writes the
  templates. Close the project in EffectCraft first.
