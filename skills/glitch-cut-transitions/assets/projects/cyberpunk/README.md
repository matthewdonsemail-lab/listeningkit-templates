# cyberpunk

A 16.7 s pre-comp, `cyberpunk`, nested at the end of `Intro 1` (from 62.13 s). A girl walks into a crowded hall, the
camera pushes into her face, a thermogram match cut drops into a glitch collage of her face in many styles, and the
outro pushes into the girl in the Nous logo, turns her round through a dozen styles, and ends on blue chiaroscuro
caricatures. Everything is built by scripts; the media they make stays local (see the repo `.gitignore`), so rerun
them to rebuild it.

## The cut

| Time | Shot | Built by |
| --- | --- | --- |
| 0 - 2.0 s | The walk-in: the hall empty, she appears, the crowd flows round her | `assets/make_cyberpunk_flow.py` |
| 2.0 s | One thermogram flash, a match cut onto her face | `plugins/cyberpunkEyes.jsx` |
| 2.0 - 5.2 s | The close-up collage, thin depth lines, the HERMES-AGENT wordmark at 3.6 s | `assets/make_cyberpunk_closeups.py`, `assets/make_cyberpunk_closeup_lines.py` |
| 5.2 - 16.7 s | The outro: the `cyberpunk outro` pre-comp, built from layers | `assets/make_cyberpunk_outro_comp.py` |

Paths are relative to `textAnimations/` unless they start `images/` or `projects/`.

## Rebuilding

Close the project in EffectCraft first. Then, in Git Bash from `textAnimations/`, with
`CLI="/c/Program Files/ArtCraft/EffectCraft/effectcraft-cli.exe"`:

```bash
python assets/make_cyberpunk_matte.py          # her cut-out, projects/cyberpunk/girl.png
python assets/make_cyberpunk_flow.py           # the walk-in + the cyberpsycho line layer behind her
python assets/make_cyberpunk_closeups.py       # the close-up collage
python assets/make_cyberpunk_closeup_lines.py  # the three depth layers of thin lines
python assets/make_cyberpunk_outro_comp.py     # the outro pre-comps' build script + its lines video
"$CLI" --project textAnimations.ecproj script plugins/cyberpunkOutro.jsx --save
"$CLI" --project textAnimations.ecproj script plugins/cyberpunkEyes.jsx --save
"$CLI" --project textAnimations.ecproj script plugins/CRTemulator/applyCyberpunk.jsx --save
"$CLI" --project textAnimations.ecproj render --comp cyberpunk --out ../renders/cyberpunk.mp4 --format h264 --quality best
```

Always run `cyberpunkEyes.jsx` before `applyCyberpunk.jsx`: rebuilding the comp clears the CRT. `cyberpunkEyes.jsx`
re-reads every generated clip from disk (`replace`), so a regenerated clip comes in at its new length; before that
fix EffectCraft kept the old length and froze on the last frame. When an outro changes length, set `OUTRO` in
`cyberpunkEyes.jsx` to its frame count / 30 (the outro script prints it).

The outro is a tree of pre-comps in the Project panel folder `cyberpunk outro parts`: `outro flash`, `outro logo`,
`outro push` and `outro back` (one pre-comp per step, the cut-up pieces as masked stills), `outro end` (plain
keyframes) and `outro portraits`, nested in `cyberpunk outro`. Every build rebuilds the comps in place, so the comps
nesting them stay connected. To change one pre-comp, rebuild just that one (about 20 s; it replaces that comp's
layers, so hand edits in it are lost, and nothing else is touched):

```bash
python assets/make_cyberpunk_outro_comp.py --only "outro end"   # or "outro push 03", "outro portraits"...
"$CLI" --project textAnimations.ecproj script plugins/cyberpunkOutro.jsx --save
```

Use Python 3.12 (`C:/Python312/python.exe`): it has numpy, OpenCV and Pillow.

## Generating stills

All stills come from treg's Nano Banana Pro (`reapi.image-gen.gemini-3-pro-image`, about $0.03 each), with
reference images hosted by `treg host`. Each script skips a still that already exists, so delete one to redo it.

