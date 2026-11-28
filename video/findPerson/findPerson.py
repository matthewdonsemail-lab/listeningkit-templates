"""Find where the person is in a video clip, in exact pixels.

Built on the same stack as AdamCodd/Yolo-twitch (https://github.com/AdamCodd/Yolo-twitch):
Ultralytics YOLO11 models (`yolo11{n,s,m,l,x}{,-seg,-pose}.pt`) with the COCO class filter set
to `person`, fed by OpenCV/ffmpeg. Yolo-twitch draws boxes on a live Twitch stream in a window;
this runs the same detection headless on a file (or stream URL) and writes the numbers:

- every sampled frame's box `[x, y, w, h]` in source pixels (and normalised 0-1),
- Ultralytics ByteTrack ids, so the same person keeps one id across the clip,
- `--task segment`: the silhouette box (tight to the mask, not the detector rectangle),
- `--task pose`: a head box from the face keypoints (nose, eyes, ears),
- `--pick real` (default): the streamer, not the people in the gameplay. Every detection is
  grouped by where it sits; the facecam is the spot that holds a person in the most frames
  (game characters move, the webcam does not), weighted by CLIP (Hugging Face
  `openai/clip-vit-base-patch32`) rating it a real human rather than a video-game character,
- the clip summary: median box, union box, centre, coverage, and an optional crop of a given
  aspect (e.g. 9:16) that keeps the person in frame.

Run (no install; uv fetches the deps, the model downloads once):

    uv run --no-project --with ultralytics --with lap --with transformers python findPerson.py CLIP.mp4
    uv run --no-project --with ultralytics --with lap --with transformers python findPerson.py CLIP.mp4 --task pose --aspect 9:16 --preview

See README.md for the output format and options.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import cv2
import numpy as np

SIZES = {"nano": "n", "small": "s", "medium": "m", "large": "l", "xlarge": "x"}  # as Yolo-twitch
TASKS = {"detect": "", "segment": "-seg", "pose": "-pose"}
PERSON = 0  # COCO class id ("person" in Yolo-twitch's COCO_CLASSES)
HEAD_KPTS = [0, 1, 2, 3, 4]  # COCO pose: nose, left/right eye, left/right ear


def model_file(size: str, task: str) -> str:
    """`yolo11<size><task>.pt` in a per-user cache; Ultralytics downloads it there on first use."""
    cache = Path(os.environ.get("LOCALAPPDATA") or Path.home() / ".cache") / "listeningkit" / "models"
    cache.mkdir(parents=True, exist_ok=True)
    return str(cache / f"yolo11{SIZES[size]}{TASKS[task]}.pt")


def device() -> str:
    """CUDA when there is one (Yolo-twitch assumes it); otherwise CPU, so it runs anywhere."""
    try:
        import torch

        return "cuda:0" if torch.cuda.is_available() else "cpu"
    except Exception:
        return "cpu"


def xywh(x0: float, y0: float, x1: float, y1: float) -> list[float]:
    return [x0, y0, x1 - x0, y1 - y0]


def rounded(b: list[float]) -> list[int]:
    return [round(float(v)) for v in b]


def norm(b: list[float], w: int, h: int) -> list[float]:
    return [round(b[0] / w, 4), round(b[1] / h, 4), round(b[2] / w, 4), round(b[3] / h, 4)]


def crop_for(aspect: float, box: list[float], w: int, h: int) -> list[int]:
    """Largest crop of `aspect` (w/h) inside the frame, centred on `box`, clamped to the frame."""
    cw, ch = (h * aspect, float(h)) if h * aspect <= w else (float(w), w / aspect)
    cx, cy = box[0] + box[2] / 2, box[1] + box[3] / 2
    x = min(max(cx - cw / 2, 0.0), w - cw)
    y = min(max(cy - ch / 2, 0.0), h - ch)
    return [round(x), round(y), round(cw), round(ch)]


def people(r, task: str) -> list[dict]:
    """Every person in one Ultralytics result: track id, score, box, plus mask/head boxes."""
    out = []
    b = r.boxes
    if b is None or len(b) == 0:
        return out
    ids = b.id.int().tolist() if b.id is not None else [None] * len(b)
    for k, (xyxy, conf, tid) in enumerate(zip(b.xyxy.tolist(), b.conf.tolist(), ids)):
        p: dict = {"track": tid, "score": float(conf), "box": xywh(*xyxy)}
        if task == "segment" and r.masks is not None and k < len(r.masks.xy):
            poly = r.masks.xy[k]
            if len(poly):
                p["maskBox"] = xywh(float(poly[:, 0].min()), float(poly[:, 1].min()), float(poly[:, 0].max()), float(poly[:, 1].max()))
        if task == "pose" and r.keypoints is not None and k < len(r.keypoints.xy):
            kp = r.keypoints.xy[k].tolist()
            kc = r.keypoints.conf[k].tolist() if r.keypoints.conf is not None else [1.0] * len(kp)
            eyes = [kp[i] for i in (1, 2) if kc[i] > 0.5 and kp[i][0] > 0]
            if eyes:
                # Eyeline: the mean of the visible eye keypoints (COCO 1 = left eye, 2 = right eye).
                p["eyes"] = [sum(q[0] for q in eyes) / len(eyes), sum(q[1] for q in eyes) / len(eyes)]
            head = [kp[i] for i in HEAD_KPTS if kc[i] > 0.5 and kp[i][0] > 0]
            if len(head) >= 2:
                xs, ys = [q[0] for q in head], [q[1] for q in head]
                # Face keypoints span eyes-to-ears; pad to cover the whole head.
                span = max(max(xs) - min(xs), max(ys) - min(ys), 1.0)
                cx, cy = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2
                p["headBox"] = xywh(cx - span * 0.9, cy - span * 1.2, cx + span * 0.9, cy + span * 1.0)
        out.append(p)
    return out


REAL = ["a webcam photo of a real human person", "a real person streaming on a facecam", "a photo of a real man sitting at a desk"]
FAKE = ["a 3D video game character", "a CGI character in a video game", "a rendered game avatar"]


def realness(crops: list[np.ndarray], clip_id: str) -> list[float]:
    """P(real person) for each crop: CLIP zero-shot, real-human prompts vs video-game-character
    prompts. YOLO finds every human shape; this tells the live streamer (webcam) apart from game
    characters, which COCO `person` cannot."""
    if not crops:
        return []
    import torch
    from transformers import CLIPModel, CLIPProcessor

    model = CLIPModel.from_pretrained(clip_id)
    proc = CLIPProcessor.from_pretrained(clip_id)
    out: list[float] = []
    for i in range(0, len(crops), 32):
        rgb = [cv2.cvtColor(c, cv2.COLOR_BGR2RGB) for c in crops[i : i + 32]]
        inp = proc(text=REAL + FAKE, images=rgb, return_tensors="pt", padding=True)
        with torch.no_grad():
            pr = model(**inp).logits_per_image.softmax(-1)
        out += [round(float(v), 3) for v in pr[:, : len(REAL)].sum(-1)]
    return out


def pick_real(samples: list[tuple[int, list[dict]]], thr: float, w: int, h: int) -> dict[int, dict]:
    """Per sampled frame, the detection that is the streamer. Every detection is grouped by where
    it sits (centre within 6% of the width / 8% of the height); the streamer's facecam is the spot
    that holds a person in the most frames, weighted by how real CLIP rates it. Game characters,
    even photoreal ones, move around the frame; the webcam does not. Each frame then keeps the
    detection nearest that spot, if it is within the radius and scores at least `thr` real."""
    rx, ry = 0.06 * w, 0.08 * h
    groups: list[dict] = []
    for k, (_, ps) in enumerate(samples):
        for p in ps:
            cx, cy = p["box"][0] + p["box"][2] / 2, p["box"][1] + p["box"][3] / 2
            g = next((g for g in groups if abs(g["cx"] - cx) < rx and abs(g["cy"] - cy) < ry), None)
            if g is None:
                g = {"cx": cx, "cy": cy, "n": 0, "frames": set(), "real": []}
                groups.append(g)
            g["n"] += 1
            g["cx"] += (cx - g["cx"]) / g["n"]
            g["cy"] += (cy - g["cy"]) / g["n"]
            g["frames"].add(k)
            g["real"].append(p.get("real", 1.0))
    if not groups:
        return {}
    top = max(groups, key=lambda g: len(g["frames"]) * float(np.mean(g["real"])))
    out = {}
    for k, (_, ps) in enumerate(samples):
        near = [p for p in ps if abs(p["box"][0] + p["box"][2] / 2 - top["cx"]) < rx and abs(p["box"][1] + p["box"][3] / 2 - top["cy"]) < ry]
        near = [p for p in near if p.get("real", 1.0) >= thr]
        if near:
            out[k] = min(near, key=lambda p: (p["box"][0] + p["box"][2] / 2 - top["cx"]) ** 2 + (p["box"][1] + p["box"][3] / 2 - top["cy"]) ** 2)
    return out


def choose(tracks: dict[int, list[tuple[int, dict]]], how: str, w: int, h: int) -> int | None:
    """The track that is "the person" (the non-`real` picks). `steady`: present in the most samples, then the
    one that moves least (a facecam holds still while game characters move). `largest`: biggest
    median box. `left`/`right`/`top`/`bottom`: nearest that edge among the well-seen tracks."""
    if not tracks:
        return None

    def med(t: int) -> list[float]:
        return np.median(np.array([p["box"] for _, p in tracks[t]]), 0).tolist()

    def motion(t: int) -> float:
        c = np.array([[p["box"][0] + p["box"][2] / 2, p["box"][1] + p["box"][3] / 2] for _, p in tracks[t]])
        return float((c.std(0) / [w, h]).sum())

    most = max(len(v) for v in tracks.values())
    good = [t for t in tracks if len(tracks[t]) >= max(1, most // 2)]
    if how == "largest":
        return max(tracks, key=lambda t: med(t)[2] * med(t)[3])
    if how in ("left", "right", "top", "bottom"):
        cx = lambda t: med(t)[0] + med(t)[2] / 2  # noqa: E731
        cy = lambda t: med(t)[1] + med(t)[3] / 2  # noqa: E731
        key = {"left": lambda t: -cx(t), "right": cx, "top": lambda t: -cy(t), "bottom": cy}[how]
        return max(good, key=key)
    return max(tracks, key=lambda t: (len(tracks[t]), -round(motion(t), 3)))


def main() -> int:
    ap = argparse.ArgumentParser(description="Find the person in a video clip with YOLO11: exact pixel boxes per frame + summary JSON.")
    ap.add_argument("video", help="video file or stream URL")
    ap.add_argument("--task", default="detect", choices=list(TASKS), help="detect (box), segment (+ silhouette box), pose (+ head box)")
    ap.add_argument("--size", default="nano", choices=list(SIZES), help="YOLO11 model size (default nano)")
    ap.add_argument("--every", type=float, default=0.5, help="sample one frame every N seconds (default 0.5; 0 = every frame)")
    ap.add_argument("--conf", type=float, default=0.35, help="minimum person score (default 0.35)")
    ap.add_argument("--pick", default="real", choices=["real", "steady", "largest", "left", "right", "top", "bottom"], help="which person is 'the person'")
    ap.add_argument("--aspect", default=None, help="also suggest a crop of this aspect, e.g. 9:16 or 1:1")
    ap.add_argument("--real", type=float, default=0.5, help="minimum CLIP real-person score for --pick real (default 0.5)")
    ap.add_argument("--clip", default="openai/clip-vit-base-patch32", help="Hugging Face CLIP model for the real-vs-game check")
    ap.add_argument("--all", action="store_true", help="also list every person found per sampled frame")
    ap.add_argument("--out", default=None, help="JSON path (default: <video>.person.json next to the clip)")
    ap.add_argument("--preview", action="store_true", help="also write <video>.person.png: a contact sheet with the boxes drawn")
    a = ap.parse_args()

    from ultralytics import YOLO

    cap = cv2.VideoCapture(a.video)
    if not cap.isOpened():
        print(f"cannot open {a.video}", file=sys.stderr)
        return 2
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    w, h = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    step = max(1, round(a.every * fps)) if a.every > 0 else 1
    aspect = None
    if a.aspect:
        x, y = a.aspect.split(":")
        aspect = float(x) / float(y)

    model = YOLO(model_file(a.size, a.task), task=a.task)
    dev = device()
    samples: list[tuple[int, list[dict]]] = []
    thumbs: list[tuple[int, np.ndarray]] = []
    stream = model.track(
        source=a.video, stream=True, persist=True, tracker="bytetrack.yaml", classes=[PERSON], conf=a.conf, vid_stride=step, device=dev, verbose=False
    )
    crops: list[np.ndarray] = []
    owners: list[dict] = []
    for k, r in enumerate(stream):
        ps = people(r, a.task)
        samples.append((k * step, ps))
        if a.pick == "real":
            for p in ps:
                x, y, bw, bh = rounded(p["box"])
                c = r.orig_img[max(0, y) : y + bh, max(0, x) : x + bw]
                if c.size and bw >= 16 and bh >= 16:
                    crops.append(c.copy())
                    owners.append(p)
        if a.preview and len(thumbs) < 64:
            thumbs.append((k, r.orig_img.copy()))

    tracks: dict[int, list[tuple[int, dict]]] = {}
    for k, (_, ps) in enumerate(samples):
        for p in ps:
            if p["track"] is not None:
                tracks.setdefault(p["track"], []).append((k, p))
    for p, sc in zip(owners, realness(crops, a.clip)):
        p["real"] = sc
    if a.pick == "real":
        hits = pick_real(samples, a.real, w, h)
        main_t = None
    else:
        main_t = choose(tracks, a.pick, w, h)
        hits = {k: p for k, p in tracks.get(main_t, [])} if main_t is not None else {}

    frames = []
    for k, (fi, ps) in enumerate(samples):
        p = hits.get(k)
        rec: dict = {"frame": fi, "time": round(fi / fps, 3), "found": p is not None}
        if p:
            rec["box"] = rounded(p["box"])
            rec["boxNorm"] = norm(p["box"], w, h)
            rec["score"] = round(p["score"], 3)
            if "real" in p:
                rec["real"] = p["real"]
            for extra in ("maskBox", "headBox", "eyes"):
                if extra in p:
                    rec[extra] = rounded(p[extra])
            if aspect:
                rec["crop"] = crop_for(aspect, p.get("headBox") or p["box"], w, h)
        if a.all:
            rec["people"] = [{"track": q["track"], "box": rounded(q["box"]), "score": round(q["score"], 3), "real": q.get("real")} for q in ps]
        frames.append(rec)

    # The streamer's webcam does not move: a frame where the detector missed them takes the box of
    # the nearest frame that found them, marked `held` (only for --pick real).
    if a.pick == "real" and any(f["found"] for f in frames):
        got = [k for k, f in enumerate(frames) if f["found"]]
        for k, f in enumerate(frames):
            if not f["found"]:
                src = frames[min(got, key=lambda j: abs(j - k))]
                f.update({key: src[key] for key in ("box", "boxNorm", "crop", "headBox", "maskBox", "eyes") if key in src})
                f["found"], f["held"] = True, True
    found = [f for f in frames if f["found"]]
    summary: dict = {
        "pick": a.pick,
        "track": main_t,
        "tracks": len(tracks),
        "sampled": len(frames),
        "found": len(found),
        "coverage": round(len(found) / max(1, len(frames)), 3),
        "held": sum(1 for f in frames if f.get("held")),
        "real": round(float(np.median([f["real"] for f in frames if f.get("real") is not None])), 3) if any(f.get("real") is not None for f in frames) else None,
    }
    if found:
        arr = np.array([f["box"] for f in found], dtype=float)
        med = np.median(arr, 0).tolist()
        x0, y0 = arr[:, 0].min(), arr[:, 1].min()
        x1, y1 = (arr[:, 0] + arr[:, 2]).max(), (arr[:, 1] + arr[:, 3]).max()
        summary.update(
            medianBox=rounded(med),
            unionBox=rounded([x0, y0, x1 - x0, y1 - y0]),
            centre=[round(med[0] + med[2] / 2), round(med[1] + med[3] / 2)],
            centreNorm=[round((med[0] + med[2] / 2) / w, 4), round((med[1] + med[3] / 2) / h, 4)],
        )
        heads = [f["headBox"] for f in found if "headBox" in f]
        if heads:
            summary["medianHeadBox"] = rounded(np.median(np.array(heads, dtype=float), 0).tolist())
        eyes = [f["eyes"] for f in found if "eyes" in f and not f.get("held")]
        if eyes:
            summary["eyes"] = rounded(np.median(np.array(eyes, dtype=float), 0).tolist())
        masks = [f["maskBox"] for f in found if "maskBox" in f]
        if masks:
            summary["medianMaskBox"] = rounded(np.median(np.array(masks, dtype=float), 0).tolist())
        if aspect:
            summary["crop"] = crop_for(aspect, summary.get("medianHeadBox") or med, w, h)
            summary["cropAspect"] = a.aspect

    report = {
        "video": str(Path(a.video).resolve()).replace("\\", "/") if Path(a.video).exists() else a.video,
        "size": [w, h],
        "fps": round(fps, 3),
        "frames": n,
        "duration": round(n / fps, 3),
        "every": a.every,
        "model": f"YOLO11 {a.size} {a.task} (Ultralytics, COCO person, ByteTrack), device {dev}",
        "boxFormat": "[x, y, w, h] in source pixels, origin top-left",
        "summary": summary,
        "samples": frames,
        "allTracks": [
            {"id": t, "samples": len(v), "real": round(float(np.median([p.get("real", 0) for _, p in v])), 3) if a.pick == "real" else None, "medianBox": rounded(np.median(np.array([p["box"] for _, p in v]), 0).tolist())}
            for t, v in sorted(tracks.items(), key=lambda kv: -len(kv[1]))
        ],
    }
    out = Path(a.out) if a.out else Path(a.video).with_suffix(".person.json")
    out.write_text(json.dumps(report, indent=1))

    if a.preview and thumbs:
        cols, tw = 4, 480
        th = round(tw * h / w)
        sheet = np.zeros((th * ((len(thumbs) + cols - 1) // cols), tw * cols, 3), np.uint8)
        lw = max(2, w // 300)
        for j, (k, fr) in enumerate(thumbs):
            for q in samples[k][1]:
                x, y, bw, bh = rounded(q["box"])
                cv2.rectangle(fr, (x, y), (x + bw, y + bh), (90, 90, 90), 1)
            rec = frames[k]
            if rec["found"]:
                x, y, bw, bh = rec["box"]
                cv2.rectangle(fr, (x, y), (x + bw, y + bh), (0, 255, 0), lw)
                if "headBox" in rec:
                    x, y, bw, bh = rec["headBox"]
                    cv2.rectangle(fr, (x, y), (x + bw, y + bh), (0, 0, 255), lw)
                if "crop" in rec:
                    x, y, bw, bh = rec["crop"]
                    cv2.rectangle(fr, (x, y), (x + bw, y + bh), (255, 255, 0), lw)
            cv2.putText(fr, f"{rec['time']:.2f}s", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)
            sheet[(j // cols) * th : (j // cols + 1) * th, (j % cols) * tw : (j % cols + 1) * tw] = cv2.resize(fr, (tw, th))
        cv2.imwrite(str(Path(a.video).with_suffix(".person.png")), sheet)

    print(json.dumps({"out": str(out).replace("\\", "/"), "size": [w, h], "summary": summary}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
