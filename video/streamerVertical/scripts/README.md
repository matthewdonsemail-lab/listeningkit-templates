# The scripts: what each one does and how

The pipeline, in run order. Every script is headless (no EffectCraft GUI) and prints what it did. Long ones are
resumable.

| # | Script | In → out | Time |
| --- | --- | --- | --- |
| 1 | `yt-dlp` (no script) | LSF clip URL → `CLIP.mp4` | seconds |
| 2 | [`scripts/transcribe.py`](transcribe.py) | `CLIP.mp4` → `assembly_CLIP.json` (words + speakers) | ~30 s |
| 3 | [`../../findPerson/findPerson.py`](../../findPerson/README.md) | `CLIP.mp4` → his eye point | ~2 min |
| 4 | [`scripts/edl.py`](edl.py) | transcript + audio → `edl.json` (beats, J-cuts) | seconds |
| 5 | [`build.py`](../build.py) | clip config → `.ecproj` in the full style | ~2.5 min |
| 6 | [`resync_captions.py`](../resync_captions.py) | `.ecproj` → captions re-timed to the cut (run by `build.py`) | ~40 s |
| 7 | [`validate.py`](../validate.py) | `.ecproj` (+ frames, + video) → pass/fail per rule | ~1 min |
| 8 | [`scripts/upscale.py`](upscale.py) | clip → Real-ESRGAN close-ups / full-frame 2x (optional) | 1 s-2 h |
| 9 | [`scripts/render_chunks.py`](render_chunks.py) | `.ecproj` → final `.mp4` | ~20 s per output second |

## 2. `transcribe.py`: words and who said them

AssemblyAI over plain HTTPS (stdlib `urllib`, no SDK). The key comes from `$ASSEMBLYAI_API_KEY` or
`~/.buzz/.secrets/assemblyai.key` and is never printed.

1. ffmpeg pulls the audio as 16 kHz mono WAV, which keeps the upload small.
2. `POST /v2/upload`, then `POST /v2/transcript` with `speaker_labels`, `format_text` and `punctuate`.
3. It polls every 3 s until the status is `completed`, then saves the whole response. The parts we use:
   `words[]` (`text`, `start`/`end` in ms of the source, `speaker`) and `utterances[]` (speaker turns).

This transcript only places the shots and the first-pass captions. The final captions come from step 6.

## 3. `findPerson.py`: where his eyes are

See its own README. In short: YOLO11 finds every person (including GTA characters), CLIP scores "real webcam
person" against "3D game character", and the spot that holds a person in the most frames is the facecam. We
take **one fixed eye point per clip** (`--task pose --pick left`), never a per-frame track. That point goes in
the clip config as `"eyes": [x, y]`. Every face framing puts the eyes at y = 680, just under the 33.33 % eyeline
guide.

## 4. `edl.py`: the cut plan

Follows matt's awesome-video-editing guides (`filmcraft/examples/pacing`, `jcut`, `audio`).

1. **Loudness envelope**: RMS of the source audio in 10 ms frames, in dBFS (16 kHz mono PCM, cached).
2. **Beats**: kept words split at sentence ends with a ≥ 0.10 s gap, at any gap ≥ 0.25 s, and at range
   boundaries. A beat under 1.0 s merges into the next if the gap is under 0.5 s.
