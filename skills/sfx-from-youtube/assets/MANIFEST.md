# Assets for sfx-from-youtube

Everything this skill needs to run again, copied here at the same path it has in the repo. The scripts still use
their original paths, so run them from the repo, or point their path constants at this folder.

## Bundled here

- `youtube_sfx.sh` (new): search YouTube and download the picked packs as WAV
- `textAnimations/assets/make_sfx_cues.py`
- `textAnimations/assets/make_sfx_kit.py`
- `textAnimations/assets/make_sfx_from_music.py`
- `textAnimations/plugins/sfxCues.jsx`
- `textAnimations/plugins/sfxLay.jsx`
- `textAnimations/SFX_CUES.md`
- `textAnimations/sfx_cues.csv`

## Not copied: media (gitignored; rebuilt by the scripts above)

- `textAnimations/assets/sfx/raw/*.wav`: the 22 YouTube packs (deleted; rebuild with `youtube_sfx.sh get ...`)
- `textAnimations/assets/sfx/<kind>/NN.wav`: the kit (14 MB, local)
- `textAnimations/assets/sfx/film_with_sfx_preview.mp3`: the last listen sent to matt
- `projects/opening/ref/trailer_nodialogue.wav`: the trailer with its dialogue removed (the source for make_sfx_from_music.py)
