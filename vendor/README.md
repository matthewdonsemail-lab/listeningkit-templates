# Vendored

Third-party code kept here so the repository carries its own tooling.

## `rea-video/`

[rea-video](https://github.com/JuneYaooo/rea-video) by JuneYaooo — reverse-engineers a video shot by shot: was it
filmed, AI-generated, 3D or built in code, how each shot is lit and cut, and a remake plan.

- Upstream commit: `356815c` (2026-11-09)
- Licence: see `rea-video/LICENSE` and `rea-video/NOTICE`
- The skill is installed for agents at `.claude/skills/rea-video/` (the same `SKILL.md` as
  `rea-video/skills/rea-video/`).
- **Dropped on purpose:** every binary in `rea-video/docs/` (`.gif`, `.png`, `.jpg`, `.webp`) and every `.mp4`,
  `.mov`, `.webm` — the demo reels and report images upstream ships, about 80 MB. The markdown docs that matter are
  all here; pull the images from upstream if a page needs them.

Run it with `bash vendor/rea-video/scripts/install_skill.sh` (installs the `rea-video` CLI) or
`python -m rea_video --help` from inside `vendor/rea-video`.
