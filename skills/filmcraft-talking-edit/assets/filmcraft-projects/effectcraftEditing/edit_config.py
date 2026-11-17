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
