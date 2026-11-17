CAM_PAD_S, CAM_SNAP_S, CAM_MIN_S = 0.15, 0.45, 1.0
# mic clock vs the display (mic_time = video_time + OFFSET); negative: the mic started 0.38 s after the display
OFFSET = float(json.loads((ROOT / "offsets.json").read_text())["mic_lag_s"])
TAG = "-v1"
CAPTION_SIZE = 36  # px at 1080 lines (FilmCraft default 54), left aligned, bottom
FPS, TPS = 60, 254_016_000_000
TPF = TPS // FPS
SHIFT = 0  # the camera shares the display's clock (same start_time in recording-meta.json)
AUDIO_SHIFT = 0  # the dialogue file is already on the display clock (prep_dialogue.sh)
GAP_S, PAD_S, MIN_BEAT_S, SNAP_S = 0.15, 0.04, 1.0, 0.25
SENT_GAP_S = 0.10
FILLER_GAP_S = 0.25
# false starts removed word-for-word: (context, part) cuts only `part` where it sits inside `context`
@@CUT_PHRASES@@CUT_WORDS: set[int] = set()
FILLER_WORDS = {"so", "and", "okay", "ok", "right", "like", "now", "yeah", "well", "but", "um", "uh", "anyway", "anyways"}
DROPPED: list[str] = []
LEAD, FADE = 5, 18

RAW = json.loads((ROOT / "transcriptMic.json").read_text(encoding="utf-8"))["words"]
WORDS = [{"text": w["text"], "start": w["start"] / 1000 - OFFSET, "end": w["end"] / 1000 - OFFSET,
          "confidence": w.get("confidence", 1.0)} for w in RAW]

# sentences, same split as sentences.txt (a word ending in . ? ! closes a sentence)
SENTS, cur = [], []
for i, w in enumerate(WORDS):
    cur.append(i)
    if re.search(r"[.?!]$", w["text"]):
        SENTS.append((cur[0], cur[-1])); cur = []
if cur:
    SENTS.append((cur[0], cur[-1]))

# ---- cold open: one-liners cut out of sentences, in play order (hook.md, casual/comedic creator videos) ----
# the hype, the one person paid, the jokes, the credits, the cost, the commissions; ends on "Yummy, yummy." and
# hands over to the start of the recording. (sentence, phrase as the raw transcript has it, label)
@@HOOK_PHRASES@@


def _phrase_words(k: int, phrase: str) -> tuple[int, int]:
    norm = lambda x: re.sub(r"[^a-z0-9$']", "", x.lower())
    a, b = SENTS[k]
    q = [norm(x) for x in phrase.split()]
    t = [norm(WORDS[i]["text"]) for i in range(a, b + 1)]
    j = next(j for j in range(len(t) - len(q) + 1) if t[j:j + len(q)] == q)
    return a + j, a + j + len(q) - 1


# (first word, last word, label)
HOOK = [(*_phrase_words(k, ph), label) for k, ph, label in HOOK_PHRASES]

# J-cuts (mandatory): the cold open stacks a fixed 6 frames over the line before; the body up to 12 frames, limited to
# where the outgoing line's audio is going down. Dialogue rotates over A1-A4 so the overlaps stack.
HOOK_OVERLAP = 6  # frames at 60 fps (0.1 s)
BODY_OVERLAP = 12  # frames at 60 fps (0.2 s), the base
AUDIO_TRACKS = ("A1", "A2", "A3", "A4")


