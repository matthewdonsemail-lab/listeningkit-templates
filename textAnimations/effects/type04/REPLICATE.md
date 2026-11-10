# Platform reel validation

The final type04 is a three-second, 1920 x 1080, 30 fps editable EffectCraft precomp. It lists
Twitter/X, Facebook, Discord, Slack, Instagram, Reddit and LinkedIn, sourced from log-cli's platform
registry. Logos are vendored Font Awesome SVGs with their license, recoloured ListeningKit blue.

The heading uses word-based position animation: 0.1-second stagger, 0.38-second top entrance with
overshoot, then a 0.32-second bottom exit beginning at 2.2 seconds plus each word's stagger.
Each rounded card scales in first, its logo starts two frames later, and its typewriter label starts
another two frames later. Cards measure completed text and animated bounds to contain the overshoot.

A top adjustment layer named Page push in uses the native Transform effect, centred at [960,540].
Across the duration, scale grows from 100% to 108% and rotation moves from 0 to -1.2 degrees.
The background is a warm white vector with faint blue and peach dot fields.

Validation performed during implementation:

- Rendered the full 90-frame sequence and inspected entrance, resting frames and staggered bottom exit.
- Inspected consecutive Facebook entrance frames to verify card, logo, then label, and container fit.
- Checked full-resolution text overshoot and page-transform midpoint frames.
- Evaluated adjustment effect properties at 1.5 seconds: 104% scale and -0.6 degree rotation.
- Exported type04.ectemplate with eight text controls and all required assets.
- Closed and reopened EffectCraft on type04 for user review; the resulting scene was accepted.
- Checked generator syntax and git diff whitespace before committing.

The motion is reconstructed from sampled Strawberry reference frames, then adapted to ListeningKit.
This is not a pixel-exact replica: platform content, logos and colours are intentional replacements,
and the dot background and easing are reconstructed. BEATS.md records the original reference roles;
MOTION.md documents the final reusable conventions.