3. **Edges**: each in/out snaps to the quiet instant (≥ 12 dB under that beat's median speech) nearest its
   first/last word, then 0.04 s further out. Neighbouring beats never replay source.
4. **J-cuts**: measure the outgoing line's tail (after it last comes within 6 dB of its speech level). The next
   beat starts over that tail: 3 frames at the cold open, up to 6 in the body, capped by the tail and 1/3 of the
   beat. The outgoing layer stays on top, so the picture cuts late while the next voice already leads.

For gameplay clips, keep the action around each line by hand (the `ranges` in the clip config). The plan is
speech-only and would drop the payoffs.

## 5. `build.py`: the edit

It **clones** every style layer from the finished template project (`projects/nickeh30-gta6-v2.ecproj`), so the
look can't drift from the original. It never rebuilds effects from numbers. Everything runs through
`effectcraft-cli run --project P --save`, because the GUI crashes under bursts of edits.

1. **Template layers** are found by role: a face beat (its scale expression says "Slow push"), a game beat (scale
   266.67), the split top and bottom (300 / 133.33), a caption, the L and R swishes, a split punch-in, both box kinds
   with their borders, an upscaled close-up, and each SFX kind. The SFX offsets are measured relative to their
   events on the template (e.g. the whoosh peak sits on the cut).
2. **Beats**: each kept range splits at sentence ends (≥ 1 s apart, no time removed inside a range). Shot per beat:
   - `game` if the beat has a game-world word;
   - `face` if it has `!`/`?` or an emphatic word;
   - otherwise `split`.

   Never the same shot twice in a row (rotate split → face → game). Beat 0 is always the intro.
3. **Beat layers**: duplicate the template beat, then `layer.replaceSource` to the new clip.
   - Start = comp time minus source time. In/out are set as in, out, in, out (a single out before in is
     silently clamped).
   - Face beats get one slow push, alternating in (700→790) and out (790→700). Their position expression holds
     the eye point at (540, 680).
   - Split tops keep the template's anchor method: anchor = (webcam centre x, eye y), position = (540, 680).
4. **Intro**: the template's intro precomp gets the new source and beat 0's span. Its eye-point expression is
   rewritten with the new eyes.
5. **Captions** (first pass): one duplicated caption per word.
   - The font size fits the 10-90 % guides: measured with the real SFC Signsmith font in PIL, capped at 260.
   - Stroke is about 21 % of size; the anchor is `[0.078·size, -0.39·size]`.
   - In/out markers drive the overshoot.
   - Each word leaves 0.12 s after it's spoken, or when the next word starts.
6. **Swish** per cut (0.15 s, centred on the cut, alternating L/R) and a **split punch-in** per split beat.
7. **Boxes**: face beats get the same-moment gameplay box (bottom, 900 px); game beats get the face box
   (bottom-left, 440 px). The template's rounded masks are kept untouched; never `layer.mask.shape rect`.
8. **Close-up upscale** (if `upscaleCloseups`): see step 8.
9. **SFX**: a whoosh per cut, a zoom whoosh per split, slide-up + pop + slide-down per box, each at its measured
   offset.
10. **Loop ending**: comp duration = the end of the last range. `exposure_out_loop` ramps
    `4·2^(10(u−1))` over the last 0.6 s, to +4 on the last frame, which is the intro's first value, so it loops.
    The riser ends on the last frame.
11. **Cleanup and stack**: delete every template layer that wasn't kept, then order top → bottom: captions,
    unsharp, exposure, swishes, punch-ins, boxes, borders, upscaled close-ups, beats, intro.
12. Runs `resync_captions.py`.

## 6. `resync_captions.py`: captions from the cut's own dialogue

Why: the full clip's transcript splits repeated words differently and counts game sounds ("Boom!") as words. On
the first preview that put captions up to 0.3 s off and showed words he never said in the cut.

1. Copy the project, mute every `sfx_` layer, render comp 1's audio to WAV. That's exactly what the viewer hears,
   minus the effects.
2. `log transcribe file WAV --json` (AssemblyAI).
3. One caption per spoken word, at its time in the cut:
   - it leaves 0.12 s after the word ends, at the next word, or after at most 1.2 s (ASR stretches shouts over
     game noise);
   - it stays up at least 2 frames.

   Caption layers are added or removed so the count matches. Size, stroke, anchor, timing and markers are rewritten.
4. Writes `<project>.captions.json`. The validator checks it exists.

Re-run it after ANY change to the cut.

## 7. `validate.py`: does it follow the rules

It reads the saved `.ecproj` (no GUI) and checks 20 rules (see the style README). `--render DIR` renders one frame
per second and fails if the face band (28-50 % of the height) or the bottom half is pure black. Limited-range
video: black reads 16, not 0. `--video FILE` measures the delivered loudness (−16…−13 LUFS) and true peak
(≤ −1 dBFS). Exit 0 = everything passes.

## 8. `upscale.py`: AI upscaling with Real-ESRGAN

The stream's webcam is small (about 224×312 px of a 1280×720 frame). Blown up to a 1080-wide close-up it turns to
mush. Real-ESRGAN redraws detail instead of stretching pixels.

- **Engine**: `realesrgan-ncnn-vulkan` with the `realesrgan-x4plus` model, in `%LOCALAPPDATA%/listeningkit/realesrgan/`
  ([xinntao/Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN) releases, the Windows zip). It runs on Vulkan, so
  any GPU works, including the AMD 780M iGPU here.
- **Always 4x.** `-s 2` with this model scrambles tiles (it cost a 25-minute run). For 2x, run 4x and then
  Lanczos-downscale.
- **`crop` mode** (close-ups): ffmpeg pulls the exact frames (`select=between(n,a,b)`) cropped to the webcam rect,
  upscales them 4x and encodes at CRF 14. In EffectCraft the result goes above its beat with the same push
  expression at scale/4, anchored on the eyes ×4. A 1 s close-up takes about 20 s.
- **`full` mode** (whole frames, as on the GTA edit): only the frames the cut uses are upscaled. Every other frame
  is Lanczos-scaled 2x, so the output has the same frame count and timing as the source and drops in with
  `file.replaceWithPrecomp`, no re-cut. It works in batches of 60 frames, and `done.json` makes it resumable (the GTA
  run survived a machine restart this way). About 7 s per 1280×720 frame on the 780M; the GTA clip took ~112 min for
  1,201 frames.
- **Tested**: crop 224×312 → 896×1248, 31 frames in 19 s; full 1280×720 → 2560×1440, frame count kept, 16 frames
  upscaled, no tile errors, visibly sharper than Lanczos.

## 9. `render_chunks.py`: the final render

A one-shot full-res render of the GTA comp (deep glows plus 2560×1440 footage) built up memory until it died
("memory allocation of … failed", the mp4 had no moov atom).

1. Render 4 s chunks (`--start/--end`, h264 at 16 Mbit, audio off), each in its own process: memory is freed
   between chunks, a failure is retried 3 times, and a rerun skips finished chunks.
2. Render the comp audio once as WAV. Chunked audio would click at every join.
3. Join with ffmpeg's concat demuxer (stream copy, no re-encode) and mux the WAV as AAC 256k through
   `volume=<gain>dB,alimiter=limit=0.79:level=disabled`. Peaks stay under −1 dBFS after AAC; `--gain` lifts quiet
   clips into −16…−13 LUFS.

Then `validate.py --video`.
