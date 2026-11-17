# EffectCraft walkthrough v1: notes for matt

`effectcraftEditing-v1.fcproj` is built from the raw Cap files (display, mic, camera) with the filmcraft skill:
- a cold open of one-liners;
- tight joins;
- stacked J-cuts over A1–A4;
- full-face cutaways on the curses, jokes and numbers;
- captions bottom left at size 36.

67.5 min → 44.0 min, 1,147 beats.

## Cold open (14.8 s)
"I did not touch the timeline" → "One prompt." → "You couldn't tell this was made with AI." → "That shit is over and fucking done with." → "you never pay for plugins. Never." → "This isn't video editing. What this is is templates," → "this is the greatest upgrade we'll ever have." It then hands over to "I'm going to show you exactly how to edit inside of this new software…"

## Cut on purpose
- Restarts, repeats, "Okay." and "Right.", and garbled lines (sentence numbers in `edit_config.py` `DROP`, text in `sentences.txt`).
- **The silent demo stretches.** Where you were clicking through or playing something without talking (27:02–27:56, 34:54–35:22, 35:38–36:14, 54:05–54:27, 57:49–58:16, 58:40–58:59, 62:04–62:20), the footage goes with the cut. Say which ones to put back as B-roll.
- "I'm not trying to convey that people are always rapists." (24:42) is cut. It reads wrong out of context.
- "Hello, this is Claude Code, right?" (0:02) is cut. The transcript probably misheard the opening.

## Please confirm (transcript words I'm not sure of)
- "Track Matte … an open-source application. It could do 99% of everything" (14:55). Which tool is this?
- "Permutation has unlocked this" (5:21). Cut for now.
- "get OpenCV 5.3, build it as a UI" (20:47). Opus? Left as heard.
- "It won Short by Opus 5.5" (61:19). "one-shot by Opus 5.5"? Left as heard.
- "Fernacade to 10 Minute Health" (4:44), the creators you edited for.
- "Capri" (34:15), the Edgerunners malware character.
- "Ezra Cohen's LUT pack for Filmographix" (55:04).
- "the CMC generation red wash" (49:17), probably the NumPy red lines.
- "I trust the GPT-2.5 model more" (50:02).
- Fixed in captions:
  - Halo 5.2 → Fable 5.2
  - Niche Portal → Nous Portal
  - Amadei/Armadale/Awadé → Amodei
  - Nate → Nathan Fielder
  - The Sanae → sun_ae
  - dala-mosh → datamosh
  - Draic/Track → Treg
  - OpenCV 5.5 → Opus 5.5 (59:13)
  - "We ban social media" → "We bend social media" (the ListeningKit page on screen says "bends")

## Sound
- The laptop mic is quiet, so the dialogue is loudness-normalised (`prep_dialogue.sh`). The edited mix measures −17.5 LUFS with a −4.1 dBFS peak and no clipping. The first pass was −35.2 LUFS.
- No system audio was recorded: Cap's `start-times.json` has `system_audio: null`. The trailers and TikToks you play are silent in this file.
- If they need sound, you'd need to record again with system audio on, or lay the reference audio in separately.

## Checked / not checked
- **Checked:**
  - The project read back with every picture, audio and camera clip at its planned frame and source-in (0 mismatches).
  - Four frames rendered: the cold open, 5 min, the "aliens" face cutaway, and the outro.
  - The audio mix exported and measured (see below).
- **Not checked by ear:** the 1,147 joins. The demo parts are slow speech, so many beats are a word or two. Listen through the body for joins that sound choppy.
- **Picture:** v1 used the raw display.mp4.
  - **v2** (`effectcraftEditing-v2.fcproj`) uses your render, `effectcraft treg/How to Edit in EffectCraft.mp4`.
  - It's the same length as the raw display (4050.6 s).
  - Its audio is −3 ms against the timeline dialogue at 6 points, with 0 ms spread (`measure_render.py`), so the source-ins are unchanged.
  - The cut is identical to v1, and the frames match at 0:03, 5:00, 22:00 and 43:20.
