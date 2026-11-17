# Quick platform-play camera edit

The tongue cards remain complete 2D precomps imported as seven separate 3D objects. The camera
travels X → Slack → Discord → Instagram → Reddit → Facebook → LinkedIn, using their distinct Z depths.
The client still slides up through its fixed mask behind the foreground tongue. No satellites.

The journey is now 8 seconds / 240 frames at 30 fps, reduced from 32.6 seconds. The current edit grid
is 120 BPM: one platform per two beats. No music track has been supplied; these are editable timing
marks, not a claim of synchronization to a soundtrack. Align the grid phase/tempo when music is added.

| Play | Camera arrival | Next pan begins | Whole-card entrance |
| --- | --- | --- | --- |
| Hermes / X | 0.5 | 1.0 | 0.0 |
| Slack | 1.5 | 2.0 | 1.1 |
| Discord | 2.5 | 3.0 | 2.1 |
| Instagram | 3.5 | 4.0 | 3.1 |
| Reddit | 4.5 | 5.0 | 4.1 |
| Facebook | 5.5 | 6.0 | 5.1 |
| LinkedIn | 6.5 | 7.5 | 6.1 |

Each pan takes one beat. The camera overshoots along the travel direction and through the focal
distance, then rebounds with a short damped spring. Whole-card scale starts 0.18 seconds before
each camera arrival and settles 0.22 seconds after it. The approximately 115% peak lands just after
arrival, while the camera can see it. Resting scale is 92%, leaving safe room for the relative 115%
bounce and camera rebound. A horizontal squeeze / vertical stretch releases into normal
proportions; a second small compression responds to the camera hit. The opening card pops over
0–0.48 seconds. Small position drift and camera dolly keep the holds moving.
Nested previews run at 3.8x so their masked reveals, typing and media states complete during the hit.

The background is an instance of the existing ditherGradientBackground. Its instance Wipe slowly
breathes as `61 + 5*sin(time*0.48)`; 106% scale gives the subtle position drift safe edge coverage.
The instance expression targets the existing Wipe control `essential/eg149`. Its original keyframes,
source layers and other instances are unchanged. Native
plug-ins must be loaded for headless rendering; otherwise the ramp displays without its dither.
The command file loads the installed plug-ins. Keep that load in the same process as renderQueue.render.

Two curved blue routes connect each adjacent pair of card positions. These are native 3D shape
layers behind the cards, with Y rotation matching the route's change in Z depth. Faint full-length
rails carry short Trim Paths strokes moving at 160 degrees per second. They share the actual camera
perspective and parallax; they are not a screen overlay. All card internals remain in their 2D sources.

Intro 1 retains its saved opening, introCard, type11 and type04. The journey runs from 12.7667 to
20.7667 seconds. The comp and work area end there; the legacy grading layer ends at the journey start so only the background is dithered. The previous
four separate demo comps remain in the library. Their instances are absent from the current edit.

Sources are log-cli's local worktree: pages/console/ConnectionsPage.tsx, PlatformConnectionTongue.tsx
and landing/PlatformDemos.tsx. The opening uses the approved /start Hermes/X card. Facebook retains
the actual listingClearOut.webp image from the source. Build startCardParts, connectionCardParts,
then logPlayJourney. Stop geometry, timing and camera expressions live in connectionPlays.mjs.

Verified the 240-frame motion render, camera arrival/squeeze frames, the loaded dither plug-in output
and the shortened Intro 1 range. Project comparisons preserve all existing items except Intro 1 and
logPlayJourney. Templates are exported under effects/logPlayJourney; EffectCraft opens on the Slack hit.
