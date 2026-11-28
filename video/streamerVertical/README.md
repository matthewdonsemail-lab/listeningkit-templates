# Streamer clip → 9:16 vertical (the house style)

The style from the NickEh30 GTA 6 edit (`projects/nickeh30-gta6-v2.ecproj`, final render
`projects/renders/nickeh30-gta6-v2-final.mp4`), written down as rules, plus a builder that applies it to
any new clip with the same webcam layout and a validator that checks a project against these rules.

| File | What it does |
|---|---|
| `build.py clip.json` | Clones every style layer from the template project onto a new source clip (headless EffectCraft). |
| `resync_captions.py project.ecproj` | Re-times the caption words to the cut's own dialogue (SFX muted → render → AssemblyAI). `build.py` runs it last. |
| `validate.py project.ecproj [--render dir] [--video file.mp4]` | Checks the rules below; exit 0 = pass. |
| `clips/*.json` | One config per clip (source, transcript, eyes, kept ranges). |
| `scripts/transcribe.py` | AssemblyAI transcript: words + speakers. |
| `scripts/edl.py` | The cut plan: beats, quiet-snapped edges, J-cuts. |
| `scripts/upscale.py` | AI upscaling with Real-ESRGAN: webcam close-ups (`crop`) or used frames of the whole clip (`full`). |
| `scripts/render_chunks.py` | Full-quality render in 4 s chunks, joined, audio muxed once through a limiter. |

**How every script works, step by step, and why: [`scripts/README.md`](scripts/README.md).**
| `../findPerson/findPerson.py` | Finds the streamer's eyes (`--task pose --pick left`). |

## Pipeline

1. **Pick the clip.** r/LivestreamFail is the source; download the Twitch/LSF clip with
   `yt-dlp --no-update -c "https://livestreamfails.com/clip/<id>"`. Landscape 1280×720, webcam top-left.
2. **Transcribe** the full clip: `python scripts/transcribe.py CLIP.mp4` (AssemblyAI, words + speakers).
3. **Find his eyes** on this clip only: `findPerson.py clip.mp4 --task pose --pick left --every 1` → `summary.eyes`.
   One fixed point for the whole clip; never track per frame.
4. **Choose the kept ranges**: cut dead air between lines, but keep gameplay action that pays a line off
   (e.g. the throw and explosion after "Here, boy"). End on the line that lands the clip.
5. **Build**: `uv run --no-project --with numpy --with pillow python build.py clips/<name>.json`.
   The source transcript only places the first-pass captions; the build ends by running
   `resync_captions.py`, which re-transcribes the finished cut's dialogue (SFX muted) and rebuilds every
   caption word from it. Re-run it after ANY change to the cut.
6. **Validate**: `python validate.py projects/<name>.ecproj --render <tmpdir>`; fix until 0 failures.
7. **Render**: `python scripts/render_chunks.py PROJECT OUT.mp4 [--gain dB]`, then `validate.py ... --video OUT.mp4`.
8. **Optional AI upscale**: `"upscaleCloseups": true` in the clip config, or `scripts/upscale.py full` for the whole frame.

## The rules (what `validate.py` checks)

| # | Rule | Why |
|---|---|---|
| 1 | Comp 1080×1920 @ 30 fps | Vertical delivery. |
| 2 | No title or end cards | Captions and footage carry it. |
| 3 | Caption words are the top layers | Nothing may smear or cover them. |
| 4 | No two caption words overlap in time | Words stagger visibly otherwise. |
| 5 | Each word's `in`/`out` markers sit on its in/out points | The overshoot expression reads the markers. |
| 6 | Captions: SFC Signsmith, all caps, yellow→orange gradient fill | House type. |
| 7 | Caption text has no `' , — –` (hyphens inside words and `. ! ?` stay) | House rule. |
| 8 | No word holds over 2.5 s | Each word leaves 0.12 s after it is spoken: clear screen in silences. |
| 9 | Picture covers every frame | 1–2 frame gaps flash black. |
| 10 | Every swish pan is 0.15 s | Centred on its cut. |
| 11 | Swish pans sit above the clips, below the captions | The whip smears the picture, not the words. |
| 12 | One unsharp layer directly under the captions | Unsharp 110 / radius 5. |
| 13 | Unsharp amount > 0 | A negative amount softens (rejected). |
| 14 | Exposure ramp-out ends on the last frame | +4 on the last frame = the intro's first frame, so it loops. |
| 15 | PiP boxes: above their border, same span, motion blur on, audio off | Boxes slide in/out with blur. |
| 16 | Comp motion blur on | Needed for rule 15. |
| 17 | PiP box crops are rounded (mask path has rounded corners, never a 4-point square) | A square crop pokes past the rounded border. Never `layer.mask.shape rect` on a box; keep the template's rounded mask. |
| 18 | Captions re-timed to the cut's own dialogue (`resync_captions.py` ran) | The source clip's transcript splits repeated words differently and counts game sounds ("Boom!") as words: it drifts ~0.3 s and shows words he never says in the cut. |
| 19 | Sound effects present (at least one per swish) | Every move has a sound. |
| 20 | `--render`: one frame per second; neither the face band (28-50 %) nor the bottom half is black | Catches missing footage, incl. a split shot with no face. |
| 21 | `--video`: −16…−13 LUFS integrated | Social loudness. |
| 22 | `--video`: true peak ≤ −1 dBFS | No clipping after AAC encode. |

