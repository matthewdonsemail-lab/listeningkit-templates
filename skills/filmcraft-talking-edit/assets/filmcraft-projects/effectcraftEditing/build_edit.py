"""EffectCraft walkthrough (matt, Cap 2026-11-16 03.27 PM, 67.5 min), FilmCraft, built from a sentence-level cut list
(the filmcraft skill: REPOS/awesome-video-editing/filmcraft; pipeline from ../databroker/build_edit.py via make_build.py).

Sources (one clock: all three Cap streams start at 6.1e-6 s in recording-meta.json, so no offsets):
  * picture: the raw Cap display.mp4 (1920x1080, ~28 fps VFR) until matt's render lands; its own sound is never placed
  * dialogue: the raw Cap mic (audio-input.m4a) decoded to mic.wav, peak-limited to -5.5 dBFS (dialogue-limited.wav).
    No Auphonic pass on this one.
  * camera: the raw Cap camera.mp4 (1280x720 VFR), same start as the display
  * system audio: not recorded (start-times.json system_audio null), so the trailers he plays are silent
  * words: AssemblyAI transcript of the raw mic (transcriptMic.json; transcript.md, sentences.txt)

Editorial (v1): the recording's own order; restarts, repeats, garbled lines, filler and the silent demo stretches cut.
A cold open of one-liners, then the body from "I'm going to show you exactly how to edit inside of this new software".
Writes NEW files only (refuses to overwrite).

Run:  uv run --no-project --with numpy python build_edit.py [--plan-only]
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
CLI = ROOT.parents[1] / "target/release/filmcraft-cli.exe"
REC = Path(r"C:\Users\0\AppData\Roaming\so.cap.desktop\recordings\Generic PnP Monitor (Display) 2026-11-16 03.27 PM.cap")
# picture: matt's Cap render (v2 on; 1920x1080 60 fps, 4050.62 s, same length as the raw display). measure_render.py:
# its audio is -3 ms against dialogue-limited.wav at 6 points, 0 ms spread, so no shift (v1 used the raw display.mp4)
VIDEO = Path(r"C:\Users\0\filmcraft\projects\effectcraft treg\How to Edit in EffectCraft.mp4")
CLEAN = ROOT / "dialogue-limited.wav"
CAMERA = REC / "content/segments/segment-0/camera.mp4"
# full-face cutaways on V2: every curse, joke and bit of banter (phrase text after FIXES; first match inside the cut);
# every number is added by number_phrases()
CAM_PHRASES = [
    "I didn't learn anything there.",
    "One prompt.",
    "And if anyone says it doesn't look good, they're lying.",
    "Please don't try to do this.",
    "Now, one thing with Claude Code is you can automate the fuck out of this.",
    "I'm pretty sure it already has won an Oscar.",
    "She's not important, she's just some scoundrel woman.",
    "Shouldn't have took out loans, very bad.",
    "chef's kiss, mate.",
    "I hate that shit.",
    "This vision model is fucking great.",
    "I think they're like aliens, lad.",
    "They're not from planet fucking Earth, mate,",
    "they are fucking evil.",
    "they're pretty funny.",
    "It's mental.",
    "That shit is over and fucking done with.",
    "The whole point of it is these people are fucking crashing.",
    "I definitely 100% bought it.",
    "I definitely didn't take a screenshot and told Claude Code to recreate it.",
    "I definitely didn't go onto some dodgy Russian website",
    "you never pay for plugins.",
    "Who's paying for Red Giant Universe?",
    "Yeah, fucking course of fucking calm, man.",
    "This looks fucking shit.",
    "Anyone who says they can edit a video like this is lying.",
    "I didn't even touch Timeline.",
    "We're cooked.",
    "Anyways, thank you very much.",
]
CAM_PAD_S, CAM_SNAP_S, CAM_MIN_S = 0.15, 0.45, 1.0
# mic clock vs the display (mic_time = video_time + OFFSET); negative: the mic started 0.38 s after the display
OFFSET = float(json.loads((ROOT / "offsets.json").read_text())["mic_lag_s"])
TAG = "-20min-v15"
CAPTION_SIZE = 36  # px at 1080 lines (FilmCraft default 54), left aligned, bottom
FPS, TPS = 60, 254_016_000_000
TPF = TPS // FPS
SHIFT = 0  # the camera shares the display's clock (same start_time in recording-meta.json)
AUDIO_SHIFT = 0  # the dialogue file is already on the display clock (prep_dialogue.sh)
GAP_S, PAD_S, MIN_BEAT_S, SNAP_S = 0.15, 0.04, 1.0, 0.25
SENT_GAP_S = 0.10
FILLER_GAP_S = 0.25
# false starts removed word-for-word: (context, part) cuts only `part` where it sits inside `context`
CUT_PHRASES = [
    ("because if you're— if you think about editing before", "if you're—"),
    ("So for example, in this research, so I used to be", "So for example, in this research,"),
    ("I found 3 trailers, 3, 4 trailers I liked.", "3 trailers,"),
    ("And I like the, I like the way", "And I like the,"),
    ("The, the, what do you call it, the volumetric effect", "The, the, what do you call it,"),
    ("which is this one here, uh, it's a tool to be able to, or for AI", "it's a tool to be able to, or"),
    ("If this did not— if this thing didn't happen,", "If this did not—"),
    ("no better scene to, to point out", "to,"),
    ("each one of the, the trailers.", "the,"),
    ("and I generated— let me get to the tweet— this shot,", "let me get to the tweet—"),
    ("which I thought was really— it was really fun", "which I thought was really—"),
    ("Again, being able to, to say what's in my head", "to,"),
    ("Well, not me personally, I was only like— if I was in here,", "I was only like—"),
    ("So, you know, in 2022,", "So, you know,"),
    ("Well, there's three, there's three people", "there's three,"),
    ("you'll, you'll understand", "you'll,"),
    ("So you, you look at it", "you,"),
    ("Not— you're gonna look at it", "Not—"),
    ("What does the scene— what was the scene showing?", "What does the scene—"),
    ("All right, uh, David from", "uh,"),
    ("the most— some of the arguably the most important people", "the most— some of the"),
    ("They're not like— they're pretty funny.", "They're not like—"),
    ("Okay, as you know, it's, it's opening shot", "it's,"),
    ("So use the— to create tension, you may use", "use the—"),
    ("filmmaking techniques to be— or video editing techniques", "filmmaking techniques to be— or"),
    ("but as you can see here, these are— this, this is just done with Python,", "these are— this,"),
    ("I was like to ChatGPT, I was like, well, you know,", "I was like, well, you know,"),
    ("we, we shoot the eye", "we,"),
    ("So you— so rather than— these 2 frames", "So you— so rather than—"),
    ("the same eyes— Eyeline match cuts", "the same eyes—"),
    ("you're able to create— this looks pretty weird.", "you're able to create—"),
    ("it's based on— I'll show the plugin after.", "it's based on—"),
    ("You can— I'm gonna say I bought this.", "You can—"),
    ("Is it— this is for After Effects.", "Is it—"),
    ("this is from Cyberpunk, this is from Cyberpunk, itself, right?", "this is from Cyberpunk,"),
    ("here's an over— here's some of the camera angles.", "here's an over—"),
    ("which again is— this is This is able to be done", "which again is— this is"),
    ("so that it It's able to just kind of— you have it bending", "It's able to just kind of—"),
    ("tools like OpenCV OpenCV, NumPy,", "OpenCV"),
    ("So it, it's melding,", "it,"),
    ("it's blending both, both frames", "both,"),
    ("It's not— I've seen a video there yesterday", "It's not—"),
    ("the ability of of AI", "of"),
    ("I think this is where being a bit of a— not using templates,", "being a bit of a—"),
    ("Or it's the most— the greatest upgrade", "it's the most—"),
]
CUT_WORDS: set[int] = set()
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
# no timeline, one prompt, can't tell it's AI, guessing is over, never pay for plugins, it's templates; ends
# on "the greatest upgrade we'll ever have" and hands over to the body. (sentence, phrase as the raw transcript has it, label)
HOOK_PHRASES = [
    # v10 (matt: "make sure it follows what this is about"): the result, the method, the proof, the joke, the numbers,
    # the payoff; hands over to "I'm going to show you exactly how to edit inside of this new software"
    (17, "I did not touch the timeline", "no_timeline"),
    (32, "One prompt.", "one_prompt"),
    (431, "you simply need free libraries and a Claude Code subscription.", "free_libraries"),
    (40, "You couldn't tell this was made with AI.", "made_with_ai"),
    (395, "That shit is over and fucking done with.", "over_and_done"),
    (570, "you never pay for plugins.", "never_pay"),
    (571, "Never.", "never"),
    (668, "it literally would have taken A week.", "a_week"),
    (669, "It's done in 2 days.", "two_days"),
    (674, "this is the greatest upgrade we'll ever have.", "greatest_upgrade"),
]


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


# ---- body: every sentence in the recording's order (sentences.txt) minus DROP: restarts, repeats, filler,
# garbled lines and the stretches where he is clicking through the demo without talking ----
DROP = [0, 4, 5, 6, 7, 8, 15, 16, 18, 19, 20, 21, 22, 23, 24, 25, 26, 35, 36, 37, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 180, 182, 183, 184, 185, 187, 188, 189, 190, 191, 192, 194, 197, 198, 199, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323, 324, 325, 331, 332, 333, 334, 335, 336, 337, 338, 339, 340, 341, 342, 343, 344, 345, 346, 347, 348, 349, 350, 351, 352, 353, 354, 355, 356, 357, 358, 359, 360, 361, 362, 363, 364, 365, 366, 367, 368, 369, 370, 371, 372, 373, 374, 375, 376, 377, 378, 379, 380, 381, 382, 383, 384, 385, 405, 406, 407, 408, 409, 410, 425, 428, 429, 430, 431, 432, 433, 441, 442, 443, 444, 445, 459, 460, 461, 462, 463, 464, 465, 466, 467, 468, 469, 470, 471, 472, 473, 474, 475, 477, 478, 479, 480, 481, 482, 487, 508, 513, 514, 515, 516, 517, 518, 519, 520, 521, 522, 523, 524, 525, 526, 534, 535, 536, 537, 539, 540, 541, 542, 543, 545, 556, 562, 579, 580, 581, 582, 583, 589, 590, 591, 592, 596, 597, 598, 599, 600, 601, 602, 603, 604, 609, 611, 617, 618, 619, 620, 621, 623, 624, 625, 626, 627, 628, 638, 639, 640, 641, 642, 651, 652, 653, 659, 661, 686, 687, 688, 689, 690, 691, 692, 693, 694, 695, 696, 697, 698, 699]
BODY = [k for k in range(len(SENTS)) if k not in set(DROP)]

# ---- quick lines: the numbers, the jokes and the curses, cut like the cold open ----
QUICK = [32, 39, 40, 60, 61, 70, 93, 94, 116, 129, 131, 157, 158, 191, 240, 251, 327, 328, 329, 336, 337, 356, 395, 403, 454, 464, 465, 467, 468, 469, 563, 564, 566, 568, 570, 571, 572, 573, 574, 575, 586, 608, 610, 613, 614, 621, 622, 669, 670, 672]
QUICK_WORDS = {i for k in QUICK for i in range(SENTS[k][0], SENTS[k][1] + 1)}

# ---- word-level caption corrections (phrase -> replacement), applied to the word list ----
# names and figures from the VSL page Matt approved (dataBrokering.html) and the Auphonic transcript where the mic
# transcript garbled a word; money slang per the caption style guide. Unverified ones are listed in the review file.
FIXES = [
    ("Opus 5.5, Halo 5.2.", "Opus 5.5, Fable 5.2."),
    ("Hermes Agent through the Niche Portal", "Hermes Agent through the Nous Portal"),
    ("Dario Amadei,", "Dario Amodei,"),
    ("Dario Armadale, Sam Altman, the Hermes girl.", "Dario Amodei, Sam Altman, the Hermes girl."),
    ("Sam Altman juxtaposes Dario Awadé", "Sam Altman juxtaposes Dario Amodei"),
    ("So Nate Fielder had", "So Nathan Fielder had"),
    ("So this TikTok The Sanae one", "So this TikTok, the sun_ae one,"),
    ("The dala-mosh effect", "The datamosh effect"),
    ("can just follow inside of Draic.", "can just follow inside of Treg."),
    ("Again, all generated with Track,", "Again, all generated with Treg,"),
    ("when I first got OpenCV 5.5,", "when I first got Opus 5.5,"),
    ("We ban social media", "We bend social media"),  # the ListeningKit page on screen: "bends social media"
]

# full-screen camera framing (matt, 2026-11-16: "a shoulder shot", no wall sign top left): on top of Fill Frame (150%),
# 1.5x more, face centred across (face_box.py: face centre 0.468 / 0.683 of the 1280x720 camera), bottom edge on the frame
CAM_SCALE, CAM_POS = 225.0, [1052.0, 270.0]
# more close-ups (matt: "not enough close ups"): whole talking stretches go full face, on top of curses, jokes and numbers.
# Sentence ranges (sentences.txt); only the ones in the cut are used.
CAM_SENTENCES = [(9, 14), (17, 17), (31, 34), (38, 41), (54, 65), (66, 70), (326, 330), (393, 395), (563, 578),
                 (584, 598), (612, 637), (640, 650), (664, 685), (700, 702)]


def cam_sentence_phrases() -> list[str]:
    """the kept text of each CAM_SENTENCES sentence (after caption fixes), as camera phrases"""
    out = []
    for a, b in CAM_SENTENCES:
        for k in range(a, b + 1):
            if k not in BODY:
                continue
            ws = [WORDS[i]["text"] for i in range(SENTS[k][0], SENTS[k][1] + 1) if i not in CUT_WORDS and WORDS[i]["text"]]
            if ws:
                out.append(" ".join(ws))
    return out


# the dialogue: v8 on, the NVIDIA RE-USE cleaned mic (run on a Colab T4, enhance/colab_job.py + colab_run_all.sh, 5 s
# chunks, no overlap; voice_reuse_full.wav, same length as the mic, 0 ms lag at 4 points), levelled like before
# (loudnorm -16, +4.9 dB, limiter -5.5 dBFS). Cut analysis stays on the raw mic.wav. DIALOGUE=raw goes back to the raw mic.
import os as _os
# v9 on (DIALOGUE=mixed, the default): RE-USE with the original patched in where RE-USE dropped speech (mix_dialogue.py
# --drop-db 15: 750 spots, 146 s) and 15% of the original under the rest, so it is less strict.
_dlg = _os.environ.get("DIALOGUE", "mixed")
if _dlg == "reuse":
    CLEAN = ROOT / "dialogue-reuse-limited.wav"
elif _dlg == "mixed":
    CLEAN = ROOT / "dialogue-mixed-limited.wav"


# matt's demo speech has many 0.25-0.55 s thinking pauses; cutting every one (the 0.25 s stammer rule) chopped sentences
# into one- and two-word beats (159 of 602 under 1 s in 20min-v6), which also jump-cuts the screen each time. 0.55 s
# keeps a sentence together (39 under 1 s) and still cuts the long ums.
FILLER_GAP_S = 0.55
# matt, 2026-11-17: "make the audio gaps shorter, there are moments where I'm not talking": 20min-v10 still had 179
# pauses of 0.25 s+ (73 over 0.4 s, 61 of them inside one clip) because the transcript stretches words over silence.
# v15: split wherever the mic itself is quiet for PAUSE_SPLIT_S (build_edit.py silent_split), and merge back only
# across gaps under that.
PAUSE_SPLIT_S = 0.30
FILLER_GAP_S = PAUSE_SPLIT_S


# AssemblyAI sometimes squashes a phrase into ~0.02 s per word (e.g. "And if you're not using frontier models," at 5:24)
# while the speech really runs on through the "gap" after it, so the cut dropped real words (matt: "it cuts there").
# Find every run of 3+ words of <= 0.03 s followed by a gap of > 1 s, spread the words over the time up to the next word,
# and never cut inside it. Found: 5:24, 5:55, 14:06, 30:20.
NO_SPLIT_AFTER: set[int] = set()
_i = 0
while _i < len(WORDS):
    _j = _i
    while _j < len(WORDS) and WORDS[_j]["end"] - WORDS[_j]["start"] <= 0.03:
        _j += 1
    if _j - _i >= 3 and _j < len(WORDS) and WORDS[_j]["start"] - WORDS[_j - 1]["end"] > 1.0:
        _t0, _t1 = WORDS[_i]["start"], WORDS[_j]["start"] - 0.1
        for _k, _w in enumerate(range(_i, _j)):
            WORDS[_w]["start"] = _t0 + (_t1 - _t0) * _k / (_j - _i)
            WORDS[_w]["end"] = _t0 + (_t1 - _t0) * (_k + 1) / (_j - _i)
        NO_SPLIT_AFTER.update(range(_i - 1, _j))
    _i = max(_j, _i + 1)


def apply_fixes() -> list[str]:
    """Rewrite word texts in place so a phrase match maps word-for-word (extra/missing words fold into the
    first/last word of the match). Returns a log of what changed."""
    log = []
    texts = [w["text"] for w in WORDS]
    for old, new in FIXES:
        o, n = old.split(), new.split()
        hits = [i for i in range(len(texts) - len(o) + 1) if texts[i:i + len(o)] == o]
        if not hits:
            log.append(f"NOT FOUND: {old!r}")
            continue
        for i in hits:
            if len(n) == len(o):
                rep = n
            elif len(n) > len(o):
                rep = n[:len(o) - 1] + [" ".join(n[len(o) - 1:])]
            else:
                rep = n + [""] * (len(o) - len(n))
            for k, t in enumerate(rep):
                texts[i + k] = t
                WORDS[i + k]["text"] = t
            log.append(f"{i}: {old!r} -> {new!r}")
    return log


def envelope(path: Path) -> np.ndarray:  # 10 ms dB envelope
    with wave.open(str(path), "rb") as w:
        d = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").astype(np.float32) / 32768
        sr = w.getframerate()
    hop = sr // 100
    n = len(d) // hop
    return 10 * np.log10(np.maximum((d[: n * hop].reshape(n, hop) ** 2).mean(axis=1), 1e-12))


ENV = np.r_[np.full(round(-OFFSET * 100), -120.0), envelope(ROOT / "mic.wav")]  # raw mic, on the display clock
S = np.array([w["start"] for w in WORDS])
E = np.array([w["end"] for w in WORDS])
SPEECH_DB = float(np.median(np.concatenate([ENV[int(S[i] * 100):int(E[i] * 100)] for i in range(len(WORDS))
                                            if 0 <= S[i] < E[i] and E[i] * 100 < len(ENV)])))
QUIET_DB = SPEECH_DB - 14.0


def quiet(a: float, b: float) -> bool:
    lo, hi = int(a * 100), int(b * 100)
    return hi <= lo or float(np.percentile(ENV[lo:hi], 95)) < QUIET_DB


def snap(t: float, lo: float, hi: float) -> float:
    """quietest 10 ms instant in [lo, hi] (clamped), else t"""
    a, b = int(max(lo, 0) * 100), int(hi * 100)
    if b - a < 2:
        return t
    k = a + int(np.argmin(ENV[a:b]))
    return k / 100 + 0.005


def tight(t: float, lo: float, hi: float, outward: int) -> float:
    """first quiet 10 ms instant walking away from the word (t) toward lo/hi, then PAD_S further out; else quietest"""
    a, b = int(max(lo, 0) * 100), int(hi * 100)
    if b - a < 2:
        return t
    idx = range(b - 1, a - 1, -1) if outward < 0 else range(a, b)
    for k in idx:
        if ENV[k] < QUIET_DB:
            return min(max((k + 0.5) / 100 + outward * PAD_S, lo), hi)
    return snap(t, lo, hi)


def _env_clean() -> np.ndarray:
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


def runs_from(indices: list[int]) -> list[list[int]]:
    """kept sentences -> kept words -> runs of consecutive words, split at quiet pauses and untranscribed sounds"""
    # word-level keep list: every word of the kept sentences, minus the words of CUT_PHRASES
    keep = sorted(i for k in indices for i in range(SENTS[k][0], SENTS[k][1] + 1) if i not in CUT_WORDS)
    groups, g = [], [keep[0]]
    for i in keep[1:]:
        if i == g[-1] + 1:
            g.append(i)
        else:
            groups.append(g); g = [i]
    groups.append(g)
    runs = []
    for g in groups:
        a, b = g[0], g[-1]
        first = a
        for i in range(a, b):
            gap = S[i + 1] - E[i]
            # a silent pause, or an untranscribed sound (AssemblyAI drops ums, uhs and restarts from the words)
            if i not in NO_SPLIT_AFTER and (silent_split(i) or (gap >= GAP_S and quiet(E[i] + PAD_S, S[i + 1] - PAD_S)) or gap >= FILLER_GAP_S
                    or (gap >= SENT_GAP_S and re.search(r"[.?!]$", WORDS[i]["text"]))):
                runs.append([first, i]); first = i + 1
        runs.append([first, b])
    # merge beats shorter than MIN_BEAT_S into a neighbour, but never back across an untranscribed-sound gap
    # (that would restore the stammer); a short leftover made only of filler words is dropped instead
    joinable = lambda i: S[i + 1] - E[i] < FILLER_GAP_S
    filler = lambda r: all(re.sub(r"[^a-z']", "", WORDS[i]["text"].lower()) in FILLER_WORDS for i in range(r[0], r[1] + 1))
    changed = True
    while changed and len(runs) > 1:
        changed = False
        for k, r in enumerate(runs):
            if E[r[1]] - S[r[0]] + 2 * PAD_S < MIN_BEAT_S:
                if k + 1 < len(runs) and runs[k + 1][0] == r[1] + 1 and joinable(r[1]):
                    runs[k + 1][0] = r[0]
                elif k > 0 and runs[k - 1][1] == r[0] - 1 and joinable(r[0] - 1):
                    runs[k - 1][1] = r[1]
                elif filler(r):
                    DROPPED.append(text(r[0], r[1]))
                else:
                    continue
                del runs[k]; changed = True; break
    return runs


def edges(a: int, b: int, hook: bool) -> tuple[float, float, float, float]:
    """source in/out seconds for words a..b, snapped to the quietest instant beside the speech, plus room tone"""
    prev_end = E[a - 1] if a else 0.0
    next_start = S[b + 1] if b + 1 < len(WORDS) else len(ENV) / 100
    lo_in = max(prev_end + 0.02, S[a] - SNAP_S)
    hi_out = min(next_start - 0.02, E[b] + SNAP_S)
    s_in = tight(S[a], lo_in, S[a] - 0.01, -1) if S[a] - lo_in > 0.03 else max(prev_end, S[a] - PAD_S / 2)
    s_out = tight(E[b], E[b] + 0.01, hi_out, +1) if hi_out - E[b] > 0.03 else min(next_start, E[b] + PAD_S / 2)
    if E[b] - S[b] < 0.04 and hi_out - E[b] <= 0.03:
        # the transcript gave the last word no length, so its sound runs past E[b]: end at the next quiet dip
        s_out = max(s_out, snap(E[b] + 0.1, E[b] + 0.05, E[b] + 0.3))
        hi_out = max(hi_out, s_out)
    if hook:  # hard cut from running speech: the nearest quiet instant within SNAP_S (else the quietest), never trusting a zero gap
        loud = float(np.percentile(ENV[int(S[a] * 100):max(int(E[b] * 100), int(S[a] * 100) + 1)], 90))
        dip = lambda t: float(ENV[max(int(t * 100) - 1, 0):int(t * 100) + 1].max()) < loud - 12
        s_in = tight(S[a] + 0.03, S[a] - SNAP_S, S[a] + 0.03, -1)
        s_in = s_in if dip(s_in) else snap(S[a], S[a] - SNAP_S, S[a] + 0.03)
        s_out = tight(E[b] - 0.03, E[b] - 0.03, E[b] + SNAP_S, +1)
        s_out = s_out if dip(s_out) else snap(E[b], E[b] - 0.03, E[b] + SNAP_S)
    if not hook:  # keep room tone beside the speech
        s_in, s_out = min(s_in, max(lo_in, S[a] - PAD_S)), max(s_out, min(hi_out, E[b] + PAD_S))
    return s_in, s_out, S[a] - s_in, s_out - E[b]


def text(a: int, b: int) -> str:
    return re.sub(r"\s+", " ", " ".join(w["text"] for w in WORDS[a:b + 1])).strip()


def find_cut_words() -> list[str]:
    """word indices of every CUT_PHRASES match inside the kept sentences"""
    norm = lambda x: re.sub(r"[^a-z0-9$']", "", x.lower())
    kept = [i for k in BODY for i in range(SENTS[k][0], SENTS[k][1] + 1)]
    toks = [norm(WORDS[i]["text"]) for i in kept]
    log = []
    CUT_WORDS.clear()
    for entry in CUT_PHRASES:
        # a plain phrase cuts every match; (context, part) cuts only `part` where it sits inside `context`
        ctx, part = (entry, entry) if isinstance(entry, str) else entry
        q = [norm(x) for x in ctx.split() if norm(x)]
        p = [norm(x) for x in part.split() if norm(x)]
        off = next(j for j in range(len(q) - len(p) + 1) if q[j:j + len(p)] == p)
        hits = [k for k in range(len(toks) - len(q) + 1) if toks[k:k + len(q)] == q]
        for k in hits:
            CUT_WORDS.update(kept[k + off:k + off + len(p)])
        log.append(f"{part!r} in {ctx!r}: {len(hits)} cut" if hits else f"NOT FOUND in cut: {ctx!r}")
    return log


def plan() -> tuple[list[dict], int]:
    segs, cursor = [], 0
    find_cut_words()

    def add(a, b, label, hook, quick=False):
        nonlocal cursor
        ov = (HOOK_OVERLAP if (hook or segs[-1]["hook"]) else body_overlap(segs[-1])) if segs else 0
        s_in, s_out, room_in, room_out = edges(a, b, hook or quick)
        in_f, out_f = round(s_in * FPS), round(s_out * FPS)
        ov = min(ov, (out_f - in_f) // 2)
        cursor -= ov
        if hook or quick:
            lead, fin, fout = 0, 1, 1
        else:
            room_before = s_in - (E[a - 1] if a else 0.0)
            lead = min(LEAD, max(0, int(room_before * FPS))) if cursor > 0 and in_f >= LEAD and not ov else 0
            fin = min(FADE, max(1, lead + round(room_in * FPS)))
            fout = min(FADE, max(1, round(room_out * FPS) + 2))
            if room_in < 0.03: fin = min(fin, 4)
            if room_out < 0.03: fout = min(fout, 4)
        segs.append({"index": len(segs), "label": label, "hook": hook, "quick": quick,
                     "audio_track": AUDIO_TRACKS[len(segs) % len(AUDIO_TRACKS)], "overlap_frames": ov, "text": text(a, b), "word_range": [a, b],
                     "source_start_s": round(in_f / FPS, 4), "source_end_s": round(out_f / FPS, 4),
                     "source_in_frame": in_f, "duration_frames": out_f - in_f, "timeline_start_frame": cursor,
                     "timeline_start_s": round(cursor / FPS, 4), "audio_lead_frames": lead,
                     "fade_in_frames": fin, "fade_out_frames": fout})
        cursor += out_f - in_f

    for n, (a, b, role) in enumerate(HOOK):
        add(a, b, f"hook_{n + 1}_{role}", True)
    for n, (a, b) in enumerate(runs_from(BODY)):
        add(a, b, f"vsl_{n + 1:03d}", False, bool(QUICK_WORDS.intersection(range(a, b + 1))))
    return segs, cursor


def camera_spans(segs: list[dict]) -> tuple[list[dict], list[str]]:
    """timeline [start, end) frames for each cutaway, split at beat edges, snapped to a beat edge when close"""
    norm = lambda x: re.sub(r"[^a-z0-9$']", "", x.lower())
    kept = [(s, i) for s in segs for i in range(s["word_range"][0], s["word_range"][1] + 1) if WORDS[i]["text"]]
    toks = [norm(WORDS[i]["text"]) for _, i in kept]
    spans, missing = [], []
    for ph in CAM_PHRASES:
        q = [norm(x) for x in ph.split() if norm(x)]
        hit = next((k for k in range(len(toks) - len(q) + 1) if toks[k:k + len(q)] == q), None)
        if hit is None:
            missing.append(ph)
            continue
        part_all = kept[hit:hit + len(q)]
        for seg_index in dict.fromkeys(s["index"] for s, _ in part_all):
            part = [(s, i) for s, i in part_all if s["index"] == seg_index]
            s = part[0][0]
            b0 = s["timeline_start_frame"]
            b1 = b0 + s["duration_frames"]
            to_tl = lambda t: b0 + round((t - s["source_in_frame"] / FPS) * FPS)
            a = max(b0, to_tl(WORDS[part[0][1]]["start"] - CAM_PAD_S))
            z = min(b1, to_tl(WORDS[part[-1][1]]["end"] + CAM_PAD_S))
            if a - b0 <= CAM_SNAP_S * FPS: a = b0
            if b1 - z <= CAM_SNAP_S * FPS: z = b1
            if z - a >= CAM_MIN_S * FPS:
                spans.append({"phrase": ph, "start_frame": a, "end_frame": z,
                              "source_in_frame": s["source_in_frame"] + (a - b0)})
    spans.sort(key=lambda x: x["start_frame"])
    merged = []
    for sp in spans:  # join cutaways that touch in continuous source so the face shot does not blink off
        if (merged and sp["start_frame"] - merged[-1]["end_frame"] <= 12
                and sp["source_in_frame"] - merged[-1]["source_in_frame"] == sp["start_frame"] - merged[-1]["start_frame"]):
            merged[-1]["end_frame"] = sp["end_frame"]
            merged[-1]["phrase"] += " / " + sp["phrase"]
        else:
            merged.append(dict(sp))
    return merged, missing


def run(args: list[str], payload: str | None = None) -> list[dict]:
    p = subprocess.run([str(CLI), *args], input=payload, text=True, capture_output=True, cwd=ROOT.parents[1])
    out = []
    for line in p.stdout.splitlines():
        try:
            v = json.loads(line)
            if isinstance(v, dict): out.append(v)
        except json.JSONDecodeError:
            pass
    if not out:
        try:
            v = json.loads(p.stdout)
            out = [v] if isinstance(v, dict) else [x for x in v if isinstance(x, dict)]
        except json.JSONDecodeError:
            pass
    if p.returncode or any(not r.get("ok", True) for r in out):
        sys.stderr.write(p.stderr[-1500:])
        raise SystemExit(f"FilmCraft failed ({p.returncode}): {[r for r in out if not r.get('ok', True)][:2]} {p.stdout[-400:]}")
    return out


def jsonl(cs: list[dict]) -> str:
    return "\n".join(json.dumps(c, separators=(",", ":")) for c in cs) + "\n"


def stamp(t: float) -> str:
    ms = round(max(0, t) * 1000)
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def captions(segs: list[dict]) -> str:
    cues = []  # [t0, t1, text, segment index]
    for s in segs:
        a, b = s["word_range"]
        base = s["timeline_start_s"] - s["source_in_frame"] / FPS
        lo, hi = s["timeline_start_s"], s["timeline_start_s"] + s["duration_frames"] / FPS
        chunk = []
        ws = [w for w in WORDS[a:b + 1] if w["text"]]
        for w in ws + [None]:
            if w is not None: chunk.append(w)
            if chunk and (w is None or len(chunk) >= 8 or w["text"].endswith((".", "?", "!"))):
                t0 = max(lo, base + chunk[0]["start"])
                t1 = min(hi, base + chunk[-1]["end"])
                txt = " ".join(c["text"] for c in chunk)
                if cues and cues[-1][3] == s["index"] and (t1 - t0 < 0.3 or len(chunk) == 1):
                    cues[-1][1], cues[-1][2] = max(cues[-1][1], t1, t0 + 0.05), cues[-1][2] + " " + txt  # no orphan cue
                else:
                    cues.append([t0, max(t1, t0 + 0.3), txt, s["index"]])
                chunk = []
    for c, d in zip(cues, cues[1:]):  # never run into the next cue
        c[1] = min(c[1], d[0] - 0.001)
    bad = [c for c in cues if c[1] <= c[0]]
    if bad:
        raise SystemExit(f"bad caption timings: {bad[:3]}")
    return "\n".join(f"{k}\n{stamp(c[0])} --> {stamp(c[1])}\n{c[2]}\n" for k, c in enumerate(cues, 1))


def main() -> None:
    fixlog = apply_fixes()
    segs, total = plan()
    names = {"edl": ROOT / f"effectcraftEditing-edl{TAG}.json", "review": ROOT / f"effectcraftEditing-review{TAG}.md",
             "srt": ROOT / f"effectcraftEditing-captions{TAG}.srt", "proj": ROOT / f"effectcraftEditing{TAG}.fcproj"}
    print(f"speech median {SPEECH_DB:.1f} dB, quiet threshold {QUIET_DB:.1f} dB")
    print(f"{len(segs)} beats ({sum(s['hook'] for s in segs)} hook), {total / FPS:.1f}s = {total / FPS / 60:.1f} min "
          f"(hook {sum(s['duration_frames'] for s in segs if s['hook']) / FPS:.1f}s)")
    for l in fixlog:
        if l.startswith("NOT FOUND"): print(l)
    CAM_PHRASES.extend(p for p in number_phrases() if p not in CAM_PHRASES)
    CAM_PHRASES.extend(p for p in cam_sentence_phrases() if p not in CAM_PHRASES)
    cams, missing = camera_spans(segs)
    cams = jcut_cams(cams, segs)
    print(f"camera cutaways {len(cams)}, {sum(c['end_frame'] - c['start_frame'] for c in cams) / FPS:.1f}s full-face")
    for m in missing:
        print("CAMERA PHRASE NOT IN CUT:", m)
    if "--plan-only" in sys.argv:
        for c in cams:
            print(f"  {c['start_frame'] / FPS:7.2f}-{c['end_frame'] / FPS:7.2f}  {c['phrase'][:70]}")
        return
    for f in names.values():
        if f.exists():
            raise SystemExit(f"{f.name} exists; not overwriting")
    names["edl"].write_text(json.dumps({"meta": {
        "source": str(VIDEO), "dialogue": str(CLEAN), "mic_and_camera_lag_s": OFFSET, "fps": FPS, "gap_s": GAP_S,
        "pad_s": PAD_S, "min_beat_s": MIN_BEAT_S, "lead_frames": LEAD, "fade_frames": FADE,
        "speech_db": round(SPEECH_DB, 1), "quiet_db": round(QUIET_DB, 1), "source_s": round(len(ENV) / 100, 2),
        "edited_s": round(total / FPS, 2), "beats": len(segs), "hook": HOOK, "body_sentences": BODY},
        "segments": segs}, indent=1), encoding="utf-8")
    names["review"].write_text(
        "# EffectCraft walkthrough edit review\n\n## Caption corrections applied\n\n" + "\n".join(f"- {l}" for l in fixlog) +
        "\n\n## Beats\n\n" + "\n".join(
            f"{s['index'] + 1:03d} {s['audio_track']} out {s['timeline_start_s']:.2f}-"
            f"{s['timeline_start_s'] + s['duration_frames'] / FPS:.2f}s  src {s['source_start_s']:.2f}-{s['source_end_s']:.2f}s"
            f"{'  HOOK' if s['hook'] else '  QUICK' if s['quick'] else ''}: {s['text']}" for s in segs) + f"\n\nTotal {total / FPS:.1f}s, {len(segs)} beats\n",
        encoding="utf-8")
    names["srt"].write_text(captions(segs), encoding="utf-8")

    proj = names["proj"]
    created = run(["--save-as", str(proj), "run", "-"], jsonl([
        {"id": "file.newProject", "params": {"name": f"EffectCraft Walkthrough {TAG[1:]}"}},
        {"id": "file.newSequence", "params": {"name": f"EffectCraft Walkthrough {TAG[1:]}", "width": 1920, "height": 1080,
                                              "fps": FPS, "sampleRate": 48000, "video": 2, "audio": 4}}]))
    seq = created[1]["result"]["sequence"]
    clean = run(["--project", str(proj), "--save", "import", str(CLEAN)])[0]["items"][0]
    vid = run(["--project", str(proj), "--save", "import", str(VIDEO)])[0]["items"][0]
    cam = run(["--project", str(proj), "--save", "import", str(CAMERA)])[0]["items"][0]

    def place_audio(item, tracks):
        cmds = [{"id": "sequence.open", "params": {"item": seq}}]
        for i, s in enumerate(segs):
            lead = s["audio_lead_frames"]
            cmds.append({"id": "timeline.place", "params": {
                "item": item, "track": s["audio_track"], "frame": s["timeline_start_frame"] - lead,
                "sourceIn": (s["source_in_frame"] - lead) * TPF + AUDIO_SHIFT, "duration": (s["duration_frames"] + lead) * TPF}})
        res = run(["--project", str(proj), "--save", "run", "-"], jsonl(cmds))
        clips = [r["result"]["clips"][0] for r in res if r.get("id") == "timeline.place"]
        if len(clips) != len(segs):
            raise SystemExit(f"expected {len(segs)} placements, got {len(clips)}")
        return clips

    aclips = place_audio(clean, ("A1", "A2"))
    cmds = []
    for clips in (aclips,):
        for s, c in zip(segs, clips):
            cmds.append({"id": "sequence.applyAudioTransition", "params": {"clip": c, "edge": "in", "frames": s["fade_in_frames"]}})
            cmds.append({"id": "sequence.applyAudioTransition", "params": {"clip": c, "edge": "out", "frames": s["fade_out_frames"]}})
    cmds += [{"id": "timeline.setTargeting", "params": {"track": t, "sourcePatch": False}} for t in ("A1", "A2", "A3", "A4")]
    lag, tail = picture_lag(segs) + [0], picture_tail(segs) + [0]
    for k, s in enumerate(segs):
        cmds.append({"id": "timeline.place", "params": {
            "item": vid, "track": "V1", "frame": s["timeline_start_frame"] + lag[k],
            "sourceIn": (s["source_in_frame"] + lag[k]) * TPF,
            "duration": (s["duration_frames"] - lag[k] + tail[k]) * TPF}})
    cmds += [{"id": "captions.import", "params": {"path": str(names["srt"]), "name": "EffectCraft Walkthrough captions"}},
             {"id": "captions.setStyle", "params": {"track": "C1", "align": "left", "anchor": "bottom", "margin": 0.05, "background": True, "size": CAPTION_SIZE}}]
    run(["--project", str(proj), "--save", "run", "-"], jsonl(cmds))

    # full-face camera cutaways on V2 (no sound), scaled to fill the 1920x1080 frame
    camcmds = [{"id": "sequence.open", "params": {"item": seq}}] + [
        {"id": "timeline.setTargeting", "params": {"track": t, "sourcePatch": False}} for t in ("A1", "A2", "A3", "A4")]
    for c in cams:
        camcmds.append({"id": "timeline.place", "params": {
            "item": cam, "track": "V2", "frame": c["start_frame"],
            "sourceIn": c["source_in_frame"] * TPF + SHIFT, "duration": (c["end_frame"] - c["start_frame"]) * TPF}})
    res = run(["--project", str(proj), "--save", "run", "-"], jsonl(camcmds))
    camclips = [r["result"]["clips"][0] for r in res if r.get("id") == "timeline.place"]
    if len(camclips) != len(cams):
        raise SystemExit(f"expected {len(cams)} camera placements, got {len(camclips)}")
    run(["--project", str(proj), "--save", "run", "-"], jsonl([{"id": "clip.fillFrame", "params": {"clips": camclips}}]))
    run(["--project", str(proj), "--save", "run", "-"], jsonl(
        [{"id": "effects.setParam", "params": {"clip": c, "effect": "motion", "param": "scale", "value": CAM_SCALE}} for c in camclips]
        + [{"id": "effects.setParam", "params": {"clip": c, "effect": "motion", "param": "position", "value": CAM_POS}} for c in camclips]))
    (ROOT / f"effectcraftEditing-camera{TAG}.json").write_text(json.dumps(cams, indent=1), encoding="utf-8")

    out = json.loads(subprocess.run([str(CLI), "--project", str(proj), "inspect", "sequence", "--compact"],
                                    capture_output=True, text=True, cwd=ROOT.parents[1]).stdout)
    aud = {c["clip"]: c for t in out["audio"] for c in t["items"]}
    vids = sorted((c["startFrame"], c["endFrame"], round(c["sourceIn"] / TPF)) for t in out["video"] if t["name"] in ("V1", "Video 1") for c in t["items"])
    camv = sorted((c["startFrame"], c["endFrame"], round((c["sourceIn"] - SHIFT) / TPF)) for t in out["video"] if t["name"] in ("V2", "Video 2") for c in t["items"])
    bad_cam = sum(v != (c["start_frame"], c["end_frame"], c["source_in_frame"]) for v, c in zip(camv, cams)) + abs(len(camv) - len(cams))
    bad = 0
    lag, tail = picture_lag(segs) + [0], picture_tail(segs) + [0]
    for k, (s, v) in enumerate(zip(segs, vids)):
        if v != (s["timeline_start_frame"] + lag[k], s["timeline_start_frame"] + s["duration_frames"] + tail[k],
                 s["source_in_frame"] + lag[k]):
            bad += 1
    for clips in (aclips,):
        for s, c in zip(segs, clips):
            a, lead = aud.get(c), s["audio_lead_frames"]
            if (a is None or a["startFrame"] != s["timeline_start_frame"] - lead
                    or a["endFrame"] != s["timeline_start_frame"] + s["duration_frames"]
                    or round((a["sourceIn"] - AUDIO_SHIFT) / TPF) != s["source_in_frame"] - lead):
                bad += 1
    print(f"{proj.name}: {len(vids)} picture clips (no source sound), {len(aud)} audio clips, "
          f"fades {sum(len(t['transitions']) for t in out['audio'])}, {out['durationFrames'] / FPS:.1f}s, mismatches {bad}, "
          f"camera cutaways {len(camv)} (mismatches {bad_cam})")
    if bad or bad_cam:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
