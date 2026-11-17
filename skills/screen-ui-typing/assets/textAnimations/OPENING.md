# The launch opener

The comp `opening` (0–15 s, 450 frames at 30 fps), played by `launch film` into `cyberpunk` with the VO and music.
Since 2026-11-15 it is matt's FilmCraft cut, rebuilt clip for clip in EffectCraft; nothing is rendered in between.

## The cut

matt edits in FilmCraft: `C:/Users/0/filmcraft/projects/launchIntro/launchIntro-v1.fcproj`, sequence `intro`.
Video 1 is the stills; Video 2 is the cyberpsycho shout (`assets/collage/opening_psycho_v5.mp4`) from 8.43 s.
The beat drops at 00:00:10:08 (frame 308): the cyberpsycho starts there.

To bring a new FilmCraft cut across (save it in FilmCraft, close EffectCraft), from `textAnimations/`:

```bash
python assets/sync_opening_from_filmcraft.py      # the clips, timestamps and Motion -> assets/opening_edit.json
python assets/make_opening_comp.py                # -> plugins/openingDawn.jsx
"$CLI" --project textAnimations.ecproj script plugins/openingDawn.jsx --save
"$CLI" --project textAnimations.ecproj script plugins/openingInserts.jsx --save
"$CLI" --project textAnimations.ecproj script plugins/CRTemulator/applyOpening.jsx --save
"$CLI" --project textAnimations.ecproj script plugins/openingThermal.jsx --save
```

To swap just the cyberpsycho clip for a new render, set `CLIP` in `plugins/openingPsychoSwap.jsx` and run it.

After the drop the clip (`--after speakers`, the default) is young Sam for 4 beats, young Dario for 4 beats (their
clips in `projects/opening/ref/speakers/`, a punch-in on every beat, their own red cyberpsycho steps from
`images/gen/make_opening_psycho_speakers.py` breaking through at each peak), then the inside scene. The three
switches are thermogram transitions (`plugins/openingThermal.jsx`, as cyberpunk's match cut).

`openingDawn.jsx` rebuilds `opening` from scratch, so always run `openingInserts.jsx` and `applyOpening.jsx` after
it, in that order.

## Inserts

`plugins/openingInserts.jsx`: three 4-frame cutaways from `projects/opening/ref/styleref.mp4`, under the VHS look:
a mouse click (styleref 52.09 s) at frame 78 (2.60 s, before the cut to the chat at 2.73 s), a finger pressing a key
(26.40 s) at frame 107 (3.58 s, before the cut at 3.63 s), the mouse click again at frame 238 (7.95 s, on "Can I
trust you?"). The reference is 640x268, so it is scaled 403% to fill the height and looks soft. Only the picture is
synced: `launch film` plays the whole VO and music from 0, as the FilmCraft sequence does.

## The look

`plugins/CRTemulator/applyOpening.jsx`:

- 0 to 10:08: a washed-out VHS look after the tragedy_rx edit (`projects/opening/ref/tragedy_rx`): lifted blacks, dull
  whites, less colour, a warm tint, a sideways blur sharpened back with Unsharp Mask so the edges ring, red and blue
  bleeding sideways, a little Wave Warp wobble, grain; and black bars down the sides (a 4:3 picture).
- 10:08 to the end: the CRT-Emulator build (style 10), as on `cyberpunk`, every CRT layer trimmed to start on the drop.

## The cyberpsycho shout

Two shots, the man behind the blinds and the man at the chalkboard, shouting at each other on the beat.

| Script | Makes |
| --- | --- |
| `images/gen/make_opening_psycho.py` | `projects/opening/psycho/<shot>/<shot>_00-11.png`: 12 steps of each going cyberpsycho, into the red sun_ae look (`projects/opening/ref/sun_ae`), camera locked |
| `assets/make_opening_psycho_matte.py` | `projects/opening/psycho/<shot>_matte.png`: each man off his background (GrabCut) |
| `assets/make_opening_psycho_cut.py` | `assets/collage/opening_psycho.mp4`; `--frames 9,40 ` writes just those frames as PNGs instead |

The cut: before the drop the real shots in the original edit, their real eyes now and then echoing outwards; from the
drop a hard cut between the two on every half-beat (every quarter-beat in the last 40%), the real shot as the base
with the cyberpsycho face coming through in rectangles over his eyes, brows, nose, mouth and cheeks (large into small,
crazier each cut), his eyes echoing outwards from the variations, the cyberpsycho lines out of his eyes, other
backgrounds glitch-cut behind him. Every still is aligned on the eyes so a rectangle cut from one lands in place.

## Next frames

`images/gen/make_opening_next.py`: each opener still a few seconds on (`projects/opening/next/<shot>_next.png`, at the
still's own size), for image-to-video as first and last frame.

treg's hosting quota is a rolling 300 MB a day; the generators host small JPEG references to stay inside it.