Base run checks rules 1–19; `--render` adds 20, `--video` adds 21–22.

## The look, element by element

**Cut.** Cut inside EffectCraft from the full source (never ffmpeg-cut or pre-cut clip files, never a
duplicate audio layer). One layer per beat carries its picture and sound. Snap edges to the quiet nearest
the word, 0.04 s out; J-cuts let the next beat's audio lead by ≤ 6 frames (3 at the cold open).

**Shot per beat** (by its words; never the same twice in a row, rotate split → face → game):
- `game` — game-world words (911, phone, police, bus, dog, fetch…): full gameplay, scale 266.67.
- `face` — `!`/`?` or emphatic words (no, wait, oh, nah, boom…): close-up at scale ~720 with one slow push,
  in (700→790) or out (790→700), alternating; eyes held at y=680 (the 33.33 % eyeline guide).
- `split` — everything else: face top (scale 300) / gameplay bottom (scale 133.33).
- Beat 0 is always the intro: a Motion Tile wall zooming from 15 % into his face in 0.5 s with an exposure
  flash and a flickering vignette.

**Captions.** Words and times come from the cut's own dialogue (rule 18). One text layer per word at `[540,300]`, size ≤ 260 fitted to the 10–90 % guides, black
stroke ≈ 21 % of size, All Fills Over All Strokes, bevel + deep glow + drop shadow, overshoot `back(2.8,1.8)`
driven by the `in`/`out` markers.

**Layer stack (top → bottom):** captions · `unsharp_110_r5` · `exposure_out_loop` · swish pans ·
split tile zooms · PiP boxes · their borders · upscaled close-ups · beats · intro precomp.

**Swish pan** per cut: 0.15 s adjustment layer — Motion Tile (mirror, 500 %) → Transform (x ±2160,
shutter 360) → horizontal Gaussian blur peaking at the cut; alternating L/R.

**Split opener** per split beat: adjustment over both halves — Motion Tile (200 % canvas is enough; 700 %
runs out of memory at full res) → Transform zoom 70 % → 165 % on his eyes by 0.3 s → expo-out back to 100 %
by 0.65 s, with an exposure flash.

**PiP boxes.** Close-ups get the same-moment gameplay in a 900 px box centred at the bottom; gameplay beats
get his face in a 440 px square bottom-left. Rounded 36 px, 12 px border in the caption gradient, the
caption's deep glow, hard drop shadow straight down at 25 %. Slide up (expo-out 0.25 s), down (expo-in 0.2 s).

**Close-up upscale.** Real-ESRGAN x4plus (ncnn-vulkan, runs on the AMD iGPU) on the webcam crop of each
close-up, laid above the beat with the same push at scale/4. For a whole-frame upscale use native ×4 then
Lanczos down (`-s 2` scrambles tiles with this model).

**Sound.** A whoosh on every swish, a zoom whoosh on every split opener, slide-up + pop + slide-down on every
box, intro flash + whoosh, a reversed-flash riser into the loop. Each hit's peak sits on its moment; levels
set by measurement (whoosh −6, slides −10, pop −12 dB under the dialogue). Final limiter so true peak ≤ −1 dB.

## Pitfalls

- Captions timed from the source clip's transcript drift and show unspoken words: always finish with `resync_captions.py`.
- `layer.mask.shape rect` replaces a rounded mask with a square: never use it on the PiP boxes.

- The GUI crashes (`0xC000041D`) under bursts of edits: edit headlessly (`effectcraft-cli run --project P --save`).
- `layer.timing` with a new out before the old in is silently ignored: set in, out, in, out (`span_steps`).
- Full-res renders of heavy comps run out of memory in one go: render 4 s chunks with `--start/--end`,
  concat, then mux the WAV once.
- The template's caption anchor is approximated as `[0.078·size, −0.39·size]`.

## Examples

| Clip | Config | Result |
|---|---|---|
| NickEh30 family-friendly train (GTA 6) | hand-built | `projects/renders/nickeh30-gta6-v2-final.mp4` |
| NickEh30 plays fetch with dogs (GTA 6), full, 41.7 s | `clips/nickeh30-dogfetch.json` | [`projects/nickeh30-dogfetch`](../../projects/nickeh30-dogfetch/README.md) (20/20 with `--render`) |
| NickEh30 plays fetch with dogs (GTA 6), first quarter | `clips/nickeh30-dogfetch-preview.json` | `projects/renders/nickeh30-dogfetch-preview.mp4` (21/21 with `--video`) |
