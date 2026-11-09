// Writes effects/<name>/effect.json for each typewriter variation.
// Every variation scales each unit from 0 to full size from its own centre (anchor centred), past
// full size and back (overshoot), and out again the same way. No fades. Run: node typewriterVariations.mjs
//
// Timing is driven from the text layer's markers:
//   "in"  marker — where the type-on starts; its duration is how long until the last unit has landed.
//   "out" marker — where the type-off starts; its duration is how long until the last unit is gone.
// The whole text also scales from 0 to full size around its centre over each marker's duration,
// with its own overshoot, on top of the letters.
// Slider controls on the layer (also in Essential Graphics):
//   Letter Overshoot — how far past full size each unit goes (0 = none).
//   Pop Time         — seconds for one unit to scale in or out.
//   Whole Overshoot  — how far past full size the whole text goes (0 = none).
//   Continuous Scale — (continuousScale only) % the whole text keeps growing per second from the
//                      "in" marker on (0 = none, negative shrinks).
import { mkdirSync, writeFileSync } from "node:fs";

const variations = {
  typewriterOvershoot: { in: [0, 0.6], out: [3, 0.5], pop: 0.25, overshoot: 2, whole: 1.7, continuous: 6 },
  typewriterOvershootFast: { in: [0, 0.35], out: [3, 0.3], pop: 0.16, overshoot: 2.6, whole: 2, continuous: 6 },
  typewriterOvershootWords: { in: [0, 0.4], out: [3, 0.35], pop: 0.28, overshoot: 2, whole: 1.7, words: true, continuous: 6 },
  typewriterOvershootRotate: { in: [0, 0.6], out: [3, 0.5], pop: 0.28, overshoot: 2, whole: 1.7, rotation: -20, continuous: 6 },
  continuousScale: { in: [0, 0.6], out: [3, 0.5], pop: 0.25, overshoot: 2, whole: 1.7, continuous: 6 },
};

// The built-in preset effects get the Continuous Scale slider too (growing from the start of the comp).
const presets = { typewriter: 6, fadeUpCharacters: 6 };

// The cv-bluekey look, on every effect: Schoolbell in brand blue #2a8cff, a white outline inside a dark
// navy #0d2a4c outline (text stroke + Stroke layer style), tilted -3°, blue Outer Glow.
const bluekeyText = { fill: [0.165, 0.549, 1], stroke: [1, 1, 1], applyStroke: true, strokeWidth: 18, strokeOverFill: false };
const bluekeyStyleSteps = () => {
  const set = (path, value) => ({ command: "prop.set", params: { layer: "text", path, value } });
  return [
    { command: "layer.style.stroke", params: { layers: ["text"] } },
    set("layerStyles/stroke/color", [0.051, 0.165, 0.298, 1]),
    set("layerStyles/stroke/size", 5),
    { command: "layer.style.outerGlow", params: { layers: ["text"] } },
    set("layerStyles/outerGlow/blendMode", 0),
    set("layerStyles/outerGlow/color", [0.165, 0.549, 1, 1]),
    set("layerStyles/outerGlow/opacity", 55),
    set("layerStyles/outerGlow/size", 28),
  ];
};
// Gives a step list the cv-bluekey look: colours on the text, layer styles right after it, and the -3° tilt.
function withBluekey(steps) {
  const at = steps.findIndex((s) => s.command === "layer.newText");
  steps[at] = { ...steps[at], params: { ...steps[at].params, ...bluekeyText } };
  steps.splice(at + 1, 0, ...bluekeyStyleSteps(), { command: "prop.set", params: { layer: "text", path: "transform/rotation", value: -3 } });
  return steps;
}

const presetScaleExpression = [
  `var cs = 0; try { cs = effect("Continuous Scale")("Slider"); } catch (e) { cs = 0; }`,
  `var s = Math.max(1 + (cs / 100) * Math.max(time - inPoint, 0), 0);`,
  `[100 * s, 100 * s, 100]`,
].join("\n");

const presetAnchorExpression = [
  `var r = sourceRectAtTime(thisComp.duration - thisComp.frameDuration, false);`,
  `[r.left + r.width / 2, r.top + r.height / 2, 0]`,
].join("\n");

const amountExpression = [
  `var ov = effect("Letter Overshoot")("Slider"), pop = Math.max(effect("Pop Time")("Slider"), 0.001);`,
  `function markerKey(name) { try { return thisLayer.marker.key(name); } catch (e) { return null; } }`,
  `function clamp(t) { return Math.min(Math.max(t, 0), 1); }`,
  `var n = Math.max(textTotal, 1), i = textIndex - 1;`,
  `function progress(m) {`,
  `  var p = Math.min(pop, m.duration > 0 ? m.duration : pop);`,
  `  var gap = n > 1 ? Math.max(m.duration - p, 0) / (n - 1) : 0;`,
  `  return clamp((time - m.time - i * gap) / p);`,
  `}`,
  `function backOut(t) { var u = t - 1; return 1 + (ov + 1) * u * u * u + ov * u * u; }`,
  `function backIn(t) { return (ov + 1) * t * t * t - ov * t * t; }`,
  `var mIn = markerKey("in"), mOut = markerKey("out");`,
  `var s = mIn ? backOut(progress(mIn)) : 1;`,
  `if (mOut && time >= mOut.time) s = 1 - backIn(progress(mOut));`,
  `var a = 100 * (1 - s);`,
  `[a, a, a]`,
].join("\n");

