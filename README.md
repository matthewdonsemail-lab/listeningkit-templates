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
| `cloudBackground` | 3D clay clouds drifting in depth layers, clay-dithered white and light blue, over the ditherGradientBackground sky. |
| `ditherGradientBackground` | Brand blue breaking into light blue, then white, in big square pixels. |

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
- **Craft plug-ins:** both backgrounds use the "Craft Halftone & Dither" effect plug-in (by qwertyonek).
  Without it they show the plain gradients, with no dither.

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

To change a template or add one, edit `typewriterVariations.mjs` and run both commands again.

## Credits

- Schoolbell font by Font Diner, from Google Fonts, under the Apache License 2.0.
- Satoshi font by the Indian Type Foundry, from [Fontshare](https://www.fontshare.com/fonts/satoshi), under the ITF Free Font License.

## License

MIT for everything else in this repository. See [LICENSE](LICENSE).
