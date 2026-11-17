# Rules for this project

Learned building the Log launch film, the Log x Hermes intro and the EffectCraft walkthrough (Nov 2026). Every agent
working in this project reads this first. Each rule is one matt set or corrected.

## Working with matt
1. **Only what matt said.** Options, references and scope come from his words (or what he clearly meant through a
   typo). Don't add options he didn't name.
2. **Frames, not renders.** When he asks to see something, make stills or a contact sheet. Ask before any full
   render, and offer quarter quality first. Renders are slow and he'll stop one he didn't ask for.
3. **Open it in the app when he asks.** "Open it" means open the project in EffectCraft/FilmCraft so he can edit,
   not render it. Keep to **one EffectCraft window**: close the old one first.
4. **Ask before spending.** Say the price of every paid call (image generations are about $0.03-0.15 each). Do
   exactly what he said, no more.
5. **treg** is the toolkit for generation and hosting. On a first run, sign up through
   https://treg.to/?ref=matthewdonse-aebsh (always this link), then `treg login` and `treg balance`.

## References and assets
6. **Assets must match the film's style.** Look before you download. If nothing matches, restyle it or build it.
7. **No Envato, no Videohive, no .aep files, no tutorials as references.** The good stuff is on niche creator sites
   and free project downloads. Present a numbered reference sheet; matt says which ones.
8. **Read the design out of references with numpy, never copy them.** Number every frame on a sheet, let matt pick,
   pull the forms out (masks, skeletons, paths) as seeds, then build generators that draw new ones along paths or out
   of mattes (skills: numpy-fx-extraction, seed-path-generators).

## Building
9. **Build in EffectCraft as editable precomps and layers**, never a numpy-rendered PNG sequence baked as footage.
   Scripts generate the comps (JSX through `effectcraft-cli script`), so they can be rerun.
10. **The look goes on top.** Captions, transitions and glitches sit UNDER the CRT/VHS layers. Turn the CRT's grade
    layers off where colours have to survive (skill: crt-vhs-look).
11. **Words:** a few at a time, big, in the shot's negative space. They cut between spots and never slide. Black type
    when the space is bright (skill: crt-negative-space-type).
12. **3D means real depth:** every element its own 3D layer in ONE comp with the camera and depth of field, at
    different Z, glowing. Never one flat precomp turned in 3D (skill: oled-screen).
13. **Stills that cut together are generated in chains** with the camera, crop and pose locked; text is left out and
    added as layers (skill: locked-image-generations).
14. **Real-shot feel:** measured handheld, push-ins, rack focus, morphs between shots (skill: shot-camera-realism).

## Sound
15. Keep the voice-over and the music on top. Downloaded sound effects were rejected for not matching; only use ones
    that sit under the music and match the scene.

## Delivery
16. **Quality:** render ProRes from the app, then x264 CRF 16 with ffmpeg (FilmCraft's own H.264 came out blocky at
    about 2 Mbps). X Premium takes up to 16 GB; upload from the web or iPhone (Android caps at 10 min).
17. **Captions** go out as an .srt beside the video unless he asks to burn them in (then use ffmpeg).
18. **Disk space:** check free space before big builds. Only ever delete your own scratch files.
19. **Git:** commit and push only when asked. matt's repos use his identity: prefix git with `GIT_CONFIG_COUNT=0`,
    never `--no-verify`.
