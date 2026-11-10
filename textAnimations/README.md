# Text Animations

ListeningKit text effects for EffectCraft, all set in Schoolbell (`fonts/Schoolbell-Regular.ttf`) with the
cv-bluekey look (see cvBluekey below): brand blue, white then navy outline, -3° tilt, blue glow.

- `textAnimations.ecproj` — one comp per template, sorted into folders in the Project panel: Text Animations,
  Title Cards, Backgrounds (with clayClouds and cloudSolo in Parts), Agent Windows and Assets (`organize.json`).
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
  The clouds also slide in and out, set on the `controls` null: from its `in` marker every cloud slides in from off
  the left with overshoot (the marker's length is how long until the last one lands), and from its `out` marker
  each winds up and slides back out to the left. Sliders: Overshoot, Stagger (the most seconds one cloud starts
  after another).
- `cloudBackground` — `sky` (the ditherGradientBackground precomp), then `clayClouds` through the site's clay
  dither: Black & White, Levels (black 0.3, white 0.92), Craft Halftone & Dither (3 px cells), Tint (shade
  light blue, lit white).

Essential Graphics: Cloud Dither Size, Cloud Shade, Cloud Lit.
build.sh builds ditherGradientBackground, then cloudBackground, then the rest, because introCard uses cloudBackground.

## ascii3D

One clay cloud drawn in ASCII characters, on the ditherGradientBackground sky held mostly blue with the dither just
creeping in at the bottom of the frame (1920×1080, 5 s).

- **cloudSolo** — the one cloud, in its own Advanced 3D comp: the same 30° camera, ambient, warm key and blue fill
  lights as `clayClouds`, and one cloud built from our six spheres under a null. It drifts slowly either side, bobs
  and turns, and slides in from off the left from its `in` marker with overshoot (Overshoot slider). Add an `out`
  marker to have it wind back out.
- **The ASCII** is built from layers, because there is no ASCII effect to apply: three full-frame grids of JetBrains
  Mono characters, from the ramp `` . , ' ` : - = + * # % @ ``, one grid per brightness band. The lit tops of the cloud
  get the dense glyphs, the body the mid ones, the shadows the sparse ones, and each grid is revealed only where the
  cloud is that bright.
- **The mattes** are three copies of `cloudSolo`, not rendered: a Levels stretches the cloud's shading to 0–1, a
  second Levels clips that to the band, and each is the luma track matte of its grid. EffectCraft renders the 3D
  scene for each one, so the comp costs roughly three cloud renders a frame.
- **The sky** is the `ditherGradientBackground` precomp, time-remapped to `0.55 + time * 0.21` so its 0 → 100 Wipe
  only reaches a little way up from the bottom instead of wiping the frame to white. Change that expression for more
  or less of the fade.

Essential Graphics: **Density** (0 is the built-in band split, positive draws more of the cloud so the ASCII is
denser, negative leaves only the brightest parts drawn), **Ink** (the glyphs on the lit parts of the cloud) and
**Shade** (the glyphs in its shadows — the three bands are drawn in Ink, Ink at 78% and Shade, so the shading reads as
form instead of one flat white silhouette).

The grids are laid out for a monospace font: JetBrains Mono advances 0.6 em, so the glyph size sets the columns and
the rows sit 0.9 of it apart. The size (20 px), the characters and their random pick are fixed in the generator, so
changing them means editing `typewriterVariations.mjs` and rebuilding.

## tiktok

A wall of TikToks behind the TikTok chrome (1920×1080, 8 s).

- **Three columns** of portrait clips, each column 640 wide, scrolling up at different speeds (42, 96 and 158 px/s
  at Speed 100) so the wall drifts against itself. Each column holds its three clips twice over and wraps every three,
  so it scrolls forever without a seam.
- **The chrome**: the TikTok logo, the Following / For You tabs, the action rail (avatar, ♥ 416K, ● 1,049, ➤ 19.4K),
  and the handle, caption and music line bottom left, over a soft black fade.
- Essential Graphics: **Speed** (all three columns together), **Handle**, **Caption**.

The clips are the ones from the rea-looksmaxxing project — `log-hyperframes/effectcraft/tiktok/tt01…tt09.mp4` — imported
from there, so this template needs that folder on disk (the project keeps them as online media, referenced by absolute
path). The TikTok mark is `assets/plat_tiktok.png`.

## ditherGradientBackground

Brand blue breaking into light blue, then into white, in big square pixels (ordered dither), wiping up the frame
from fully blue to fully white. Two bands, each a black-to-white Gradient Ramp through Craft Halftone & Dither
(18 px cells) and Tint: `upper` goes blue to light blue over 378 px, `lower` light blue to white over the next
491 px.

**Wipe** is a slider on the `controls` null that moves both bands together: 0 is fully blue (the fade sits below
the frame), 100 is fully white (the fade has gone off the top). It's keyframed 0 → 100 over the 5 s comp with easy
ease, so the fade comes up slowly, speeds up, and lands on white at the end. Move the keyframes to retime it, or
remove them and set one value for a still gradient (about 45 gives the original look).

The dither leaves a dot in every tile even in pure white, so a `clear` layer in Bottom Color covers everything past
the end of the fade; at Wipe 100 the frame is clean white.

Essential Graphics: Wipe, Top Color, Middle Color, Bottom Color, Pixel Size. The lower band follows the upper
band's Middle Color and Pixel Size by expression. cloudBackground and introCard use this precomp, so they wipe too.

## brickTextBackground

A wall of blue rounded bricks filling the frame (8 rows of same-size bricks in a running bond), each holding one word
picked at random from a sentence.

- **Sentence** — the `sentence` guide layer (not rendered). Type any sentence; every brick picks its words from it.
- **Build** (0–100, on `controls`) — the bricks pop in one by one in a fixed random order with overshoot; at 100 the
  wall fills the whole comp. Keyframed 0 → 100 over the first 2.5 s. **Overshoot** sets the pop.
- **Scramble** (checkbox, off by default) — every brick swaps to another random word every **Scramble Every** seconds.
- **Brick Color** — the bricks' colour. Words are Satoshi Bold in white and shrink to fit their brick.

All of these are in Essential Graphics. `effects/brickTextBackground/NOTES.md` explains a heavier version that was
removed, and why it was too heavy.

## claudeCode, codex, terminal

The agent windows from log-cli's landing page, rebuilt as reusable precomps (1920×1080, transparent background,
window centred, 6 s), from plain shapes and text so they stay light:

