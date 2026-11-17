# Terminal, context, decision, shortlist

`logResearchDepth` is a standalone editable eight-second composition at 30 fps. It is available
in Product Demos; its four component precomps live in Research components. The accepted Intro 1
sequence remains 20.7667 seconds, with the revised type11 in its existing slot.

| Stage | Source precomp | World position X / Y / Z | Camera arrival |
| --- | --- | --- | --- |
| Ask once | researchTerminal | 960 / 540 / 0 | 0.50 s |
| Treg source context | researchSources | 2740 / 140 / 850 | 2.25 s |
| SubQ checks the fit | researchDecision | 1280 / 1640 / -380 | 4.25 s |
| Shortlist for Hermes | researchShortlist | 3380 / 1150 / 1100 | 6.25 s |

The panels form a staggered spatial layout. The camera follows one time-aware Hermite spline with
continuous velocity across authored poses. Before each departure it anticipates away from the next
panel, then pulls back into a curved diagonal pan, rotates slightly through the push-in, continues
past the arrival and rebounds. Small drift/orbit connects the focus and anticipation poses. The final
move pulls back and pans out. `researchCameraPoses()` authors the poses rather than restarting a
separate easing function for each axis at each stop.

All four panels use the same focus spring: 70 → 108 → 89 → 94 → 92 percent. The peak lands 0.025
seconds after camera arrival. Paired squeeze/stretch and a small rotational rebound use the same
timing for every panel. The scale anchor is the visible panel centre [700,550]. Internal row pops
settle within the shell; their backgrounds no longer overshoot beyond the panel border.

`brandBlueGradient` is the reusable background: a 12-second native Gradient Ramp with Light blue
and Deep blue Essential Graphics controls and slow gradient-point motion. This scene uses that smooth
blue background and white 3D connections. External context headings have been removed. Source panels
remain entirely 2D, with staggered row pops and their own functional UI titles.

Each connection draws from the active panel toward its destination: Trim Paths End goes 0 → 100
from 0.18 seconds before departure to 0.04 seconds before arrival. Trim Paths Start then goes 0 → 100
from arrival +0.10 to +0.64, clearing the tail into the destination. Offset stays zero. No persistent
full rail or endlessly cycling dash is used. Endpoints lie beneath the panel surfaces so the curves
emerge from and land in the actual UI panels.

`researchTerminal` embeds the reusable native `hermesAgentTerminal` precomp, with the approved Hermes
mark, Hermes Agent chrome, a typed prompt, Treg tool output and the SubQ handoff. This is a dedicated
2D agent terminal; it does not depend on the Claude Code terminal. The original terminal source and
its other instances are unchanged. The prompt is
“Find growth leaders at Series A startups in SF.” Treg supplies source context; SubQ illustrates a
matching pass; a shortlist retains the reasons for each match. This is illustrative data, not a live
query or an assertion that these people, roles or matching decisions are current.

Source references:

- Sibling repo `treg-hyperframes/compositions/terminal.html`: terminal-to-provider reveal.
- `treg-hyperframes/compositions/routing.html`: provider chips and people rows.
- `treg-hyperframes/compositions/qualify.html`: scanning, match/skip rows and filtering.
- `treg-hyperframes/compositions/leads.html`: names, roles and contextual shortlist.
- log-cli worktree `site/apps/web/src/landing/LandingPage.tsx`: Treg/SubQ roles and blue styling.
- `landing/useCases/ReaLooksmaxxingPage.tsx`: Treg finds context, SubQ selects useful results.

The Treg mark and provider PNGs come from treg-hyperframes. SubQ's SVG comes from the Log marketing
assets. The Treg mark uses separate solid shapes, avoiding the SVG-mask rendering issue seen with
the site's knockout icon. Tint preserves its white detail. Assets are frozen in `assets/research`.

Build `hermesAgentTerminal` and `brandBlueGradient`, then `researchParts`, then `logResearchDepth`.
`researchDepth.mjs` generates their command files; the main generator and clean-build dependency
order include them. Do not clean-build over the saved project. This smooth scene needs no dither
plug-in. Other comps that use dither still require plug-ins loaded in the rendering process.

The reusable local skill is `skills/effectcraft-motion/SKILL.md` at the repository root, also installed
in the user's Codex skills directory. Marketing captures and component candidates are documented in
`references/marketing/ASSETS.md`.

Verify the complete 240-frame blue-background render, anticipation/wide views, arrival scale peaks,
post-pan rebound, line draw/clear and final pullback/pan. Check that each source component has no 3D
internal layers and each outer panel has collapse off. Compare against the saved project backup to
preserve unrelated scenes and the original terminal.

The latest pass rendered all 240 frames and checked the four focus peaks: each evaluates to the
same 105.746% X / 110.254% Y after squeeze/stretch. Native Trim Paths checks confirm End advances
from 0 to 100 during the handoff and Start clears the tail afterward. The scene dependency graph
contains `hermesAgentTerminal` and no Claude Code/Codex terminal source. Unrelated project items
match the pre-change backup after export.