// The whole layer: scale over the full marker duration, anchor kept at the text's centre.
const wholeScaleExpression = [
  `var ov = effect("Whole Overshoot")("Slider");`,
  `function markerKey(name) { try { return thisLayer.marker.key(name); } catch (e) { return null; } }`,
  `function progress(m) { return Math.min(Math.max((time - m.time) / Math.max(m.duration, 0.001), 0), 1); }`,
  `function backOut(t) { var u = t - 1; return 1 + (ov + 1) * u * u * u + ov * u * u; }`,
  `function backIn(t) { return (ov + 1) * t * t * t - ov * t * t; }`,
  `var mIn = markerKey("in"), mOut = markerKey("out");`,
  `var s = mIn ? backOut(progress(mIn)) : 1;`,
  `if (mOut && time >= mOut.time) s = 1 - backIn(progress(mOut));`,
  `var cs = 0; try { cs = effect("Continuous Scale")("Slider"); } catch (e) { cs = 0; }`,
  `s *= Math.max(1 + (cs / 100) * Math.max(time - (mIn ? mIn.time : 0), 0), 0);`,
  `s = Math.max(s, 0);`,
  `[100 * s, 100 * s, 100]`,
].join("\n");

// Measured once the text has landed, so the letters' own scaling does not move the anchor.
const centredAnchorExpression = [
  `var m; try { m = thisLayer.marker.key("in"); } catch (e) { m = null; }`,
  `var r = sourceRectAtTime(m ? m.time + m.duration + 0.5 : time, false);`,
  `[r.left + r.width / 2, r.top + r.height / 2, 0]`,
].join("\n");

const animator = "text/animators/animator";

for (const [name, v] of Object.entries(variations)) {
  const set = (path, value) => ({ command: "prop.set", params: { layer: "text", path, value } });
  const steps = [
    { command: "comp.new", params: { name, width: 1920, height: 1080, frameRate: 30, duration: 4, background: "#FAF7F0", open: true } },
    { command: "layer.newText", params: { text: "listening kit", name: "text", position: [960, 540], font: "Schoolbell", style: "Regular", size: 160, fill: [0.07, 0.07, 0.07], justify: "center" } },
    { command: "effect.apply", params: { effect: "Slider Control", layers: ["text"] } },
    { command: "effect.apply", params: { effect: "Slider Control", layers: ["text"] } },
    { command: "effect.apply", params: { effect: "Slider Control", layers: ["text"] } },
    set("effects/#1/slider", v.overshoot),
    set("effects/#2/slider", v.pop),
    set("effects/#3/slider", v.whole),
    ...(v.continuous !== undefined
      ? [{ command: "effect.apply", params: { effect: "Slider Control", layers: ["text"] } }, set("effects/#4/slider", v.continuous)]
      : []),
    { command: "layer.addMarker", params: { layers: ["text"], time: v.in[0], comment: "in" } },
    { command: "layer.addMarker", params: { layers: ["text"], time: v.out[0], comment: "out" } },
    { command: "markers.set", params: { layer: "text", index: 0, duration: v.in[1] } },
    { command: "markers.set", params: { layer: "text", index: 1, duration: v.out[1] } },
    { command: "layer.addTextAnimator", params: { layer: "text", properties: ["scale", ...(v.rotation ? ["rotation"] : [])], name: "typeOn" } },
    { command: "layer.addTextSelector", params: { layer: "text", animator: 1, kind: "expression" } },
    set(`${animator}/properties/scale`, [0, 0, 100]),
    set("text/moreOptions/anchorGrouping", v.words ? 1 : 0),
    set("text/moreOptions/groupingAlignment", [0, -50]),
  ];
  if (v.words) steps.push(set(`${animator}/selectors/expressionSelector/basedOn`, 2));
  if (v.rotation) steps.push(set(`${animator}/properties/rotation`, v.rotation));
  steps.push(
    { command: "prop.setExpression", params: { layer: "text", path: `${animator}/selectors/expressionSelector/amount`, expression: amountExpression } },
    { command: "prop.setExpression", params: { layer: "text", path: "transform/anchor", expression: centredAnchorExpression } },
    { command: "prop.setExpression", params: { layer: "text", path: "transform/scale", expression: wholeScaleExpression } },
    { command: "essential.setName", params: { comp: name, name } },
    { command: "essential.addProperty", params: { comp: name, layer: "text", path: "text/sourceText", name: "Text" } },
    { command: "essential.addProperty", params: { comp: name, layer: "text", path: "text/sourceText", name: "Font", as: "font" } },
    { command: "essential.addProperty", params: { comp: name, layer: "text", path: "transform/position", name: "Position" } },
    { command: "essential.addProperty", params: { comp: name, layer: "text", path: "effects/#1/slider", name: "Letter Overshoot" } },
    { command: "essential.addProperty", params: { comp: name, layer: "text", path: "effects/#2/slider", name: "Pop Time" } },
    { command: "essential.addProperty", params: { comp: name, layer: "text", path: "effects/#3/slider", name: "Whole Overshoot" } },
  );
  if (v.continuous !== undefined)
    steps.push({ command: "essential.addProperty", params: { comp: name, layer: "text", path: "effects/#4/slider", name: "Continuous Scale" } });
  mkdirSync(`effects/${name}`, { recursive: true });
  writeFileSync(`effects/${name}/effect.json`, JSON.stringify(withBluekey(steps), null, 2) + "\n");
}