- **claudeCode** — the cream Claude window (`site/apps/web/src/landing/AgentSession.tsx`): sidebar with Claude,
  New session, Chats, Code and Recents; the your-marketing / main bar; a prompt bubble, a `log · twitterDms` tool
  card with its result, the reply in serif; the "Reply to Claude…" box with Opus 5.5 and the orange send button.
- **codex** — the white Codex window from the same file: New thread, the your-marketing recents, the thread title
  and branch, the prompt pill, "Called log.twitterDms" with its result box, the reply, and "Ask Codex anything".
- **terminal** — the Claude Code CLI window from the rea-looksmaxxing project (`log-hyperframes/effectcraft/scene2`):
  near-black with a title bar, traffic lights and "matt — claude — ~/log", the orange-bordered "Welcome to Claude
  Code" box, then the session in JetBrains Mono: the prompt typed after `>`, an orange ● log tool line, a grey └
  result and a blue ● reply. The window pops in.

The Claude and Codex marks are the real ones from log-cli's `BrandMark.tsx`, saved as `assets/claude.svg` and
`assets/codex.svg`.

They play the start of the site's session: the prompt is typed into the input box at the bottom (the hint hides while
it's there), then sent at 1.74 s: the box clears and the prompt pops in as a bubble at the top. The tool call pops in
at 2.24 s and the reply types on word by word from 3.04 s. The terminal pops in and types its lines one after another.
Essential Graphics: Prompt, Tool, Reply (and Result on the terminal).

## Building

- `node typewriterVariations.mjs` writes every generated effect's `effect.json` (overshoot variations, presets, cvBluekey). Edit the
  table at its top to add or change one.
- `bash build.sh` rebuilds the project, sorts it into folders (`organize.json`; add a new template's comp there), names the slider controls and re-applies their expressions (`nameControls.jsx`), and writes the
  templates. Close the project in EffectCraft first.