| Script (in `images/gen/`) | Makes |
| --- | --- |
| `make_cyberpunk_opening.py` | `open_a-g.png`: the locked-off hall, her spot empty (a), her standing (b), the crowd moved on round her (c-g) |
| `make_cyberpunk_opening_styles.py` | `styles/open_<k>_<anime\|being>.png`: each moment redrawn in the anime and light-being styles |
| `make_cyberpunk_eyes.py` | `eyes1-3.png`: the close-ups, from the overhead angle |
| `make_cyberpunk_variants.py` | `variants/eyes2/<style>.png`: the photo close-up in five Intro 1 styles |
| `make_cyberpunk_zoomstyles.py` | `outro/front_00-11.png`, `outro/back_00-11.png`: the outro push redrawn per frame |
| `make_cyberpunk_turn.py` | `outro/portrait_0-5.png`: the caricature headshots |
| `make_caricature_ensemble.py` | `outro/ensemble.png`: the caricatures in the Headband Portraits composition |

What worked when prompting:

- **Match cuts need a composition reference.** Pass the exact frame you are cutting from as the first image and say
  "keep the composition exactly". For the outro push, the 12 zoom frames were extracted from the rendered outro
  (`outro/zoomref/`) and each was redrawn from its own frame.
- **Name the reference's job.** "The FIRST image is the composition", "the crowd reference" and so on. A style
  reference passed fourth was ignored until it went first.
- **Say "one single image, not a grid".** One photo came back as a contact sheet of eight.
- **The result can be a JPEG.** The download pattern has to accept `.jpg` as well as `.png`.
- **Flat backgrounds need a clean-up.** The model drifts into texture; `images/gen/flatten_stamp_bg.py` keeps the
  black, white and grey (figures and dither) and makes everything else flat brand blue.

## Techniques

### Glitch collage (cutting in rectangles)

Every style of a shot is first aligned to one framing (`aligned()` in `make_cyberpunk_closeups.py`: scale and crop so
the point between her eyes sits at frame centre, eyes the same distance apart). Then anything cut from one style lands
in place on another. Every 2 frames new pieces are added to a stack that keeps the newest 12-14, so the collage builds
instead of resetting: large rectangle strips, and her features (eyes, brows, nose, mouth) blown up 1.3-2x. Every other
4-frame cut is her full face, clean, so she stays readable.

In the outro push every frame is at a different zoom, so `into(j, i)` re-frames style `j` to frame `i`'s zoom before
cutting from it. The pieces are positioned in the logo's own coordinates and ride the push; the large rectangles can
land anywhere in the frame, so the whole scene is cut up, not just her face.

### Cut-out and slow shutter (the walk-in)

- **Her matte** (`make_cyberpunk_matte.py`): the difference between her shot and the same shot with her spot empty,
  refined with OpenCV GrabCut. Around her feet only the near-black shoes and trousers are kept, so her shadow doesn't
  come with her.
- **Painting her out** of every background frame with the empty plate, under a widened, softened matte, so the
  cut-out is the only her.
- **The slow shutter**: each background frame is blended with the ones before (`acc*0.58 + new*0.42`), so people drag
  into ghost trails; zoom streaks are copies scaled out from her centre and averaged.
- **Her entrance**: an exposure blow-out (3 frames up, 6 down) and a pixel sort of her shape that resolves over 10
  frames; every 6 frames one or two quadrants of her body (never her face) cut to another style for 2 frames.

### cyberpsycho lines

`plugins/cyberpsycho/cyberpsycho.py`, measured from the red lines in `references/cyberpsycho/` (isolated by colour):
thin jittery strokes about 7 px wide that swell into tapering blades, stepped right angles, drips and ticks, 9-38 pieces
covering 2.5-5% of the frame, redrawn on twos. `frame()` draws one; a matte makes them start inside the subject and
shoot outward; `thin=True` with an `avoid` oval keeps them off a face; `glitch()` pixel-sorts them into streaks, slips
bands sideways, splits red and blue and drops blocks out. Near-white with a thin dark edge, under the CRT, they read as
the CRT's own highlights; pure blue on top of the CRT looked like a sticker.

### Depth of field

The thin close-up lines come in three layers, each its own ProRes 4444 with alpha: far (fine, soft, pushes 4%), mid
(sharp, 14%), near (big, blurred, 38%). Different push rates give parallax as the camera moves in.

### CRT and thermogram

`plugins/CRTemulator/applyCyberpunk.jsx` runs the CRT-Emulator plug-in's own build (style 10) the way
`applyIntro1.jsx` does, with Posterize Time switched off. The thermogram is the orange/green LUT flash inside an
exposure blow-out from `thermalCuts.jsx`, used once, on the match cut into her face.