for (const [name, continuous] of Object.entries(presets)) {
  const steps = [
    { command: "comp.new", params: { name, width: 1920, height: 1080, frameRate: 30, duration: 4, background: "#FAF7F0", open: true } },
    { command: "layer.newText", params: { text: "listening kit", name: "text", position: [960, 540], font: "Schoolbell", style: "Regular", size: 160, fill: [0.07, 0.07, 0.07], justify: "center" } },
    { command: "layer.applyTextPreset", params: { layer: "text", preset: name } },
    { command: "effect.apply", params: { effect: "Slider Control", layers: ["text"] } },
    { command: "prop.set", params: { layer: "text", path: "effects/#1/slider", value: continuous } },
    { command: "prop.setExpression", params: { layer: "text", path: "transform/anchor", expression: presetAnchorExpression } },
    { command: "prop.setExpression", params: { layer: "text", path: "transform/scale", expression: presetScaleExpression } },
    { command: "essential.setName", params: { comp: name, name } },
    { command: "essential.addProperty", params: { comp: name, layer: "text", path: "text/sourceText", name: "Text" } },
    { command: "essential.addProperty", params: { comp: name, layer: "text", path: "text/sourceText", name: "Font", as: "font" } },
    { command: "essential.addProperty", params: { comp: name, layer: "text", path: "transform/position", name: "Position" } },
    { command: "essential.addProperty", params: { comp: name, layer: "text", path: "effects/#1/slider", name: "Continuous Scale" } },
  ];
  mkdirSync(`effects/${name}`, { recursive: true });
  writeFileSync(`effects/${name}/effect.json`, JSON.stringify(withBluekey(steps), null, 2) + "\n");
}

// cv-bluekey: the ListeningKit sticker look (log-cli's .lk-bluekey, the looksmaxxing project's word stickers).
// Schoolbell in brand blue #2a8cff, a white outline inside a dark navy #0d2a4c outline, tilted -3°, blue glow.
// It pops in like the looksmaxxing words (0 → 126% → 94% → 100% over 4 frames) from the "in" marker, pops out in
// reverse from the "out" marker, and wobbles and bobs while on screen.
// Sliders: Continuous Scale (% per second), Wobble (degrees), Bob (pixels).
const bluekeyNames = ["Continuous Scale", "Wobble", "Bob"];

const bluekeyScaleExpression = [
  `var cs = effect("Continuous Scale")("Slider"), f = thisComp.frameDuration;`,
  `function markerKey(name) { try { return thisLayer.marker.key(name); } catch (e) { return null; } }`,
  `var keys = [[0, 0], [2 * f, 126], [3 * f, 94], [4 * f, 100]];`,
  `function pop(t) {`,
  `  if (t <= 0) return 0;`,
  `  for (var j = 1; j < keys.length; j++) if (t <= keys[j][0]) return keys[j - 1][1] + (keys[j][1] - keys[j - 1][1]) * (t - keys[j - 1][0]) / (keys[j][0] - keys[j - 1][0]);`,
  `  return 100;`,
  `}`,
  `var mIn = markerKey("in"), mOut = markerKey("out");`,
  `var p = mIn ? pop(time - mIn.time) : 100;`,
  `if (mOut && time >= mOut.time) p = pop(mOut.time + 4 * f - time);`,
  `var s = (p / 100) * Math.max(1 + (cs / 100) * Math.max(time - (mIn ? mIn.time : 0), 0), 0);`,
  `[100 * s, 100 * s, 100]`,
].join("\n");

{
  const name = "cvBluekey";
  const set = (path, value) => ({ command: "prop.set", params: { layer: "text", path, value } });
  const expr = (path, expression) => ({ command: "prop.setExpression", params: { layer: "text", path, expression } });
  const steps = [
    { command: "comp.new", params: { name, width: 1920, height: 1080, frameRate: 30, duration: 4, background: "#FAF7F0", open: true } },
    { command: "layer.newText", params: { text: "listening kit", name: "text", position: [960, 540], font: "Schoolbell", style: "Regular", size: 160, fill: [0.165, 0.549, 1], stroke: [1, 1, 1], applyStroke: true, strokeWidth: 18, strokeOverFill: false, justify: "center" } },
    { command: "layer.style.stroke", params: { layers: ["text"] } },
    set("layerStyles/stroke/color", [0.051, 0.165, 0.298, 1]),
    set("layerStyles/stroke/size", 5),
    { command: "layer.style.outerGlow", params: { layers: ["text"] } },
    set("layerStyles/outerGlow/blendMode", 0),
    set("layerStyles/outerGlow/color", [0.165, 0.549, 1, 1]),
    set("layerStyles/outerGlow/opacity", 55),
    set("layerStyles/outerGlow/size", 28),
    ...bluekeyNames.map(() => ({ command: "effect.apply", params: { effect: "Slider Control", layers: ["text"] } })),
    set("effects/#1/slider", 6),
    set("effects/#2/slider", 2),
    set("effects/#3/slider", 6),
    { command: "layer.addMarker", params: { layers: ["text"], time: 0, comment: "in" } },
    { command: "layer.addMarker", params: { layers: ["text"], time: 3, comment: "out" } },
    expr("transform/anchor", centredAnchorExpression),
    expr("transform/scale", bluekeyScaleExpression),
    expr("transform/rotation", `-3 + effect("Wobble")("Slider") * Math.cos(time * 2 * Math.PI * 2.5)`),
    expr("transform/position", `value + [0, effect("Bob")("Slider") * Math.cos(time * 2 * Math.PI * 2), 0]`),
    { command: "essential.setName", params: { comp: name, name } },
    { command: "essential.addProperty", params: { comp: name, layer: "text", path: "text/sourceText", name: "Text" } },
    { command: "essential.addProperty", params: { comp: name, layer: "text", path: "text/sourceText", name: "Font", as: "font" } },
    { command: "essential.addProperty", params: { comp: name, layer: "text", path: "transform/position", name: "Position" } },
    ...bluekeyNames.map((n, k) => ({ command: "essential.addProperty", params: { comp: name, layer: "text", path: `effects/#${k + 1}/slider`, name: n } })),
  ];
  mkdirSync(`effects/${name}`, { recursive: true });
  writeFileSync(`effects/${name}/effect.json`, JSON.stringify(steps, null, 2) + "\n");
}

