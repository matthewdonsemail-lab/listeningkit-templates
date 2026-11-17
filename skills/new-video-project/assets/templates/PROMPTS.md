# Prompts for {{NAME}}

Ready-to-use prompts, one per stage, in the order the launch film was built. Each one names the skill to load
(`skills/<name>/SKILL.md` in listeningkit-templates) and points at this project's folders. Fill in the brackets, then
paste. Every prompt assumes the agent has read `RULES.md` and `BRIEF.md` first.

## 0. Kick-off
> Read `projects/{{NAME}}/RULES.md` and `BRIEF.md`. Summarise the brief back to me in five lines: what the video is,
> its length, the music/VO, the look, and what I've said I want in it. Don't add anything I didn't say. Then list the
> stages from `PROMPTS.md` that this video needs.

## 1. References
> Load the `numpy-fx-extraction` skill. Download these references into `projects/{{NAME}}/ref/`: [links]. Make a
> numbered frame sheet of each in `ref/sheets/` and show me them. I'll tell you the frame numbers I like.

> Load `seed-path-generators`. From frames [numbers] of [reference], pull the line/shape forms out with numpy as
> seeds into `assets/seeds/`, and show me a sheet: the reference frames, the seeds, then 3 new generated variations.

## 2. Stills
> Load `locked-image-generations`. Generate [the first anchor shot: a cast sheet / the main character standing] from
> [references]. Say the price first. Once I approve it, generate [the shots] with it as the reference, camera and
> crop locked, no text in the pictures. Write the prompts into `gen/prompts.py` and the images into `gen/`.

> Make [N] style versions of [shot] ([styles]) with the camera, crop and pose locked, so they glitch in place.

## 3. Screens and UI
> Load `screen-ui-typing`. Build the [ChatGPT / app] screen as live text and shapes in EffectCraft, the prompt typing
> "[text]" at [speed], filmed in 3D with depth of field in [reference]'s monitor look. Show me 4 stills.

## 4. The shots
> Load `shot-camera-realism`. Give every shot in the [section] a real-camera feel: handheld measured from
> [reference], slow push-ins, and morph [shot A] into [shot B]. Show me a strip of frames across the morph.

> Load `grade-and-thermal-cuts`. Grade the shots: [look A] on [shots], [look B] on [shots]. Put the thermogram flash
> on [the scene switches / the drop at mm:ss:ff]. Show me before/after stills.

## 5. The big moment
> Load `cyberpsycho-cut` and `eye-echo`. From [mm:ss:ff] (the drop), take [the two people] into [the look] over 12
> steps each, cut them off the background, and glitch-cut them against each other on the beat, with the eye echo.
> Frames first.

## 6. Cuts and type
> Load `glitch-cut-transitions`. Put the transitions on every cut in [section]: shot A running past the cut, B in
> early, the blends, a pixel-sort burst, all under the CRT. Show me one cut taken apart frame by frame.

> Load `crt-negative-space-type`. Put the VO on screen: a few big words at a time in each shot's empty space, cutting
> between spots, never moving, black when the background is bright. Random letters swap to the 8-bit font. Stills.

## 7. The look
> Load `crt-vhs-look`. Put the VHS look and 4:3 bars on [section] and the CRT from [mm:ss:ff]. Captions and
> transitions stay under it. Show me a close-up still of the CRT and one wide.

## 8. Ending and sound
> Load `end-card-and-outro`. End on [logo A], then [logo B] wrapped in lines, then both side by side. Stutter the
> music's last phrase into a reverb tail so it doesn't stop dead. Leave breathing room.

## 9. Delivery
> Render it in quarter quality so I can watch it. [After I say yes:] Render the full version: ProRes from the app,
> then x264 CRF 16, AAC 320k. Put the .srt beside it. Tell me the file size, length and bitrate.

## 10. Write it up
> Rebuild the process board for this project (`textAnimations/assets/make_process_board.py` is the template) and
> update any skill this video taught us something new about, with pictures.

## Talking-head edits
> Load `filmcraft-talking-edit`. Cut [recording] into a [length] walkthrough in FilmCraft: clean the voice, keep
> whole sentences, cut pauses over 0.30 s, 8-frame J-cuts, close-ups on talking sentences, and cut in [inserts] where
> I talk about them.
