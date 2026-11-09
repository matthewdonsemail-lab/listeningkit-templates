# brickTextBackground notes

This is the original version: 60 same-size blue bricks in 8 rows, one random word each from the sentence, with
Build, Overshoot, Scramble, Scramble Every and Brick Color. Scramble is off by default.

## The heavier version, removed on 2026-11-10

A later version (commits c89d449 to 3ba8929) was too heavy to work with. It lagged and crashed EffectCraft and used up
the machine's memory, so it was taken out and this original was put back. It had:

- Smaller bricks: 126, then 208, then 72.
- A shade per brick, and a gradient across the wall run through Craft Halftone & Dither on every frame.
- Bricks that wrap their word: each brick as wide as its word plus padding, laid end to end in rows, with Zoom,
  Padding X/Y and Gap sliders.

What made it heavy:

- **Text measuring.** Each brick worked out its position by measuring every word before it in its row with
  `sourceRectAtTime`. That was about 500 text layouts every frame at 208 bricks. Measuring each word once into a
  slider got it down to 72, but it was still heavy.
- **The dither.** Craft Halftone & Dither ran over the whole frame on every frame.
- **Scramble with wrapping bricks.** Each word swap changed its brick's width, so the whole row reflowed and was
  measured again.
- **Layer count.** Two layers per brick, every one with expressions, plus the comp opening as the active comp.

If bricks that wrap their words come back, lay them out once instead of per frame. Either the build script
measures the words and writes fixed sizes and positions, or the layout is baked to keyframes. Keep the dither off
the bricks, and keep the brick count low.

The full heavy version is in the git history, in `textAnimations/typewriterVariations.mjs` at commit 3ba8929.