// introCard: a title card precomp.
//   "Introducing" — Satoshi (the ListeningKit site font), navy, the overshoot typewriter.
//   "listening kit" — below it, cv-bluekey look with the overshoot typewriter, on top of the lines around it.
//   Subtext — smaller, one text layer per word, each word scaling in with overshoot one after another.
//     Highlights as on the site: "no dashboards" and "no SaaS" in Satoshi Black, brand blue, with a dashed
//     underline that draws on with them; "your agent." as a small cv-bluekey sticker.
//   The subtext's timing and look live on the "controls" null: its "in" / "out" markers and its
//   Overshoot, Pop Time, Word Spacing and Continuous Scale sliders (the whole block keeps growing around
//   its centre). The words lay themselves out from their own widths,
//   so changing a word's text reflows the line.
{
  const name = "introCard";
  const ink = [0.051, 0.165, 0.298];
  const body = [0.193, 0.29, 0.403]; // navy at 85% on white, as the site's subtext
  const blue = [0.165, 0.549, 1];
  const baselines = [666, 722]; // one per subtext line
  const words = [
    { t: "no", hl: 1 }, { t: "dashboards", hl: 1 }, { t: ",", ns: true },
    { t: "no", hl: 2 }, { t: "SaaS", hl: 2 }, { t: ",", ns: true },
    { t: "just", line: 1 }, { t: "your", line: 1 }, { t: "accounts", line: 1 }, { t: "and", line: 1 },
    { t: "your", bk: true, line: 1 }, { t: "agent.", bk: true, line: 1 },
  ].map((w) => ({ line: 0, ...w })).map((w, i) => {
    const size = w.bk ? 58 : 46;
    return { ...w, i, size, layer: `word ${String(i + 1).padStart(2, "0")}`, anchorY: -Math.round(size * 0.35) };
  });
  const names = JSON.stringify(words.map((w) => w.layer));
  const space = JSON.stringify(words.map((w, i) => (i > 0 && !w.ns && words[i - 1].line === w.line ? 1 : 0)));
  const lines = JSON.stringify(words.map((w) => w.line));
  const n = words.length;

  // Shared by every word and underline: where each word starts, each line centred on its own.
  const layout = [
    `var names = ${names}, space = ${space}, lines = ${lines};`,
    `var gap = thisComp.layer("controls").effect("Word Spacing")("Slider");`,
    `function wordWidth(k) { return thisComp.layer(names[k]).sourceRectAtTime(0, false).width; }`,
    `var lefts = [], totals = [];`,
    `for (var k = 0; k < names.length; k++) { var L = lines[k]; if (totals[L] === undefined) totals[L] = 0; if (space[k]) totals[L] += gap; lefts.push(totals[L]); totals[L] += wordWidth(k); }`,
    `function start(k) { return thisComp.width / 2 - totals[lines[k]] / 2; }`,
  ];
  const timing = [
    `var c = thisComp.layer("controls"), ov = c.effect("Overshoot")("Slider"), pop = Math.max(c.effect("Pop Time")("Slider"), 0.001), n = ${n};`,
    `function markerKey(name) { try { return c.marker.key(name); } catch (e) { return null; } }`,
    `function clamp(t) { return Math.min(Math.max(t, 0), 1); }`,
    `function wordGap(m) { var p = Math.min(pop, m.duration > 0 ? m.duration : pop); return { p: p, g: n > 1 ? Math.max(m.duration - p, 0) / (n - 1) : 0 }; }`,
    `function backOut(t) { var u = t - 1; return 1 + (ov + 1) * u * u * u + ov * u * u; }`,
    `function backIn(t) { return (ov + 1) * t * t * t - ov * t * t; }`,
    `var mIn = markerKey("in"), mOut = markerKey("out");`,
  ];
  // The whole subtext block keeps growing around its centre (controls' Continuous Scale, from its "in" marker):
  // word positions spread out from the centre and every word scales up by the same amount.
  const growth = [
    `var cc = thisComp.layer("controls"), gcs = cc.effect("Continuous Scale")("Slider");`,
    `var gIn; try { gIn = cc.marker.key("in"); } catch (e) { gIn = null; }`,
    `var grow = Math.max(1 + (gcs / 100) * Math.max(time - (gIn ? gIn.time : 0), 0), 0);`,
    `var cx = thisComp.width / 2, cy = ${Math.round((baselines[0] + baselines[1]) / 2 - 16)};`,
  ];
  const wordPosition = (w) =>
    [
      ...layout,
      ...growth,
      `var px = start(${w.i}) + lefts[${w.i}] + wordWidth(${w.i}) / 2, py = ${baselines[w.line] + w.anchorY};`,
      `[cx + (px - cx) * grow, cy + (py - cy) * grow]`,
    ].join("\n");
  const wordAnchor = (w) => [`var r = sourceRectAtTime(0, false);`, `[r.left + r.width / 2, ${w.anchorY}, 0]`].join("\n");
  const wordScale = (w) =>
    [
      ...timing,
      `var i = ${w.i};`,
      `function progress(m) { var q = wordGap(m); return clamp((time - m.time - i * q.g) / q.p); }`,
      `var s = mIn ? backOut(progress(mIn)) : 1;`,
      `if (mOut && time >= mOut.time) s = 1 - backIn(progress(mOut));`,
      ...growth,
      `s = Math.max(s, 0) * grow;`,
      `[100 * s, 100 * s, 100]`,
    ].join("\n");
  // The underline draws on from the first word of its group starting to the last one landing, and back off.
  const underlinePath = (first, last, line) =>
    [
      ...layout,
      ...timing,
      ...growth,
      `var a = ${first}, b = ${last};`,
      `function reveal(m) { var q = wordGap(m); return clamp((time - m.time - a * q.g) / ((b - a) * q.g + q.p)); }`,
      `var v = mIn ? reveal(mIn) : 1;`,
      `if (mOut && time >= mOut.time) v = 1 - reveal(mOut);`,
      `var x0 = start(a) + lefts[a], x1 = start(b) + lefts[b] + wordWidth(b), y = ${baselines[line] + 12};`,
      `x0 = cx + (x0 - cx) * grow; x1 = cx + (x1 - cx) * grow; y = cy + (y - cy) * grow;`,
      `createPath([[x0, y], [x0 + (x1 - x0) * v, y]], [], [], false)`,
    ].join("\n");

  const on = (layer) => ({
    set: (path, value) => ({ command: "prop.set", params: { layer, path, value } }),
    expr: (path, expression) => ({ command: "prop.setExpression", params: { layer, path, expression } }),
    slider: () => ({ command: "effect.apply", params: { effect: "Slider Control", layers: [layer] } }),
    marker: (time, comment) => ({ command: "layer.addMarker", params: { layers: [layer], time, comment } }),
    markerLength: (index, duration) => ({ command: "markers.set", params: { layer, index, duration } }),
  });
  const stickerStyle = (layer, outline) => {
    const l = on(layer);
    return [
      { command: "layer.style.stroke", params: { layers: [layer] } },
      l.set("layerStyles/stroke/color", [...ink, 1]),
      l.set("layerStyles/stroke/size", outline),
      { command: "layer.style.outerGlow", params: { layers: [layer] } },
      l.set("layerStyles/outerGlow/blendMode", 0),
      l.set("layerStyles/outerGlow/color", [...blue, 1]),
      l.set("layerStyles/outerGlow/opacity", 55),
      l.set("layerStyles/outerGlow/size", 28),
    ];
  };

  const intro = on("introducing");
  const brand = on("listening kit");
  const controls = on("controls");
  const steps = [
    { command: "comp.new", params: { name, width: 1920, height: 1080, frameRate: 30, duration: 5, background: "#FAF7F0", open: true } },

    // Background: the cloudBackground template precomp (built first by build.sh).
    { command: "layer.addItem", params: { item: "cloudBackground", time: 0 } },
    { command: "layer.rename", params: { layer: "cloudBackground", name: "background" } },

    // "Introducing": the overshoot typewriter in Satoshi.
    { command: "layer.newText", params: { text: "Introducing", name: "introducing", position: [960, 420], font: "Satoshi", style: "Bold", size: 96, fill: ink, justify: "center" } },
    intro.slider(), intro.slider(), intro.slider(), intro.slider(),
    intro.set("effects/#1/slider", 2), intro.set("effects/#2/slider", 0.25), intro.set("effects/#3/slider", 1.7), intro.set("effects/#4/slider", 6),
    intro.marker(0, "in"), intro.marker(4.2, "out"), intro.markerLength(0, 0.5), intro.markerLength(1, 0.4),
    { command: "layer.addTextAnimator", params: { layer: "introducing", properties: ["scale"], name: "typeOn" } },
    { command: "layer.addTextSelector", params: { layer: "introducing", animator: 1, kind: "expression" } },
    intro.set("text/animators/animator/properties/scale", [0, 0, 100]),
    intro.set("text/moreOptions/groupingAlignment", [0, -50]),
    intro.expr("text/animators/animator/selectors/expressionSelector/amount", amountExpression),
    intro.expr("transform/anchor", centredAnchorExpression),
    intro.expr("transform/scale", wholeScaleExpression),

    // "listening kit": the cv-bluekey look with the overshoot typewriter.
    { command: "layer.newText", params: { text: "listening kit", name: "listening kit", position: [960, 530], font: "Schoolbell", style: "Regular", size: 170, justify: "center", ...bluekeyText } },
    ...stickerStyle("listening kit", 5),
    brand.set("transform/rotation", -3),
    brand.slider(), brand.slider(), brand.slider(), brand.slider(),
    brand.set("effects/#1/slider", 2), brand.set("effects/#2/slider", 0.25), brand.set("effects/#3/slider", 1.7), brand.set("effects/#4/slider", 6),
    brand.marker(0.55, "in"), brand.marker(4.3, "out"), brand.markerLength(0, 0.6), brand.markerLength(1, 0.4),
    { command: "layer.addTextAnimator", params: { layer: "listening kit", properties: ["scale"], name: "typeOn" } },
    { command: "layer.addTextSelector", params: { layer: "listening kit", animator: 1, kind: "expression" } },
    brand.set("text/animators/animator/properties/scale", [0, 0, 100]),
    brand.set("text/moreOptions/groupingAlignment", [0, -50]),
    brand.expr("text/animators/animator/selectors/expressionSelector/amount", amountExpression),
    brand.expr("transform/anchor", centredAnchorExpression),
    brand.expr("transform/scale", wholeScaleExpression),

    // The subtext's controls.
    { command: "layer.newNull", params: { name: "controls" } },
    controls.slider(), controls.slider(), controls.slider(), controls.slider(),
    controls.set("effects/#1/slider", 2), controls.set("effects/#2/slider", 0.3), controls.set("effects/#3/slider", 18), controls.set("effects/#4/slider", 6),
    controls.marker(1, "in"), controls.marker(4.4, "out"), controls.markerLength(0, 1), controls.markerLength(1, 0.4),
  ];

  for (const w of words) {
    const l = on(w.layer);
    const look = w.bk
      ? { font: "Schoolbell", style: "Regular", ...bluekeyText, strokeWidth: 7 }
      : { font: "Satoshi", style: w.hl ? "Black" : "Bold", fill: w.hl ? blue : body };
    steps.push(
      { command: "layer.newText", params: { text: w.t, name: w.layer, position: [960, baselines[w.line]], size: w.size, ...look } },
      ...(w.bk ? [...stickerStyle(w.layer, 2), l.set("transform/rotation", -3)] : []),
      l.expr("transform/anchor", wordAnchor(w)),
      l.expr("transform/position", wordPosition(w)),
      l.expr("transform/scale", wordScale(w)),
    );
  }

  for (const group of [1, 2]) {
    const inGroup = words.filter((w) => w.hl === group);
    const layer = `underline ${group}`;
    const l = on(layer);
    steps.push(
      { command: "layer.newShape", params: { kind: "none", name: layer } },
      { command: "shape.newPath", params: { layer, vertices: [[0, 0], [100, 0]], closed: false, fill: false, stroke: blue, strokeWidth: 4, space: "layer" } },
      l.set("transform/position", [0, 0]),
      l.set("transform/anchor", [0, 0]),
      l.set("contents/group/contents/stroke/dashes/dash", 10),
      l.set("contents/group/contents/stroke/dashes/gap", 7),
      l.expr("contents/group/contents/path/path", underlinePath(inGroup[0].i, inGroup[inGroup.length - 1].i, inGroup[0].line)),
      l.expr("contents/group/contents/stroke/width", [...growth, `4 * grow`].join("\n")),
    );
  }

  // "listening kit" sits on top, overlapping "Introducing" above it and the subtext below it.
  steps.push({ command: "layer.arrange", params: { layers: ["listening kit"], to: "front" } });

  const ess = (layer, path, label, as) => ({ command: "essential.addProperty", params: { comp: name, layer, path, name: label, ...(as ? { as } : {}) } });
  steps.push(
    { command: "essential.setName", params: { comp: name, name } },
    ess("introducing", "text/sourceText", "Introducing"),
    ess("listening kit", "text/sourceText", "Brand"),
    ...words.filter((w) => w.t !== ",").map((w) => ess(w.layer, "text/sourceText", `Subtext ${w.layer.replace("word ", "")}`)),
    ess("introducing", "effects/#4/slider", "Introducing Continuous Scale"),
    ess("listening kit", "effects/#4/slider", "Brand Continuous Scale"),
    ess("controls", "effects/#4/slider", "Subtext Continuous Scale"),
    ess("controls", "effects/#1/slider", "Subtext Overshoot"),
    ess("controls", "effects/#2/slider", "Subtext Pop Time"),
    ess("controls", "effects/#3/slider", "Word Spacing"),
  );
  mkdirSync(`effects/${name}`, { recursive: true });
  writeFileSync(`effects/${name}/effect.json`, JSON.stringify(steps, null, 2) + "\n");
}

