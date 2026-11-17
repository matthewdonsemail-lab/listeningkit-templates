# Website steps on an outward track

`logThreeStepsTrack` is a standalone 9-second / 270-frame composition at 30 fps. It lives in
Product Demos, with its editable source precomps in Three-step components. The accepted research
scene and Intro 1 sequence are preserved.

The source is the sibling log-cli worktree
`.claude/worktrees/site-mcp-promo-452719/site/apps/web/src/landing/useCases/HowItWorks.tsx`.
Its three cards are **Ask your agent**, **log writes and runs the play**, and **It lands on Discord**.
The five tool calls and example result rows come from `DISCORD_PLAY.how` in `platformPages.ts`.
The agent identity is Hermes, using the existing frozen Hermes mark. Discord uses the existing
platform SVG. These are native editable reconstructions of the website components.

| Card | Source | Position X / Y / Z | Focus |
| --- | --- | --- | --- |
| Step 1 | stepsCard1 | 360 / 540 / 0 | 0.70 s |
| Step 2 | stepsCard2 | 2160 / 540 / -2800 | 3.70 s |
| Step 3 | stepsCard3 | 360 / 540 / -5600 | 6.70 s |

The layout stays at one eye level, alternating between two X positions along an outward Z track.
The physical camera Z retreats continuously, from -2300 to about -11483 by the final rendered frame.
Native camera Zoom supplies the longer visual pushes while that outward dolly continues. The
camera yanks wide between the long pushes, with broad pre/post pans and a small roll. A natural
cubic spline connects the look target, lens magnification, orbit and roll with continuous velocity
and acceleration. Sparse poses replace the former rapid zoom/roll reversals around each arrival.
The outward Z surges use quintic ramps, keeping acceleration continuous at their boundaries too.
The final pullback continues panning left along the retreating track.

All three arrivals share an analytic damped spring from 40% toward 92%, with a broad overshoot
around 103%, restrained squeeze/stretch and a small matching rotation. It avoids the former cluster
of short keyed reversals. Future panels reveal after the camera has passed their Z planes.
Complete-card opacity remains 100%. Each exit anticipates by growing, then collapses to zero over
0.68 seconds: Step 1 at 3.52–4.20, Step 2 at 6.52–7.20 and Step 3 at 8.15–8.83 seconds.
No complete-card fade is used. Each brand-blue connection draws toward the next
card with Trim Paths End, then clears with Start. Connections appear only after the camera has
retreated behind their full depth range, avoiding near-plane stroke flares.

Each `stepsCard` is a complete flat component: blue gradient carrier, wide product demo, Step N,
title and supporting copy. Source internals are all 2D. Each outer instance is one 3D precomp with
collapse off, anchored at [600,650]. No external heading or decorative satellite logos are added.
The background is a 3000%-scale 3D instance of the existing `ditherGradientBackground`, placed at
world Z=6500 behind the entire track. Its world position drifts slowly around [1150,540,6500], so
camera pans, pushes and pullbacks move through its texture with real perspective and parallax.
The instance uses Pixel Size 5 to keep the enlarged dithering readable, and Wipe remains
61 + 4 sin(time × 0.32). Its original source is unchanged. Both handoff paths use opaque brand blue
#2A8CFF; their existing Trim Paths timing is retained.

Step 1 types the request, then staggers the Hermes reply and tool chip. Step 2 writes the real five
Discord calls into `play.ts`, scales the code out while sliding the running-play UI in with overshoot,
and checks off the five rows during the
focus window. Step 3 staggers the website's Who / What log did / Status rows and Discord footer.
Text and the complete-card framing are exposed through Essential Graphics.

`threeStepsTrack.mjs` generates `effects/stepsTrackParts/effect.json` and
`effects/logThreeStepsTrack/effect.json`. Build `ditherGradientBackground` and `stepsTrackParts` before the
scene. The main generator, clean-build order and project organization include both new templates.
For saved-project edits, build only these new comps; do not clean-build over the user's edit.

Validation: render all 270 frames; inspect each arrival, the extended pushes, wide swings and exit;
sample the native camera Position at all 270 frames to confirm Z strictly retreats; confirm every
source is 2D and each complete-card instance is 3D with collapse off; compare every preexisting
project item against the backup, excluding only the scene and `stepsPlayDemo` deliberately edited
for this refinement. Load the Craft plug-ins and render in the same process to include the real
dither. Do not save QA render queue entries in the project. Export both
templates and reopen EffectCraft on `logThreeStepsTrack` for review.

The initial 270-frame native review established the 2D source / 3D instance structure and preserved
all 415 earlier project items. The current refinement retains those components and instances.
Handoff 1 End still advances 0% → 49.074% → 100% at 2.85, 3.25 and 3.67 seconds; Start clears
between 3.80 and 4.35 seconds. The authored camera spline's maximum velocity/acceleration mismatch
at segment boundaries is below 1e-12. Verify the revised native render and Z travel after changes.

The revised 270-frame render includes the real Craft dither. Native sampling confirms opacity 100%
for every complete card on every frame, strictly outward Z travel (3.667–152.780 units per frame),
and scale exits of approximately 92% → 102.14% → 0% for all three cards. Only `logThreeStepsTrack`
and `stepsPlayDemo` changed; the other 425 saved project items match this refinement's backup.

The subsequent background pass rendered all 270 frames with the enlarged 3D dither and blue paths.
Native projection checks place all four frame corners inside the background plane on every frame,
with at least 241 screen pixels of coverage margin. Only `logThreeStepsTrack` changed in this pass;
the other 426 saved items, including the dither source and all component precomps, are unchanged.