def body_overlap(prev: dict) -> int:
    """frames the next line may start over the tail of `prev`: where prev's audio is going down, at most BODY_OVERLAP"""
    a0, z = prev["word_range"]
    end = prev["source_end_s"]
    loud = float(np.percentile(ENV[int(S[a0] * 100):max(int(E[z] * 100), int(S[a0] * 100) + 1)], 90))
    t_down = end
    for k in range(int(end * 100) - 1, int(max(S[a0], end - 0.4) * 100), -1):
        if ENV[k] >= loud - 6:
            t_down = (k + 1) / 100
            break
    return max(0, min(BODY_OVERLAP, round((end - t_down) * FPS), prev["duration_frames"] // 3))


# numbers go full face for emphasis (Matt, 2026-10-15)
NUMBER = re.compile(r"\$|\d[\d,.]*\s*(?:k\b|%)|\d{1,3}(?:,\d{3})+|\b\d{3,}\b|million|milli\b|grand\b|large\b", re.I)


def number_phrases() -> list[str]:
    """each number said in the cut, with two words either side"""
    out = []
    for k in sorted(set(BODY) | {k for k, _, _ in HOOK_PHRASES}):
        a, b = SENTS[k]
        kept = [i for i in range(a, b + 1) if i not in CUT_WORDS and WORDS[i]["text"]]
        for j, i in enumerate(kept):
            if NUMBER.search(WORDS[i]["text"]):
                out.append(" ".join(WORDS[x]["text"] for x in kept[max(0, j - 2):j + 3]))
    return list(dict.fromkeys(out))


# matt, 2026-11-17: "the J-cut stuff isn't being done with the few frames so it can then cut into the next one": the
# audio overlap above only covers the outgoing line's quiet tail (0 frames on 76 of 431 cuts in 20min-v10), so the voice
# never really led the picture. Now every body cut is a J-cut of at least JCUT frames: the incoming line's audio starts,
# its picture cuts in JCUT frames later; the outgoing picture runs on over that (picture only, past its audio).
JCUT = 8  # frames at 60 fps


def picture_lag(segs: list[dict]) -> list[int]:
    """frames each picture clip starts after its line's audio"""
    out = []
    for k, s in enumerate(segs):
        ov = s.get("overlap_frames", 0)
        out.append(0 if k == 0 else (ov if s["hook"] else max(ov, min(JCUT, s["duration_frames"] // 3))))
    return out


def picture_tail(segs: list[dict]) -> list[int]:
    """frames each picture clip runs past its line's audio, to meet the next picture's late cut"""
    lag = picture_lag(segs)
    return [max(0, lag[k + 1] - segs[k + 1].get("overlap_frames", 0)) if k + 1 < len(segs) else 0 for k in range(len(segs))]


def jcut_cams(cams: list[dict], segs: list[dict]) -> list[dict]:
    """a camera cutaway that starts on a line's start starts on its (late) picture cut; one that ends on a line's end
    runs on to the next picture cut"""
    lag, tail = picture_lag(segs), picture_tail(segs)
    at = {s["timeline_start_frame"]: lag[k] for k, s in enumerate(segs)}
    ends = {s["timeline_start_frame"] + s["duration_frames"]: tail[k] for k, s in enumerate(segs)}
    for c in cams:
        d = at.get(c["start_frame"], 0)
        c["start_frame"] += d
        c["source_in_frame"] += d
        c["end_frame"] += ends.get(c["end_frame"], 0)
    return cams


# ---- body: sentence indices kept, original order (see sentences.txt), grouped like the VSL page ----
# Dropped on purpose: restarts and repeats (14, 21, 54, 60-62, 200-201, 204, 399...), garbled spans (28-29 "Infomill",
# 79-83, 118, 163, 249 "$28,840", 429), unverifiable numbers (72-73 SubQ context/tokens, 241 "100,000 credits"),
# and filler ("Right.", "Okay.", "All right."); second restatements and asides trimmed for length (v1, 22.8 -> ~20 min).
@@BODY@@

# ---- quick lines: the numbers, the jokes and the curses, cut like the cold open ----
@@QUICK@@QUICK_WORDS = {i for k in QUICK for i in range(SENTS[k][0], SENTS[k][1] + 1)}

# ---- word-level caption corrections (phrase -> replacement), applied to the word list ----
# names and figures from the VSL page Matt approved (dataBrokering.html) and the Auphonic transcript where the mic
# transcript garbled a word; money slang per the caption style guide. Unverified ones are listed in the review file.
@@FIXES@@
