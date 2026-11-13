# Commentary, exposition and visual bridges

The film explains the premise under spoken commentary. Full-screen typography carries the main
thought. Brief footage or concept sequences bridge those thoughts and make the idea visible.
The opening already contains the saved `HermesGirl.mp4` montage and its grading. Preserve it.

The useful editorial pattern is:

**Short montage / visual hook → full-screen premise → brief concept in motion → next full-screen
statement → demonstrated outcome → closing position.**

Choose each insert from the sentence being spoken and the viewer's goal. A platform interface is
useful only when its action needs to be understood. A recreated dashboard is not the default
explanation. Prefer the idea: a conversation needs a reply, context reaches Hermes, one request
becomes several completed actions, a result lands. The existing 3D scenes supply reusable visual
parts; use the relevant beat rather than showing every precomp at full length by default.

## Exposition shots

- Make one readable thought fill the frame. Use large navy Satoshi and one Schoolbell blue highlight.
- Keep the layout stable. Reveal words or short phrases with the commentary, then let the completed
  thought hold. Avoid animating continuously just because a shot is motion graphics.
- Track the spoken words with editable timing cues. Keep their settled positions fixed so a newly
  appearing word does not recenter the sentence or change its line breaks.
- Use a quiet 2% page push and restrained ear drift. Save the large swings and depth moves for the
  conceptual transition. The contrast between quiet reading and a short moving insert creates pace.
- Keep dither behind the message or on supporting footage. Preserve a clear reading field.
- Exit by anticipating slightly larger and scaling out. Keep complete-asset opacity at 100%.
- End on a clear exposition or result frame. The viewer should understand what changed.

## Positional assets

Build the composition from independent editable parts: text block, ear frame, background, and
optional subject footage or concept insert. The ears are anchored edge accents, cropped around
the statement with slow drift; they do not orbit the copy. This makes it possible to change the
shot, track a spoken phrase or reposition an accent without rebuilding a whole website section.

The website references are local log-cli sources:

- `site/apps/web/src/landing/Control.tsx`: large Satoshi statement, Schoolbell category, oversized
  ears at the edges and dither behind the reading field.
- `site/apps/web/src/landing/ListeningIntro.tsx`: the premise that potential customers are talking
  about a problem on social media; typography dominates while background material provides context.
- `site/apps/web/public/images/ears/ear1.webp` through `ear8.webp`: the actual existing ear artwork.

The source checkout is `../log-cli/.claude/worktrees/site-mcp-promo-452719`.
The eight ear assets are frozen in `assets/exposition`; the native study uses four edge accents.

## First native study

`expositionStudy` is a standalone nine-second typography study in Title Cards / Exposition:

| Time | Precomp | Website statement |
| --- | --- | --- |
| 0–5 s | expositionPremise | Your (potential) customers are moaning about something on social media. |
| 5–9 s | expositionPositioning | The best tool for social media marketing. |

Both plates use the reusable transparent `expositionEars` precomp. Their copy remains editable in
Essential Graphics. Each line has a **words** marker: move it to the spoken phrase, and stretch its
duration to spread the word reveals. Word visibility cuts on without a fade or a layout shift. A
composition **out** marker controls the whole text/ear scale-out. The study's current timing is a
provisional reading rhythm; no voiceover recording has been supplied or claimed to be synchronized.

This is a library study for judging the exposition style. It does not replace the saved intro,
change the accepted 3D camera scenes, or determine the final commentary. The final sequence should
be assembled against the actual voiceover, choosing only the visual beats that support its meaning.

`expositionCards.mjs` generates the four native command files. Build ditherGradientBackground,
expositionEars and both typography plates before expositionStudy. Export each matching template.
Render the actual dither with Craft plug-ins loaded in the render process; inspect word reveals,
the full-sentence hold, cropped ear bounds and overshoot scale-outs. Reopen EffectCraft on the study.

The native review rendered all 270 frames, including real dither, progressive word reveals,
completed reading holds and scale-outs. All 427 preexisting project items match the saved backup;
the four exposition comps and their imported ear assets are additions. The original Hermes opening,
Intro 1 assembly and accepted 3D scenes remain intact.
