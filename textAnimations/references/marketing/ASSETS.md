# Marketing component study

Captured from the local Log marketing source on 2026-11-12. The public listeningkit.com homepage
currently has a different agency layout, so the reference is the existing Log worktree served locally.

Source: sibling repo `log-cli/.claude/worktrees/site-mcp-promo-452719/site/apps/web`.

| Capture | Component | Useful motion treatment |
| --- | --- | --- |
| [Built-with strip](built-with.png) | LandingPage.tsx | Treg/SubQ roles, compact service badges, blue-to-white gradient |
| [Platform demonstration](platforms.png) | PlatformSuite.tsx / PlatformDemos.tsx | Complete card precomp, selected conversation pulls forward |
| [Agent workflow](agent-workflow.png) | useCases/HowItWorks.tsx | Prompt → play steps → delivered result, staged through Z |
| [Research story](research-story.png) | useCases/ReaLooksmaxxingPage.tsx / platformStories.tsx | Context retrieval → selecting useful formats → action |

The research story capture includes the site's black video surface where external media was not
playing. The workflow capture shows its progressive reveal with later steps blurred, plus the site's
MCP promotion. Reuse the hierarchy, copy and panel geometry; do not reproduce these loading/reveal
states or the promotional overlay. `component-overview.png` pairs the clean built-with/platform views.

Additional native motion candidates from the inspected source:

- Incoming post cards: stagger a few full post precomps through depth, then frame the relevant post.
- Classification table: scan through rows, mark match/skip, collapse into a useful shortlist.
- Conversation: preserve the thread as one 2D panel and pull one actionable reply forward.
- Play execution: terminal request, tool context, decision, completed action. Use complete panels
  at successive depths rather than making every UI atom a separate 3D layer.

The first implemented study is `logResearchDepth`, with four native source precomps, a dedicated
Hermes Agent terminal, provider badges, matching rows and a shortlist. The revised camera uses
anticipation and follow-through, and white connections draw/clear with the handoff.
See `../../RESEARCH_DEPTH.md`.
