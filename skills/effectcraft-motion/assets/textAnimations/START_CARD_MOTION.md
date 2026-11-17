# /start cards as motion graphics

For the active continuous camera sequence, see [PLAY_JOURNEY.md](PLAY_JOURNEY.md). The four separate
scenes below are retained library studies; Intro 1 now uses logPlayJourney and the /connections plays.

The exact source is `log-cli/.claude/worktrees/site-mcp-promo-452719/site/apps/web/src/pages/console/`:
`StartPage.tsx`, `PlatformInterfaceTongue.tsx`, `AgentCover.tsx`, `agentPlatforms.tsx`, and
`components/ai-elements/agentToolCall.tsx`. The main checkout no longer has the console route.

Preserve the source object's anatomy: dark Hermes client with its thin border and compact chrome,
prompt and tool transcript, and a separate overlapping blue play card beneath. The blue card uses
the source's lighter blue top, deeper blue base, white platform icon, hand-drawn title and short copy.
The client has a soft edge, not a hard navy shadow. No browser sidebar or dotted scene backdrop.

Build each complete card as a reusable **2D precomp**, then import the finished card into the outer
scene as **one 3D layer**. All client, prompt, tools and tongue layers inside the component stay 2D.
Do not separate the client's internal pieces along Z. Do not add satellites or orbiting logo tiles.

`startClientContentX/Discord/Slack/Reply` assembles the client. `startClientReveal*` moves that complete
client upward from y=1090 to y=440, starting at 0.5 seconds and settling at 1.5 seconds. `startPlay*`
holds a fixed rectangular mask on `Hero Client` with its bottom at y=744, and places `Tongue` in front
at y=827 (visible top y=713). The overlap stays closed even at the small overshoot peak. Only the outer
scene has a 3D camera and enables 3D on the completed `startPlay*` instance. Collapse stays off.

| Scene | Frames / 30 fps | Camera and action |
| --- | --- | --- |
| logAgentDemo | 0–215 | Tongue pops in; the complete client slides up through its fixed mask behind the tongue. One completed card moves under the camera, then exits left. |
| logInboxDemo | 0–239 | Three completed X, Discord and Slack card precomps fan out at different depths. Each card's internal masked reveal stays 2D. |
| logReplyDemo | 0–269 | One completed card. Draft and voice states appear inside the client; the camera moves around the intact component. |
| logListeningDemo | 0–251 | Completed X, Discord and Slack cards slide through in sequence. No orbiting logos or payload satellites. |

Opening, introCard, type11 and type04 stay as saved. Replace only the four rejected UI demonstrations.
Keep 1920×1080, 30 fps and the existing scene durations so Intro 1's sequence remains contiguous.
Review the masked entrance frame by frame and verify that the client never leaks below the tongue.