// cloudBackground: 3D clay clouds drifting over the ditherGradientBackground sky, rebuilt from log-cli's landing
// page hero (site/apps/web/src/landing/ClayClouds.tsx). That page loads Claybound's cloud.glb, which isn't
// licensed to ListeningKit, so each cloud here is our own: a cluster of six 3D spheres under a null.
//
//   clayClouds — an Advanced 3D comp: a 30° camera, ambient + warm key (casting shadows) + blue fill lights, and
//     30 clouds in 4 depth layers (12 far and small ... 3 near and big), as on the site. Each cloud drifts right
//     at its layer's speed and wraps around, bobs gently and turns slowly (expressions on its null). Far clouds
//     are tinted toward the sky to stand in for the site's fog.
//   cloudBackground — the ditherGradientBackground precomp as the sky, then clayClouds run through the site's
//     clay dither: Black & White, Levels (black point 0.3, white point 0.92), Craft Halftone & Dither (3 px
//     cells), Tint (shade light blue #9ecbff, lit white).
// Positions are generated from a fixed seed, so every build is the same.
{
  const plugins = { command: "effect.plugins.load", params: { folder: `${process.env.APPDATA.replace(/\\/g, "/")}/EffectCraft/Plug-ins` } };
  const set = (layer, path, value) => ({ command: "prop.set", params: { layer, path, value } });
  const expr = (layer, path, expression) => ({ command: "prop.setExpression", params: { layer, path, expression } });
  const fx = (layer, effect) => ({ command: "effect.apply", params: { effect, layers: [layer] } });

  let seed = 20261110;
  const random = () => ((seed = (seed * 1664525 + 1013904223) % 4294967296) / 4294967296);
  const round = (n) => Math.round(n * 100) / 100;

  // The site's scene in its own units: camera at z 12 with a 30° field of view, clouds in layers at z -16 ... -1.
  const layers = [
    { count: 12, z: -16, scale: 0.75, speed: 0.05, fog: 0.35 },
    { count: 9, z: -10, scale: 1.0, speed: 0.08, fog: 0.2 },
    { count: 6, z: -5, scale: 1.35, speed: 0.13, fog: 0.08 },
    { count: 3, z: -1, scale: 1.9, speed: 0.22, fog: 0 },
  ];
  const cameraZ = 12;
  const unit = 540 / Math.tan((15 * Math.PI) / 180) / cameraZ; // px per site unit at z 0
  const halfHeight = (z) => Math.tan((15 * Math.PI) / 180) * (cameraZ - z);
  const halfWidth = (z) => halfHeight(z) * (1920 / 1080);
  const sky = [0.353, 0.651, 1]; // the site's fog colour #5aa6ff
  // One cloud: six puffs [x, y, radius] as fractions of its width (y down).
  const puffs = [[0, -0.05, 0.3], [-0.3, 0.08, 0.22], [0.3, 0.06, 0.24], [-0.12, 0.14, 0.22], [0.16, 0.15, 0.22], [0.06, -0.2, 0.2]];

  const steps = [
    plugins,
    { command: "comp.new", params: { name: "clayClouds", width: 1920, height: 1080, frameRate: 30, duration: 5, open: true } },
    { command: "comp.settings", params: { comp: "clayClouds", renderer: "advanced3D" } },
    { command: "layer.newCamera", params: { name: "camera", type: "oneNode", angleOfView: 30, position: [960, 540, -cameraZ * unit] } },
    { command: "layer.newLight", params: { kind: "Ambient", name: "ambient", color: "#ffffff", intensity: 55 } },
    { command: "layer.newLight", params: { kind: "Parallel", name: "key", color: "#fff1dc", intensity: 110, castsShadows: true, position: [-40, -960, -1700] } },
    { command: "layer.newLight", params: { kind: "Parallel", name: "fill", color: "#a8d1ff", intensity: 30, position: [2260, 840, -1000] } },
  ];

  let n = 0;
  for (const layer of layers) {
    const zPx = -layer.z * unit;
    const edge = halfWidth(layer.z) + 2; // site units either side of centre before a cloud wraps
    for (let i = 0; i < layer.count; i++) {
      n += 1;
      const name = `cloud ${String(n).padStart(2, "0")}`;
      const s = layer.scale * (0.6 + random() * 0.7);
      const squash = 0.8 + random() * 0.3;
      const half = halfHeight(layer.z);
      const minY = half - 0.63 * 2 * half + 0.5 * s;
      const maxY = half - 0.55 * s;
      const yUnits = minY + random() * Math.max(0, maxY - minY);
      const span = edge * 2;
      const xUnits = -edge + (span / layer.count) * (i + random() * 0.6);
      const phase = random() * Math.PI * 2;
      const spin = (random() - 0.5) * 0.08;
      const turn = (random() - 0.5) * 0.9;
      const widthPx = 2 * s * unit;
      const colour = sky.map((c) => round(1 + (c - 1) * layer.fog));

      steps.push(
        { command: "layer.newNull", params: { name } },
        { command: "layer.setSwitch", params: { layers: [name], switch: "threeD", value: true } },
        set(name, "transform/position", [round(960 + xUnits * unit), round(540 - yUnits * unit), round(zPx)]),
        set(name, "transform/scale", [100, round(100 * squash), 100]),
        // Drift right at the layer's speed and wrap at the edge, bob, and turn slowly, as on the site.
        expr(name, "transform/position", [
          `var unit = ${round(unit)}, speed = ${layer.speed}, edge = ${round(edge)};`,
          `var x0 = ${round(xUnits)}, y0 = ${round(yUnits)}, phase = ${round(phase)};`,
          `var x = x0 + speed * time + edge;`,
          `x = x - Math.floor(x / (2 * edge)) * (2 * edge) - edge;`,
          `var y = y0 + Math.sin(time * 0.5 + phase) * 0.08;`,
          `[960 + x * unit, 540 - y * unit, ${round(zPx)}]`,
        ].join("\n")),
        expr(name, "transform/rotationY", `${round((turn * 180) / Math.PI)} + ${round((spin * 180) / Math.PI)} * time`),
      );
      puffs.forEach(([dx, dy, r], k) => {
        const puff = `${name} puff ${k + 1}`;
        steps.push(
          { command: "layer.new3dPrimitive", params: { kind: "sphere", name: puff, radius: round((r * widthPx) / 1.9), position: [round(960 + xUnits * unit + (dx * widthPx) / 1.9), round(540 - yUnits * unit + (dy * widthPx) / 1.9), round(zPx)], baseColor: colour, roughness: 0.85, metallic: 0, castsShadows: true, acceptsShadows: true } },
          { command: "layer.setParent", params: { layers: [puff], parent: name } },
        );
      });
    }
  }

  steps.push(
    { command: "comp.new", params: { name: "cloudBackground", width: 1920, height: 1080, frameRate: 30, duration: 5, open: true } },
    // The sky is the ditherGradientBackground precomp (built first by build.sh).
    { command: "layer.addItem", params: { item: "ditherGradientBackground", time: 0 } },
    { command: "layer.rename", params: { layer: "ditherGradientBackground", name: "sky" } },
    { command: "layer.addItem", params: { item: "clayClouds", time: 0 } },
    fx("clayClouds", "Black & White"),
    fx("clayClouds", "Levels"),
    set("clayClouds", "effects/#2/inBlack", 0.3),
    set("clayClouds", "effects/#2/inWhite", 0.92),
    fx("clayClouds", "Craft Halftone & Dither"),
    set("clayClouds", "effects/#3/cell_size", 3),
    set("clayClouds", "effects/#3/contrast", 1),
    set("clayClouds", "effects/#3/dither_spread", 1),
    fx("clayClouds", "Tint"),
    set("clayClouds", "effects/#4/black", [0.62, 0.8, 1, 1]),
    set("clayClouds", "effects/#4/white", [1, 1, 1, 1]),
    { command: "essential.setName", params: { comp: "cloudBackground", name: "cloudBackground" } },
    { command: "essential.addProperty", params: { comp: "cloudBackground", layer: "clayClouds", path: "effects/#3/cell_size", name: "Cloud Dither Size" } },
    { command: "essential.addProperty", params: { comp: "cloudBackground", layer: "clayClouds", path: "effects/#4/black", name: "Cloud Shade" } },
    { command: "essential.addProperty", params: { comp: "cloudBackground", layer: "clayClouds", path: "effects/#4/white", name: "Cloud Lit" } },
  );
  mkdirSync("effects/cloudBackground", { recursive: true });
  writeFileSync("effects/cloudBackground/effect.json", JSON.stringify(steps, null, 2) + "\n");
}

