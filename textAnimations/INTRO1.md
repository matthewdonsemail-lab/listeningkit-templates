# Intro 1: Log and Hermes

The saved opening, introCard and type04 are preserved; type11 has the revised three-line typography
and its surrounding logo arrangement. One continuous platform-play camera
journey follows type04. Use assembleIntro1.jsx against the saved project rather than rebuilding over manual edits.

| Precomp | In | Out |
| --- | --- | --- |
| introCard | 2.8333 | 4.7667 |
| type11 | 4.7667 | 9.7667 |
| type04 | 9.7667 | 12.7667 |
| logPlayJourney | 12.7667 | 20.7667 |

Each completed card is built as its own 2D comp, then imported into the outer scene as one 3D layer.
Inside startPlay*, Hero Client slides up through a stationary mask behind the foreground Tongue.
Client internals remain flat and editable. No satellite or orbiting-logo decorations are used.
See PLAY_JOURNEY.md for the seven camera stops and START_CARD_MOTION.md for the exact mask geometry.
The camera eases from Hermes/X into Slack, Discord, Instagram, Reddit, Facebook and LinkedIn. Whole
cards enter with overshoot at different Z depths; their native /connections previews stay 2D inside.

The main adjustment layer retains Halftone & Dither and Pixel Sort. Its short cut-follow motion and
blur remain in place. The dither/pixel-sort mix is bypassed during type11 so the text and logo tiles
keep their clean native appearance; type11 owns its dotted background and Page push in motion.
The duration and work area end at 20.7667 seconds. The legacy grading layer ends at 12.7667 so the new cards stay clean over their own dither background.
The old typography-only library sources remain available, without instances in Intro 1.

Build startCardParts and connectionCardParts before logPlayJourney. Exported templates live in their matching
effects folders. After changes, reopen EffectCraft for review. Commit and push only when requested.

