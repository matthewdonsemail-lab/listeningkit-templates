#!/usr/bin/env bash
# Builds textAnimations.ecproj from every effects/<name>/effect.json with the EffectCraft CLI,
# then writes each effect's <name>.ectemplate into its own directory.
# Add an effect: make effects/<name>/effect.json (a JSON array of CLI commands) and re-run.
set -euo pipefail
cd "$(dirname "$0")"
CLI="${EFFECTCRAFT_CLI:-/c/Program Files/ArtCraft/EffectCraft/effectcraft-cli.exe}"
PROJECT="textAnimations.ecproj"

# Precomps go first, in order: cloudBackground uses ditherGradientBackground, introCard uses cloudBackground.
first=(effects/ditherGradientBackground/effect.json effects/cloudBackground/effect.json)
args=()
for f in "${first[@]}"; do args+=(--commands "$f"); done
for f in effects/*/effect.json; do [[ " ${first[*]} " == *" $f "* ]] || args+=(--commands "$f"); done
"$CLI" --empty run "${args[@]}" --save-as "$PROJECT"
"$CLI" script nameControls.jsx "$PROJECT"

# Open on a light comp: close every comp tab (the heavy ones, like brickTextBackground, lag the viewer) and
# leave only typewriterOvershoot open.
close=()
for dir in effects/*/; do close+=(comp.close "{\"comp\":\"$(basename "$dir")\"}"); done
"$CLI" --project "$PROJECT" run "${close[@]}" comp.close '{"comp":"clayClouds"}' comp.open '{"comp":"typewriterOvershoot"}' --save

# Sort the Project panel into folders (Text Animations, Title Cards, Backgrounds, Agent Windows, Assets).
# A new template's comp needs adding to organize.json, or it stays at the top level.
"$CLI" --project "$PROJECT" run --commands organize.json --save

for dir in effects/*/; do
  name="$(basename "$dir")"
  "$CLI" --project "$PROJECT" exec essential.exportTemplate \
    --params "{\"comp\":\"$name\",\"path\":\"$(cygpath -m "$PWD")/effects/$name/$name.ectemplate\",\"name\":\"$name\"}"
done
