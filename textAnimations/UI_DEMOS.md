# Animated /start card components

The active edit now uses [logPlayJourney](PLAY_JOURNEY.md): one 3D camera travels between complete
cards at different depths. It begins with the approved Hermes/X card, then uses the native Slack,
Discord, Instagram, Reddit, Facebook and LinkedIn previews from /connections. The four older scene
comps described below remain in the library. Their instances have been removed from Intro 1.

The current demos use the exact /console/start tongue-card structure from log-cli's local worktree.
See START_CARD_MOTION.md for the source paths, component hierarchy, mask dimensions and motion beats.

Each complete card is assembled as a 2D precomp (startPlayX, startPlayDiscord, startPlaySlack,
startPlayReply). Hero Client has a fixed mask, and the entire client slides up from behind Tongue.
The tongue stays on top. Prompt, tools, logo and text remain native editable 2D elements.

The outer logAgentDemo/logInboxDemo/logReplyDemo/logListeningDemo scenes import those completed
precomps as 3D layers. They do not separate the client's internal layers in depth. There are no
satellites, orbiting logos, dotted backgrounds or hard navy shadows on the client.

Intro 1 keeps its saved opening, introCard, type11 and type04 and retains its 20.7667-second duration.
The corrected demos replace only the four previous walkthroughs. The original grading stays intact.

Verification: rendered the masked entrance at 30 fps and checked frames before reveal, during the
slide and at the overshoot peak. Checked the assembled Intro 1 hold and the three-card layout.
Project comparisons confirmed unrelated saved items are unchanged. All start* component layers stay
2D; the hero scene contains one complete 3D card layer and a native camera. Templates are exported
in each effects directory; startCardParts contains the editable source components.

