# The launch film's ending (plan)

Status: plan, nothing built (2026-11-15). The opener (`OPENING.md`) and cyberpunk are done; the ending is everything in
`launch film` after cyberpunk.

## Where it starts

`launch film` plays `opening` (0-15 s), then `cyberpunk` from 15.0 s to 37.43 s. Cyberpunk's outro already carries the
VO through "…so you can win more deals." (37.44 s) and ends on the blue chiaroscuro caricature close-up. So the ending
runs **37.43 s to the end of the VO (58.30 s) plus an end card**, about 21 s plus the card. `launch film` is 59.27 s
long now; the end card needs it longer.

## The lines (the recorded VO, `projects/cyberpunk/audio_words.json`)

| # | VO | Words land at (s) |
| --- | --- | --- |
| E1 | Humans can tell when you use AI. | 37.94 humans, 38.52 tell, 39.30 use, 39.64 AI |
| E2 | Log systematically defeats that by becoming you. | 40.64 Log, 41.72 defeats, 43.16 becoming, 43.68 you |
| E3 | There are opportunities across every conversation you've ever had. | 44.98 opportunities, 46.64 conversation, 48.02 had |
| E4 | Log helps you find them, speak with them, and win the people over. | 49.56 find, 50.32 speak, 51.58 win, 52.36 over |
| E5 | For whatever you do, for whatever you want. | 53.16, 54.44 |
| E6 | All locally, because that's what counts. | 55.58 all, 56.16 locally, 57.98 counts (ends 58.30) |

E1-E4 are lines 12-15 of `NARRATIVE_SCRIPT.md`; E5 and E6 are new in the recording.

## The shots

Same world and methods as the rest: stills locked to one composition, cut-outs on layers, the glitch collage,
cyberpsycho lines, the CRT over everything, thermogram flashes on the big switches, every shot a pre-comp.

| Time (s) | Shot |
| --- | --- |
| 37.43 - 40.64 | **E1, the uncanny message.** Carries on from the last caricature: the same face, close, now lit by a phone. The AI-written message on the screen glitches between styles and pixel-sorts; the profile photo won't hold still. On "tell" his eyes narrow; on "AI" the message tears (the glitch blocks). |
| 40.64 - 44.22 | **E2, it holds.** Same phone, same face. On "Log" her line (the cyberpsycho line, blue) arrives on the screen and the glitching stops: one style, sharp, still. "Becoming you": the message's photo settles into her. The one shot in the film where nothing cuts; his face softens. |
| 44.66 - 48.40 | **E3, the hall again.** Thermogram flash on "There", then the marble hall from above (cyberpunk's `open_a` composition), still cold blue, the crack still in the floor. On "conversation" a thin blue thread runs from her to each person, lighting one by one. |
| 48.68 - 52.72 | **E4, find / speak / win.** "Find them" (49.56): one thread flares. "Speak with them" (50.32): her line runs down it. "Win the people over" (51.58): that person turns to her and the warm gold of the opening floods back round them. |
| 53.16 - 55.58 | **E5, it spreads.** "For whatever you do" / "for whatever you want": the gold spreads person to person across the hall, each one settling into one face as it reaches them; the crack closes. |
| 55.58 - 58.30 | **E6, locally.** On "locally" the camera pulls up and out of the hall through the CRT glass: it was on a laptop screen on a desk, at night, in the opener's VHS look. "Because that's what counts": hold on the laptop; hard cut on "counts". |
| 58.30 - ~61 | **End card.** LOG / BY LISTENINGKIT × NOUS RESEARCH, the white marks on black, one last thermogram flash into it. |

## What has to be made

| Part | New stills (Nano Banana Pro) | Built from |
| --- | --- | --- |
| E1-E2 | about 5: the caricature lit by a phone (glitching and holding), the phone screen with the message in several styles and settled | the outro caricature (`projects/cyberpunk/outro/portrait_*.png`) as the composition reference |
| E3-E5 | about 5: the hall from above, cold with the crack; warm with the crowd; the crack closed | `open_a`'s composition, as `make_cyberpunk_opening.py` |
| E6 | about 2: the laptop on a desk at night with the hall on its screen | the opener's look |
| End card | none | the Log and Nous marks as layers |

About 12 stills: about $0.36 through treg if its hosting quota allows, about $1.80 through Google's inline endpoint if
not (as `make_opening_next.py --google`).

## Open questions for matt

- E6: does "all locally" end on the laptop (the local machine), or somewhere else?
- E1: the phone person is the caricature (carrying on from cyberpunk); or one of the two cyberpsycho men from the opener?
- The end card: how long, and does the music run out under it?
- Captions: the script plans caption cards for every line; the opener and cyberpunk don't have them yet.
