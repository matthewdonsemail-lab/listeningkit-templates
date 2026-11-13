---
name: effectcraft-motion
description: Build and refine editable native EffectCraft product motion graphics, using completed 2D component precomps, 3D camera scenes, ListeningKit styling, and the saved-project CLI workflow. Use for this EffectCraft project rather than converting it to HTML video.
---

# Native EffectCraft motion

The reference project is `textAnimations` in `C:/Users/0/.buzz/REPOS/listeningkit-templates`.
Read its `README.md`, `MOTION.md` and the relevant scene document before editing. The native CLI is
`C:/Program Files/ArtCraft/EffectCraft/effectcraft-cli.exe`. Work through source generators and the
CLI; do not operate the desktop UI when the user has requested no computer use.

## Build components before staging the camera

- Inspect the actual React component, local assets and a browser screenshot when requested. Use
  those as references; screenshots do not replace editable shapes/text in the delivered precomp.
- Build the entire card, terminal, conversation or table as a 2D source comp. Keep source internals
  2D. Import that completed precomp into the outer scene as one 3D layer, with collapse disabled.
- For a tongue play, the client slides upward through a fixed Add mask behind the foreground blue
  tongue. The mask stays fixed; only the nested client content moves. See `START_CARD_MOTION.md`.
- Place complete cards at distinct Z depths and animate a native two-node camera. Use the requested
  choreography. `connectionPlays.mjs` shows a lateral tour; `researchDepth.mjs` shows a camera that
  zooms out, pans diagonally between different X/Y/Z positions, then zooms into the next panel.
  Give each phase time to read; a straight depth stack does not substitute for a pan.
- For an explicitly outward-only Z track, use `threeStepsTrack.mjs`: ordered alternating X positions,
  one eye level, successively deeper cards and strictly retreating native camera Z. Native camera
  Zoom supplies long visual pushes without reversing the dolly. Yank wide, swing laterally, push
  into the next focus and rebound. Gate future cards and paths until the camera has passed their
  planes, and verify native Z at every rendered frame. See `THREE_STEPS_TRACK.md`.
- Match terminal chrome, identity and branding to the actual agent. Changing a Claude Code prompt
  does not turn that component into Hermes. `hermesAgentTerminal` is the dedicated native Hermes UI.
- Avoid decorative satellite logos. World-space paths can clarify connections/depth when useful.

## Motion and typography

For commentary-led exposition, follow `textAnimations/EDITING_STYLE.md`: one full-screen thought,
stable large typography, voice-timed word cues, a reading hold and restrained motion. Brief montage
or concept shots bridge the exposition. Choose the idea/action/outcome that supports the spoken
sentence; do not default to recreating a platform dashboard. The website's Control/ListeningIntro
typography and edge ears are the references. `expositionCards.mjs` provides native positional parts
and a standalone study. Treat its word timing as provisional until the actual narration is supplied.

Use staggered entrances for related elements, complete-card scale overshoot and damped camera
arrival overshoot. The scale peak must occur while the camera sees the card: an offscreen bounce
does not communicate an entrance. Keep some dolly/drift in holds. Check the largest combined
camera/scale peak for clipping. A slightly smaller resting card leaves room for its bounce.

Complete cards exit with an overshoot scale-out: anticipate slightly larger, then scale to zero.
Keep card opacity at 100%; do not fade completed steps away. Avoid several rapid lens/roll/scale
reversals on the same arrival. Use a broad damped spring and sparse camera poses; the natural
cubic path in `threeStepsTrack.mjs` keeps both velocity and acceleration continuous for a fluid swing.

For fluid multi-panel camera work, connect anticipation, pullback, curved pan, rotating push-in,
post-pan rebound and the next drift in one path with continuous velocity. Avoid restarting isolated
eases that fully stop at every focus. Use a shared whole-panel spring so arrivals feel related.
For a connection that communicates a handoff, animate Trim Paths End toward the destination, then
Start to clear the tail after arrival. A looping dash over a complete rail communicates a different
thing. Keep its timing tied to the action rather than an arbitrary offset loop.

Use a beat grid for quick demos (currently 120 BPM / 30 fps); align it to actual music when supplied.
Accelerate nested content so its meaningful action finishes in the visible window. Include exits.

Keep a clear text hierarchy, intentional line breaks and consistent alignment. Use navy Satoshi for
supporting copy and one focused blue Schoolbell sticker highlight, with restrained white/navy outlines.
For editable text containers, measure settled source bounds and account for the animated peak.

Choose the background for the scene. The research composition uses the reusable smooth
`brandBlueGradient` and white connecting lines, with no external context headings. The platform journey
and three-step outward track use the existing dither background.
Use the existing dither background as an instance; do not change its source to animate one scene.
Animate its instance Wipe/drift slowly, overscan to cover edges, and time-remap longer instances so
the shorter background source remains visible. Resolve the existing Essential Graphics property
path with `props`/`essential.list`; control IDs are project-specific.
When a moving 3D backdrop is requested, put an oversized instance behind every card in world space,
with collapse off. Let camera travel create parallax rather than pinning the background to the frame.
Adjust instance Pixel Size for readable enlarged dithering, and project its corners through the
entire camera move to verify coverage. The three-step scene uses a 3000% plane at Z=6500 and blue paths.

## Preserve the saved edit

Back up the project and close the clean GUI normally before file-based changes. Preserve saved
opening/source comps. Do not run a clean whole-project rebuild over the user's saved project.

`comp.new` reuses an existing comp and skips its build block. For a targeted replacement, remove
only that generated source comp, rebuild its commands, and restore its instances/timing. In this
project, `assembleIntro1.jsx` restores type11 and the accepted Intro 1 sequence. New library scenes
can remain standalone until their placement is requested.

Generate JSON with non-ASCII characters escaped for the CLI's Windows command-file reader. Inline
CLI commands run before `--commands` files; put dependent operations in one ordered command file.
Maintain the generator, effect.json, template and dependency ordering together.

## Verify and hand back

Render entrances, holds, camera arrivals, largest overshoots and exits. Load wasm plug-ins and render
in the same CLI process (`effect.plugins.load` then `renderQueue.render`); a plain headless render
otherwise omits the real dither. Do not save QA render queue entries into the main project.

Compare preexisting project items against the backup, excluding only intentionally edited comps.
Export the changed `.ectemplate`. Close/reopen EffectCraft on the changed comp so the user can
review it. Do not commit or push unless requested.

The scene documents in `textAnimations/PLAY_JOURNEY.md` and `RESEARCH_DEPTH.md` record current
timings, sources, component names and renderer-specific checks.
