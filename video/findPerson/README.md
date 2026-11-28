# findPerson

Point it at a video clip and get the exact pixel box of where the person is, frame by frame, as JSON.

For streamer clips it finds **the streamer** (the facecam), not the people in the gameplay behind them, even when the game is photoreal (GTA 6).

## Run

No install: `uv` fetches the dependencies, and the models download once to `%LOCALAPPDATA%/listeningkit/models` (YOLO) and the Hugging Face cache (CLIP).

```bash
uv run --no-project --with ultralytics --with lap --with transformers \
  python video/findPerson/findPerson.py CLIP.mp4 --aspect 9:16 --preview
```

Writes `CLIP.person.json` next to the clip. With `--preview` it also writes `CLIP.person.png`, a contact sheet you can check by eye:

- **green**: the chosen person
- **red**: the head box (`--task pose`)
- **cyan**: the suggested crop
- **grey**: everyone else the detector saw

The run's last stdout line is a one-line JSON summary.

## How it decides who "the person" is

1. **Detect**: Ultralytics YOLO11, the same models and `person` class filter as [AdamCodd/Yolo-twitch](https://github.com/AdamCodd/Yolo-twitch), run headless on the file with ByteTrack ids. It finds every human shape, including game characters.
2. **Real or game**: CLIP (`openai/clip-vit-base-patch32`) scores each detection crop as "a real person on a webcam" vs "a 3D video game character".
3. **Where they sit** (`--pick real`, the default): detections are grouped by position. The facecam is the spot that holds a person in the most frames, weighted by the CLIP score. Game characters move around the frame; the webcam does not. This is what separates NickEh30 from photoreal GTA 6 passengers, which CLIP alone rates as real.
4. **Held frames**: a frame where the detector missed the streamer takes the box from the nearest frame that found them, marked `"held": true`.

Other picks: `steady` (the tracked person in the most frames, then the one that moves least), `largest`, and `left` / `right` / `top` / `bottom` (the well-seen person nearest that edge). Use these for clips with no facecam.

## Options

| Option | Default | Meaning |
|---|---|---|
| `--every S` | `0.5` | sample one frame every S seconds (`0` = every frame) |
| `--task` | `detect` | `detect` (box), `segment` (+ `maskBox`, tight to the silhouette), `pose` (+ `headBox` from face keypoints) |
| `--size` | `nano` | YOLO11 size: `nano` `small` `medium` `large` `xlarge` |
| `--pick` | `real` | which person: `real` `steady` `largest` `left` `right` `top` `bottom` |
| `--real T` | `0.5` | minimum CLIP real-person score for `--pick real` |
| `--conf T` | `0.35` | minimum detector score |
| `--aspect W:H` | none | also suggest a crop of that aspect around the person (e.g. `9:16`) |
| `--all` | off | also list every person per sampled frame, with track id and CLIP score |
| `--out PATH` | `<clip>.person.json` | output path |
| `--preview` | off | write the contact sheet |
| `--clip ID` | `openai/clip-vit-base-patch32` | Hugging Face CLIP model |

The tool uses CUDA if there is one, otherwise the CPU. An 8 s clip at 0.5 s sampling takes under a minute on the CPU after the first run, which downloads the models.

## Output

All boxes are `[x, y, w, h]` in source pixels, origin top-left. `boxNorm` is the same box divided by the frame size.

```jsonc
{
  "video": "C:/…/clip.mp4", "size": [1280, 720], "fps": 30, "frames": 242, "duration": 8.067,
  "summary": {
    "pick": "real", "sampled": 17, "found": 17, "held": 4, "coverage": 1.0, "real": 0.951,
    "medianBox": [0, 155, 271, 542],      // where the person usually is
    "unionBox":  [0, 153, 352, 560],      // everywhere they went
    "centre": [136, 426], "centreNorm": [0.1059, 0.5917],
    "crop": [0, 0, 405, 720], "cropAspect": "9:16"   // with --aspect
  },
  "samples": [
    { "frame": 0, "time": 0.0, "found": true, "box": [0, 155, 270, 540], "boxNorm": [...],
      "score": 0.87, "real": 0.95, "crop": [...] },
    { "frame": 15, "time": 0.5, "found": true, "held": true, "box": [...] }
  ],
  "allTracks": [ { "id": 3, "samples": 12, "medianBox": [...] } ]
}
```

To place a clip in an EffectCraft comp so the person sits at a target point, use `summary.centre` (or the per-frame `box` centres for a moving crop) together with the layer's scale.

## Tested on

`B3PfPBKrfAAR_00_A_0.0-8.1.mp4` (NickEh30, GTA 6 train). The facecam (`[0,155,271,542]`) is found in all 17 samples: 13 detected, 4 held. CLIP alone picked GTA passengers on this clip; grouping by position fixes it.
