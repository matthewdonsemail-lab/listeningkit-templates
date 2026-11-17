HEADER = r'''"""EffectCraft walkthrough (matt, Cap 2026-11-16 03.27 PM, 67.5 min), FilmCraft, built from a sentence-level cut list
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
'''
CUT_PHRASES = r'''CUT_PHRASES = [
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
'''
HOOK = r'''HOOK_PHRASES = [
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
'''
# the body: every sentence in order, minus these (see sentences.txt)
DROP = {
    0,  # "Hello, this is Claude Code, right?" (misheard intro, confirm)
    16, 30, 37, 56, 71, 80, 89, 95, 120, 126, 154, 164, 185, 189, 204, 216, 219, 221, 227, 232, 243, 244, 248, 254, 264,
    272,  # "I'm not trying to convey that people are always rapists." (flagged, cut)
    289, 291, 292, 299, 300, 301, 302, 319, 320, 353, 358, 362, 379, 380, 381, 382, 383, 384, 389, 410, 425, 428,
    444, 445, 459, 460, 461, 472, 474, 479, 487, 508, 537, 539, 540, 541, 542, 543, 545, 548, 549, 556, 576, 582, 583,
    599, 600, 601, 602, 603, 604, 609, 611, 615, 619, 620, 623, 624, 625, 651, 652, 653, 659, 661, 686, 691,
}
QUICK = {32, 39, 40, 60, 61, 70, 93, 94, 116, 129, 131, 157, 158, 191, 240, 251, 327, 328, 329, 336, 337, 356, 395, 403,
         454, 464, 465, 467, 468, 469, 563, 564, 566, 568, 570, 571, 572, 573, 574, 575, 586, 608, 610, 613, 614, 621, 622,
         669, 670, 672}
FIXES = r'''FIXES = [
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
'''

# ---- the 20 min backup cut (matt, 2026-11-16): the visual demos as the spine, opinion bits short, ref walk-throughs trimmed
def _r(a, b): return list(range(a, b + 1))
KEEP_20 = set(
    _r(1, 3) + _r(9, 14) + [17] + _r(27, 34) + _r(38, 41) + _r(54, 65)  # the full frontier-models bit: Claude Code / Codex / Hermes / Open Code on max plans       # who, what, one prompt
    + _r(66, 70)                                                                             # always a reference
    + [123] + _r(153, 158)                                                                   # The Big Short
    + _r(177, 179) + [181, 186, 193, 195, 196]                                               # the camera
    + _r(200, 213) + _r(229, 241)                                                            # dead UI -> HTML -> precomp
    + _r(326, 330)                                                                           # caricatures
    + _r(386, 400)                                                                           # stop guessing by eye
    + _r(401, 404) + _r(411, 424) + [426, 427]                                               # cyberpsycho eyes
    + _r(434, 440) + _r(446, 456)                                                            # the diagram, eyeline match
    + [457, 458, 476]                                                                   # the CRT
    + _r(483, 486) + _r(488, 507) + _r(509, 512)                                             # lines from a seed
    + _r(527, 533)                                                                           # layering
    + [538, 544] + _r(546, 555) + _r(557, 561)                                               # transitions with maths
    + _r(563, 578)                                                                           # plugins
    + _r(584, 588) + _r(593, 595) + [605, 606, 607, 608, 610] + _r(612, 616) + [622] + _r(629, 637)  # templates
    + _r(643, 650)                                                                           # taste, speak it
    + _r(654, 658) + [660] + _r(662, 685) + _r(700, 702))                                    # close