// ditherGradientBackground: brand blue at the top breaking into light blue, then into white, in big square
// pixels (ordered/Bayer dither). Two bands, each a black-to-white Gradient Ramp run through Craft Halftone &
// Dither (18 px cells) and then Tint, so the dither's black and white become the band's two colours:
//   upper — Top Color (blue) to Middle Color (light blue), from y 320 to 702.
//   lower — Middle Color to Bottom Color (white), from y 702 down, wiped so it only covers below 702.
// Essential Graphics: Top Color, Middle Color, Bottom Color, Pixel Size.
{
  const name = "ditherGradientBackground";
  const plugins = { command: "effect.plugins.load", params: { folder: `${process.env.APPDATA.replace(/\\/g, "/")}/EffectCraft/Plug-ins` } };
  const set = (layer, path, value) => ({ command: "prop.set", params: { layer, path, value } });
  const expr = (layer, path, expression) => ({ command: "prop.setExpression", params: { layer, path, expression } });
  const fx = (layer, effect) => ({ command: "effect.apply", params: { effect, layers: [layer] } });
  const blue = [0.165, 0.549, 1, 1];
  const lightBlue = [0.56, 0.77, 1, 1];
  const white = [1, 1, 1, 1];
  const split = 702; // a multiple of the 18 px cell, so the cut falls between pixel rows

  const band = (layer, y0, y1, black, whiteTo) => [
    { command: "layer.newSolid", params: { name: layer, color: "#000000", width: 1920, height: 1080 } },
    fx(layer, "Gradient Ramp"),
    set(layer, "effects/#1/start", [960, y0]),
    set(layer, "effects/#1/startColor", [0, 0, 0, 1]),
    set(layer, "effects/#1/end", [960, y1]),
    set(layer, "effects/#1/endColor", [1, 1, 1, 1]),
    fx(layer, "Craft Halftone & Dither"),
    set(layer, "effects/#2/cell_size", 18),
    set(layer, "effects/#2/contrast", 1),
    set(layer, "effects/#2/dither_spread", 1),
    fx(layer, "Tint"),
    set(layer, "effects/#3/black", black),
    set(layer, "effects/#3/white", whiteTo),
  ];

  const steps = [
    plugins,
    { command: "comp.new", params: { name, width: 1920, height: 1080, frameRate: 30, duration: 5, open: true } },
    ...band("upper", 320, split, blue, lightBlue),
    ...band("lower", split, 1200, lightBlue, white),
    fx("lower", "Linear Wipe"),
    set("lower", "effects/#4/completion", (split / 1080) * 100),
    set("lower", "effects/#4/angle", 180),
    // The lower band follows the upper one's Middle Color and pixel size.
    expr("lower", "effects/#3/black", `thisComp.layer("upper").effect(3)(2)`),
    expr("lower", "effects/#2/cell_size", `thisComp.layer("upper").effect(2)("cell_size")`),
    { command: "essential.setName", params: { comp: name, name } },
    { command: "essential.addProperty", params: { comp: name, layer: "upper", path: "effects/#3/black", name: "Top Color" } },
    { command: "essential.addProperty", params: { comp: name, layer: "upper", path: "effects/#3/white", name: "Middle Color" } },
    { command: "essential.addProperty", params: { comp: name, layer: "lower", path: "effects/#3/white", name: "Bottom Color" } },
    { command: "essential.addProperty", params: { comp: name, layer: "upper", path: "effects/#2/cell_size", name: "Pixel Size" } },
  ];
  mkdirSync(`effects/${name}`, { recursive: true });
  writeFileSync(`effects/${name}/effect.json`, JSON.stringify(steps, null, 2) + "\n");
}
