"""Generates build_edit.py from ../databroker/build_edit.py: same pipeline, this recording's sources and cut list."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
src = (ROOT.parent / "databroker" / "build_edit.py").read_text(encoding="utf-8")
body = src[src.index("def apply_fixes()"):]
header = (ROOT / "edit_config.py").read_text(encoding="utf-8")

SILENT_SPLIT = '''def _env_clean() -> np.ndarray:
    """10 ms dB envelope of the dialogue you hear (CLEAN: stereo s16, already on the display clock)"""
    with wave.open(str(CLEAN), "rb") as w:
        ch, sr = w.getnchannels(), w.getframerate()
        d = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").astype(np.float32).reshape(-1, ch).mean(axis=1) / 32768
    hop = sr // 100
    n = len(d) // hop
    return 10 * np.log10(np.maximum((d[: n * hop].reshape(n, hop) ** 2).mean(axis=1), 1e-12))


# the raw mic hears breaths and room noise at -50..-57 dB in the pauses, right on QUIET_DB, so the pauses are found on
# the cleaned dialogue instead (speech around -20 dBFS there, pauses under -45)
ENV_C = _env_clean()
PAUSE_DB = -45.0


def silent_split(i: int) -> bool:
    """the dialogue is quiet for PAUSE_SPLIT_S+ between the middles of words i and i+1: cut there, with the two words'
    edges moved onto the silence (the transcript often runs a word on over it)"""
    lo, hi = int((S[i] + E[i]) / 2 * 100), int((S[i + 1] + E[i + 1]) / 2 * 100)
    best, run0 = (0, 0), None
    for k in range(lo, hi + 1):
        q = k < hi and k < len(ENV_C) and ENV_C[k] < PAUSE_DB
        if q and run0 is None:
            run0 = k
        if not q and run0 is not None:
            if k - run0 > best[1] - best[0]:
                best = (run0, k)
            run0 = None
    if (best[1] - best[0]) / 100 < PAUSE_SPLIT_S:
        return False
    E[i] = min(E[i], best[0] / 100)
    S[i + 1] = max(S[i + 1], best[1] / 100)
    return True


'''
swaps = [
    ('names = {"edl": ROOT / f"databroker-edl{TAG}.json", "review": ROOT / f"databroker-review{TAG}.md",\n'
     '             "srt": ROOT / f"databroker-captions{TAG}.srt", "proj": ROOT / f"databroker{TAG}.fcproj"}',
     'names = {"edl": ROOT / f"effectcraftEditing-edl{TAG}.json", "review": ROOT / f"effectcraftEditing-review{TAG}.md",\n'
     '             "srt": ROOT / f"effectcraftEditing-captions{TAG}.srt", "proj": ROOT / f"effectcraftEditing{TAG}.fcproj"}'),
    ('"# Data brokering VSL edit review\\n\\n', '"# EffectCraft walkthrough edit review\\n\\n'),
    ('f"Data Brokering VSL {TAG[1:]}"', 'f"EffectCraft Walkthrough {TAG[1:]}"'),
    ('"Data Brokering VSL captions"', '"EffectCraft Walkthrough captions"'),
    ('(ROOT / f"databroker-camera{TAG}.json")', '(ROOT / f"effectcraftEditing-camera{TAG}.json")'),
    # the overlap is also capped by the INCOMING beat (half its length): one-word beats from the slow demo speech
    # ("I", "by") were shorter than a 12-frame overlap, so their picture clip came out empty
    ('        cursor -= ov\n        s_in, s_out, room_in, room_out = edges(a, b, hook or quick)\n'
     '        in_f, out_f = round(s_in * FPS), round(s_out * FPS)\n',
     '        s_in, s_out, room_in, room_out = edges(a, b, hook or quick)\n'
     '        in_f, out_f = round(s_in * FPS), round(s_out * FPS)\n'
     '        ov = min(ov, (out_f - in_f) // 2)\n'
     '        cursor -= ov\n'),
    # never cut inside a span listed in NO_SPLIT_AFTER (words the transcript squashed; see edit_config)
    ('            if ((gap >= GAP_S and quiet(', '            if i not in NO_SPLIT_AFTER and ((gap >= GAP_S and quiet('),
    # more close-ups: whole talking sentences full face too (cam_sentence_phrases in edit_config)
    ('    CAM_PHRASES.extend(p for p in number_phrases() if p not in CAM_PHRASES)\n',
     '    CAM_PHRASES.extend(p for p in number_phrases() if p not in CAM_PHRASES)\n'
     '    CAM_PHRASES.extend(p for p in cam_sentence_phrases() if p not in CAM_PHRASES)\n'),
    # bust-shot framing on every camera clip, after Fill Frame
    ('    run(["--project", str(proj), "--save", "run", "-"], jsonl([{"id": "clip.fillFrame", "params": {"clips": camclips}}]))\n',
     '    run(["--project", str(proj), "--save", "run", "-"], jsonl([{"id": "clip.fillFrame", "params": {"clips": camclips}}]))\n'
     '    run(["--project", str(proj), "--save", "run", "-"], jsonl(\n'
     '        [{"id": "effects.setParam", "params": {"clip": c, "effect": "motion", "param": "scale", "value": CAM_SCALE}} for c in camclips]\n'
     '        + [{"id": "effects.setParam", "params": {"clip": c, "effect": "motion", "param": "position", "value": CAM_POS}} for c in camclips]))\n'),
    # v15 (matt, 2026-11-17, "make the audio gaps shorter"): split wherever the mic is quiet for PAUSE_SPLIT_S
    ('def runs_from(indices: list[int]) -> list[list[int]]:\n', SILENT_SPLIT + 'def runs_from(indices: list[int]) -> list[list[int]]:\n'),
    ('            if i not in NO_SPLIT_AFTER and ((gap >= GAP_S and quiet(',
     '            if i not in NO_SPLIT_AFTER and (silent_split(i) or (gap >= GAP_S and quiet('),
    # v15 J-cuts: the outgoing picture runs on to the incoming picture's late cut (picture_tail in edit_config)
    ('    lag = picture_lag(segs) + [0]\n    for k, s in enumerate(segs):\n        cmds.append(',
     '    lag, tail = picture_lag(segs) + [0], picture_tail(segs) + [0]\n    for k, s in enumerate(segs):\n        cmds.append('),
    ('            "duration": (s["duration_frames"] - lag[k]) * TPF}})\n',
     '            "duration": (s["duration_frames"] - lag[k] + tail[k]) * TPF}})\n'),
    ('    lag = picture_lag(segs) + [0]\n    for k, (s, v) in enumerate(zip(segs, vids)):\n'
     '        if v != (s["timeline_start_frame"] + lag[k], s["timeline_start_frame"] + s["duration_frames"],\n',
     '    lag, tail = picture_lag(segs) + [0], picture_tail(segs) + [0]\n    for k, (s, v) in enumerate(zip(segs, vids)):\n'
     '        if v != (s["timeline_start_frame"] + lag[k], s["timeline_start_frame"] + s["duration_frames"] + tail[k],\n'),
]
for old, new in swaps:
    if not body.count(old):
        raise SystemExit(f"pattern not found: {old[:70]!r}")
    body = body.replace(old, new)
(ROOT / "build_edit.py").write_text(header + "\n\n" + body, encoding="utf-8")
print("wrote build_edit.py")
