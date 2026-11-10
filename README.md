# listeningkit-templates

ListeningKit's motion templates for [EffectCraft](https://artcraft.ai): text animations, title cards and
backgrounds in the ListeningKit look. Every template is built from EffectCraft layers, effects and
expressions, so each one is editable in Essential Graphics. None of them is a baked image.

## What's in it

Everything lives in [`textAnimations/`](textAnimations). Open `textAnimations/textAnimations.ecproj` in
EffectCraft to see every comp, or import a single `.ectemplate` from `textAnimations/effects/<name>/`.

| Template | What it does |
| --- | --- |
| `typewriterOvershoot` | Types on letter by letter. Each letter and the whole line scale from 0 with overshoot, then out again. |
| `typewriterOvershootFast` | The same, quicker, with a bigger overshoot. |
| `typewriterOvershootWords` | The same, word by word. |
| `typewriterOvershootRotate` | The same, each letter also swinging in from -20°. |
| `continuousScale` | The overshoot typewriter with the text growing steadily while it's on screen. |
| `typewriter` | The plain hard-cut typewriter. |
| `fadeUpCharacters` | Letters fade up into place. |
| `cvBluekey` | The ListeningKit sticker: pops in over 4 frames, wobbles and bobs. |
| `introCard` | A title card: "Introducing", "listening kit" and a word-by-word subtext with highlighted, dash-underlined words. |
| `claudeCode` | The Claude Code window from the landing page, playing a prompt, a log tool call and the reply. |
| `codex` | The Codex window from the landing page, playing the same session. |
| `terminal` | The Claude Code CLI window: welcome box, then a typed prompt, a log tool call, its result and the reply. |
| `cloudBackground` | 3D clay clouds drifting in depth layers, clay-dithered white and light blue, over the ditherGradientBackground sky. |
| `ascii3D` | One 3D clay cloud drawn in ASCII characters, on the ditherGradientBackground sky held mostly blue with the dither just creeping in at the bottom. |
| `tiktok` | Three columns of portrait TikToks scrolling up at different speeds, behind the TikTok chrome: tabs, logo, action rail, handle, caption and music. |
| `brickTextBackground` | A wall of blue word bricks built from your sentence: Build pops them in until they fill the frame, Scramble swaps the words. |
| `ditherGradientBackground` | Brand blue breaking into light blue, then white, in big square pixels, wiping from fully blue to fully white on a Wipe slider. |

Every text template uses the cv-bluekey look: Schoolbell in brand blue `#2a8cff`, a white outline inside a navy
`#0d2a4c` outline, a -3° tilt and a blue glow.

### Controls

- **Markers:** the text layers have `in` and `out` markers. A marker's position is when that half starts, and
  its length is how long it takes. Drag a marker to retime, stretch it to speed up or slow down, delete
  `out` to keep the text on screen.
- **Sliders** (on the layer and in Essential Graphics): Letter Overshoot, Pop Time, Whole Overshoot and
  Continuous Scale, plus Wobble and Bob on cvBluekey and Word Spacing on the intro card's subtext.

[`textAnimations/README.md`](textAnimations/README.md) has every template's settings in detail.

## Requirements

- **EffectCraft**, with its command-line tool `effectcraft-cli` for rebuilding.
- **Fonts:** Schoolbell and Satoshi are included in `textAnimations/fonts`. Install both before opening the project.
- **Craft plug-ins:** the backgrounds use the "Craft Halftone & Dither" effect plug-in (by qwertyonek).
  Without it they show the plain gradients, with no dither.

## How it works

Nothing here is drawn by hand. Every template is generated from code, then built by EffectCraft's own command-line
tool, so the whole project can be rebuilt from scratch and every change is reviewable in git.

```
typewriterVariations.mjs ──► effects/<name>/effect.json ──► build.sh ──► textAnimations.ecproj
   (the templates, in JS)      (EffectCraft CLI commands)     (effectcraft-cli)   + effects/<name>/<name>.ectemplate
```

1. **`typewriterVariations.mjs`** describes every template. It writes each one as a list of EffectCraft CLI commands
   (new comp, new layer, set a property, add an expression, add a marker, add an Essential Graphics control…) to
   `effects/<name>/effect.json`. Random-looking layouts (clouds, bricks) use a fixed seed, so every build is the same.
2. **`build.sh`** runs those commands with `effectcraft-cli`:
   - builds the precomps other templates use first (`ditherGradientBackground` → `cloudBackground` → `introCard`),
     then everything else, into one `textAnimations.ecproj`;
   - runs `nameControls.jsx`, which names the slider controls (the expressions read them by name, e.g.
     `effect("Pop Time")`) and re-applies the expressions so they pick the names up;
   - closes every comp tab and leaves the light `typewriterOvershoot` open, so the project opens fast;
   - sorts the Project panel into folders with `organize.json` (Text Animations, Title Cards, Backgrounds, Agent
     Windows, Assets);
   - exports each comp as `effects/<name>/<name>.ectemplate`, with its Essential Graphics controls.
3. **The templates are driven by expressions**, not keyframes, wherever they need to react to their controls: `in` /
   `out` markers set timing, sliders set overshoot, speed, spacing and colours, and text layers read their words
   from Essential Graphics. Change a control and the animation follows.

House rules the generator follows:

- **Keep comps light.** No per-frame layout chains (a layer re-measuring other layers' text every frame), no
  full-frame plug-in effects on busy comps, and keep layer counts low. `effects/brickTextBackground/NOTES.md` is
  the case study of a version that broke this and was removed.
- **Build from layers, not images.** Backgrounds and windows are shapes, text, solids and effects; the only files
  imported are the brand marks in `textAnimations/assets/`, plus the nine TikTok clips the `tiktok` wall uses (those
  are referenced from the rea-looksmaxxing project, not copied in).
- **ASCII command files.** `effectcraft-cli` reads command files in the Windows code page, so the generator writes
  every non-ASCII character (✻, ·, “ ”…) as a `\u` escape.

## Rebuilding

Each template is a list of EffectCraft CLI commands in `textAnimations/effects/<name>/effect.json`, so the
whole project can be rebuilt from scratch:

```bash
cd textAnimations
node typewriterVariations.mjs   # writes every effect.json
bash build.sh                   # builds textAnimations.ecproj and exports each .ectemplate
```

`build.sh` runs in Git Bash on Windows. It uses `cygpath` and looks for the CLI at
`C:\Program Files\ArtCraft\EffectCraft\effectcraft-cli.exe`. Set `EFFECTCRAFT_CLI` to use another path.
Close the project in EffectCraft before rebuilding.

To change a template or add one, edit `typewriterVariations.mjs` and run both commands again. A new template also
needs its comp added to `organize.json`, and its slider names to `nameControls.jsx` if it has sliders.

## Credits

- Schoolbell font by Font Diner, from Google Fonts, under the Apache License 2.0.
- Satoshi font by the Indian Type Foundry, from [Fontshare](https://www.fontshare.com/fonts/satoshi), under the ITF Free Font License.

## License

MIT for everything else in this repository. See [LICENSE](LICENSE).
