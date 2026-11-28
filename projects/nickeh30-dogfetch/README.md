# nickeh30-dogfetch

**"NickEh30 plays fetch with dogs in GTA 6"**: a 41.7 s 9:16 vertical cut from an 83 s
[r/LivestreamFail clip](https://livestreamfails.com/clip/tt8gdQ8EmoJW) (802 upvotes). It's the second clip in the
house style from `projects/nickeh30-gta6-v2.ecproj`, and the first one built end to end by the scripts with no hand
edits.

The whole project is generated. The source video, the `.ecproj` and the render stay local (repo `.gitignore` and
hooks), so rerun the steps below to rebuild them. Committed here: the transcript, the cut plan and the build/caption
records. The scripts live in [`video/streamerVertical`](../../video/streamerVertical/README.md), which also lists the
style rules.

## The cut

Shot per beat is picked from his words (see "Shot per beat" in the style README). Source times are seconds into the
83 s clip.

| Comp | Shot | Source | Line |
| --- | --- | --- | --- |
| 0.00 | intro → face | 15.20-19.47 | Here, boy. (intro tile zoom into his face, then the throw) |
| 4.27 | game | 19.47-23.63 | Boom! |
| 8.43 | face | 23.63-25.70 | Nah, nah, I wouldn't. |
| 10.50 | split | 25.70-27.60 | I wouldn't. I wouldn't. |
| 12.40 | face | 27.60-29.93 | No, no, no, I wouldn't. |
| 14.73 | game | 40.93-46.90 | I won't, I won't… I'm just playing |
| 20.70 | split | 50.03-51.03 | I'm just playing. |
| 21.70 | face | 51.03-52.63 | All right guys, I gotta get going. |
| 23.30 | game | 52.63-57.13 | Goodbye. Ah, they're trying to swim with me. |
| 27.80 | split | 59.93-61.93 | Here, boy. |
| 29.80 | game | 61.93-64.77 | Fudge, fudge boy. |
| 32.63 | face | 71.90-75.27 | Oh my God. |
| 36.00 | game | 75.27-80.03 | Oh my God. |
| 40.77 | face → loop | 82.20-83.13 | Oh my God. (exposure ramps out to loop) |

The kept ranges (`clips/nickeh30-dogfetch.json`) were picked by hand, not by `edl.py`. `edl.py` cuts to the speech
only, which would drop the gameplay that pays each line off: the throw and the explosion after "Here, boy", and the
dogs swimming after him. `edl.json` here is its speech-only plan, kept for reference. For a talking-head stream,
use `edl.py`'s cut as is. For gameplay, keep the action around each line.

Built: 14 beats, 65 caption words, 13 whip pans, 3 split punch-ins, 10 picture-in-picture boxes, 46 sound effects.
No AI upscale on this one (`"upscaleCloseups": false`).

## Files

| File | What it is | Made by |
| --- | --- | --- |
| `tt8gdQ8EmoJW.mp4` (local) | The source clip, 1280×720, 83 s | `yt-dlp --no-update -c "https://livestreamfails.com/clip/tt8gdQ8EmoJW"` |
| `assembly_tt8gdQ8EmoJW.json` | AssemblyAI transcript of the full clip: words (ms) + speakers | `scripts/transcribe.py` |
| `edl.json` | The speech-only cut plan with J-cut overlaps (reference) | `scripts/edl.py` |
| `nickeh30-dogfetch.ecproj` (local) | The EffectCraft project | `build.py` |
| `nickeh30-dogfetch.build.json` | Beats: kind, comp start, source in/out, words | `build.py` |
| `nickeh30-dogfetch.captions.json` | Final caption words and times, from the cut's own dialogue | `resync_captions.py` |
| `../renders/nickeh30-dogfetch.mp4` (local) | The render | `scripts/render_chunks.py` |

## Rebuilding

From `video/streamerVertical/`, in Git Bash:

```bash
P=../../projects/nickeh30-dogfetch
# 1. source + transcript (AssemblyAI key: $ASSEMBLYAI_API_KEY or ~/.buzz/.secrets/assemblyai.key)
(cd $P && yt-dlp --no-update -c -o "tt8gdQ8EmoJW.%(ext)s" "https://livestreamfails.com/clip/tt8gdQ8EmoJW")
python scripts/transcribe.py $P/tt8gdQ8EmoJW.mp4
# 2. his eye point on this clip only (gave 153,246; it goes in the clip config as "eyes")
uv run --no-project --with ultralytics --with lap --with transformers \
  python ../findPerson/findPerson.py $P/tt8gdQ8EmoJW.mp4 --task pose --pick left --every 1
# 3. build (about 2.5 min, headless), then check every rule
uv run --no-project --with numpy --with pillow python build.py clips/nickeh30-dogfetch.json
python validate.py $P/nickeh30-dogfetch.ecproj --render "$TMPDIR/frames"
# 4. render in 4 s chunks, join, mux the audio once with the limiter (about 17 min), check loudness (+4 dB gave −14.6 LUFS)
python scripts/render_chunks.py $P/nickeh30-dogfetch.ecproj ../../projects/renders/nickeh30-dogfetch.mp4 --gain 4
python validate.py $P/nickeh30-dogfetch.ecproj --video ../../projects/renders/nickeh30-dogfetch.mp4
```

Close the project in EffectCraft before building; the build writes the `.ecproj` headlessly.

## What went wrong on the way (now caught by the validator)

- **Split shots with a black top half.** The template positions the split's face by its anchor (webcam centre, eye
  height) at (540, 680). The builder had put a full-frame-centre position on top of that anchor, which pushed his
  face off-screen. Fixed in `build.py`. `validate.py --render` now checks the face band (28-50 % of the height) and
  the bottom half separately, because the caption kept the whole-frame average above black. Pure black reads 16 in
  limited-range video, not 0.
- **"BOOM!" on screen for 6 s.** AssemblyAI stretched the shout over the game noise. `resync_captions.py` now caps
  every word at 1.2 s.
