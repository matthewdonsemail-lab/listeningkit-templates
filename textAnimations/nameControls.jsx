// Names the slider controls in every comp, which the expressions read by name, then re-applies every
// layer's expressions so they pick up the new names. Run by build.sh.
//   Most comps: the "text" layer's sliders. A single slider (the preset effects) is Continuous Scale.
//   namesByLayer: comps with their own names per layer (cvBluekey, introCard).
var names = ["Letter Overshoot", "Pop Time", "Whole Overshoot", "Continuous Scale"];
var namesByLayer = {
  cvBluekey: { text: ["Continuous Scale", "Wobble", "Bob"] },
  introCard: {
    introducing: ["Letter Overshoot", "Pop Time", "Whole Overshoot", "Continuous Scale"],
    "listening kit": ["Letter Overshoot", "Pop Time", "Whole Overshoot", "Continuous Scale"],
    controls: ["Overshoot", "Pop Time", "Word Spacing", "Continuous Scale"]
  },
  // null in a list keeps that effect's own name.
  ditherGradientBackground: { controls: ["Wipe"] },
  cloudSolo: { controls: ["Overshoot"] },
  ascii3D: { controls: ["Density", "Ink", "Shade"] },
  blackHighlightFocus: { controls: ["Focus Blur", "Stagger", "Overshoot"] },
  tiktok: { controls: ["Overshoot", "Stagger"] },
  clayClouds: { controls: ["Overshoot", "Stagger"] },
  brickTextBackground: { controls: ["Build", "Overshoot", "Scramble", "Scramble Every", "Brick Color"] }
};

function reapply(group) {
  for (var j = 1; j <= group.numProperties; j++) {
    var p = group.property(j);
    if (p.numProperties !== undefined && p.numProperties > 0) reapply(p);
    else if (p.canSetExpression && p.expression) p.expression = p.expression;
  }
}

function nameSliders(layer, list) {
  var count = layer.property("Effects").numProperties;
  for (var k = 0; k < list.length && k < count; k++) if (list[k]) layer.effect(k + 1).name = list[k];
}

for (var i = 1; i <= app.project.numItems; i++) {
  var comp = app.project.item(i);
  if (!(comp instanceof CompItem)) continue;
  var byLayer = namesByLayer[comp.name];
  if (byLayer) {
    for (var layerName in byLayer) if (comp.layer(layerName)) nameSliders(comp.layer(layerName), byLayer[layerName]);
  } else {
    var layer = comp.layer("text");
    if (!layer) continue;
    var count = layer.property("Effects").numProperties;
    nameSliders(layer, count == 1 ? ["Continuous Scale"] : names);
  }
  for (var l = 1; l <= comp.numLayers; l++) reapply(comp.layer(l));
}
app.project.save();
