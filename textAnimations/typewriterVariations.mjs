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
import { mkdirSync, writeFileSync as writeFileRaw } from "node:fs";

// effectcraft-cli reads command files in the Windows code page, not UTF-8, so every non-ASCII character
// (symbols, curly quotes, middle dots…) is written as a JSON \u escape, which reads back exactly.
const writeFileSync = (path, text) =>
  writeFileRaw(path, text.replace(/[\u0080-￿]/g, (c) => "\\u" + c.charCodeAt(0).toString(16).padStart(4, "0")));

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
    // Slide in and out: the controls null's "in" marker (start, and how long until the last cloud has landed)
    // and "out" marker (start, and how long until the last cloud has left), with Overshoot and Stagger (the
    // most seconds one cloud starts after another) sliders.
    { command: "layer.newNull", params: { name: "controls" } },
    fx("controls", "Slider Control"),
    fx("controls", "Slider Control"),
    set("controls", "effects/#1/slider", 1.7),
    set("controls", "effects/#2/slider", 0.35),
    { command: "layer.addMarker", params: { layers: ["controls"], time: 0, comment: "in" } },
    { command: "layer.addMarker", params: { layers: ["controls"], time: 3.6, comment: "out" } },
    { command: "markers.set", params: { layer: "controls", index: 0, duration: 1.3 } },
    { command: "markers.set", params: { layer: "controls", index: 1, duration: 1.3 } },
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
        // Drift right at the layer's speed and wrap at the edge, bob, and turn slowly, as on the site. On top of
        // that, slide in from off the left with overshoot at the controls' "in" marker, and wind up and slide
        // back out to the left at its "out" marker, each cloud a little after the last (Stagger).
        expr(name, "transform/position", [
          `var unit = ${round(unit)}, speed = ${layer.speed}, edge = ${round(edge)};`,
          `var x0 = ${round(xUnits)}, y0 = ${round(yUnits)}, phase = ${round(phase)};`,
          `var x = x0 + speed * time + edge;`,
          `x = x - Math.floor(x / (2 * edge)) * (2 * edge) - edge;`,
          `var y = y0 + Math.sin(time * 0.5 + phase) * 0.08;`,
          `var c = thisComp.layer("controls"), ov = c.effect("Overshoot")("Slider"), stagger = Math.max(c.effect("Stagger")("Slider"), 0);`,
          `function markerKey(name) { try { return c.marker.key(name); } catch (e) { return null; } }`,
          `var delay = stagger * ${((n * 7) % 10) / 10};`,
          `function progress(m) { var d = Math.max(m.duration - stagger, 0.001); return Math.min(Math.max((time - m.time - delay) / d, 0), 1); }`,
          `function backOut(t) { var u = t - 1; return 1 + (ov + 1) * u * u * u + ov * u * u; }`,
          `function backIn(t) { return (ov + 1) * t * t * t - ov * t * t; }`,
          `var mIn = markerKey("in"), mOut = markerKey("out"), away = x + edge;`,
          `if (mIn) x -= away * (1 - backOut(progress(mIn)));`,
          `if (mOut && time >= mOut.time) x -= away * backIn(progress(mOut));`,
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

// ditherGradientBackground: brand blue breaking into light blue, then into white, in big square pixels
// (ordered/Bayer dither), wiping up the frame from fully blue to fully white. Two bands, each a black-to-white
// Gradient Ramp run through Craft Halftone & Dither (18 px cells) and then Tint, so the dither's black and white
// become the band's two colours:
//   upper — Top Color (blue) to Middle Color (light blue) over 378 px.
//   lower — Middle Color to Bottom Color (white) over the next 491 px, wiped so it only covers below the split.
// The "controls" null's Wipe slider moves both bands together: 0 is fully blue (the fade sits below the frame),
// 100 is fully white (the fade has gone off the top). It's keyframed 0 → 100 over the comp with easy ease, so the
// fade comes up slowly, speeds up, and settles on white at the end; retime or reshape it by moving the keys.
// Essential Graphics: Wipe, Top Color, Middle Color, Bottom Color, Pixel Size.
{
  const name = "ditherGradientBackground";
  const plugins = { command: "effect.plugins.load", params: { folder: `${process.env.APPDATA.replace(/\\/g, "/")}/EffectCraft/Plug-ins` } };
  const set = (layer, path, value) => ({ command: "prop.set", params: { layer, path, value } });
  const key = (layer, path, value, time) => ({ command: "prop.addKey", params: { layer, path, value, time } });
  const ease = (layer, path, time, side) => ({ command: "keys.setEase", params: { layer, path, time, side, speed: 0, influence: 60 } });
  const expr = (layer, path, expression) => ({ command: "prop.setExpression", params: { layer, path, expression } });
  const fx = (layer, effect) => ({ command: "effect.apply", params: { effect, layers: [layer] } });
  const blue = [0.165, 0.549, 1, 1];
  const lightBlue = [0.56, 0.77, 1, 1];
  const white = [1, 1, 1, 1];
  const duration = 5;
  const lastFrame = duration - 1 / 30;
  // Where the bands sit, from the Wipe slider. The fade is 378 px (upper) + 491 px (lower) tall; Wipe moves its top
  // edge from the bottom of the frame (0) to the fade's full height above the top (100). The split between the
  // bands is snapped to the pixel grid so it falls between pixel rows.
  const geometry = [
    `var p = Math.min(Math.max(thisComp.layer("controls").effect("Wipe")("Slider"), 0), 100) / 100;`,
    `var cell = Math.max(thisComp.layer("upper").effect(2)("cell_size"), 1);`,
    `var up = 378, low = 491, H = thisComp.height;`,
    `var top = H - p * (H + up + low + cell);`,
    `var split = Math.round((top + up) / cell) * cell;`,
    `var bottom = split + low;`,
    `var bottomRow = Math.ceil(bottom / cell) * cell;`,
  ];
  const at = (result) => [...geometry, result].join("\n");

  const band = (layer, black, whiteTo) => [
    { command: "layer.newSolid", params: { name: layer, color: "#000000", width: 1920, height: 1080 } },
    fx(layer, "Gradient Ramp"),
    set(layer, "effects/#1/startColor", [0, 0, 0, 1]),
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
    { command: "comp.new", params: { name, width: 1920, height: 1080, frameRate: 30, duration, open: true } },
    ...band("upper", blue, lightBlue),
    ...band("lower", lightBlue, white),
    fx("lower", "Linear Wipe"),
    set("lower", "effects/#4/angle", 180),
    // The lower band follows the upper one's Middle Color and pixel size.
    expr("lower", "effects/#3/black", `thisComp.layer("upper").effect(3)(2)`),
    expr("lower", "effects/#2/cell_size", `thisComp.layer("upper").effect(2)("cell_size")`),

    // The controls null and its Wipe slider, keyframed fully blue → fully white with easy ease.
    { command: "layer.newNull", params: { name: "controls" } },
    fx("controls", "Slider Control"),
    key("controls", "effects/#1/slider", 0, 0),
    key("controls", "effects/#1/slider", 100, lastFrame),
    ease("controls", "effects/#1/slider", 0, "out"),
    ease("controls", "effects/#1/slider", lastFrame, "in"),

    expr("upper", "effects/#1/start", at(`[thisComp.width / 2, top]`)),
    expr("upper", "effects/#1/end", at(`[thisComp.width / 2, split]`)),
    expr("lower", "effects/#1/start", at(`[thisComp.width / 2, split]`)),
    expr("lower", "effects/#1/end", at(`[thisComp.width / 2, bottom]`)),
    expr("lower", "effects/#4/completion", at(`Math.min(Math.max(split / H * 100, 0), 100)`)),

    // The dither leaves a dot in every tile even in pure white, so a clean Bottom Color layer covers everything
    // past the end of the fade (snapped to the pixel rows); at Wipe 100 that's the whole frame.
    { command: "layer.newSolid", params: { name: "clear", color: "#ffffff", width: 1920, height: 1080 } },
    fx("clear", "Fill"),
    expr("clear", "effects/#1/color", `thisComp.layer("lower").effect(3)(2)`),
    fx("clear", "Linear Wipe"),
    set("clear", "effects/#2/angle", 180),
    expr("clear", "effects/#2/completion", at(`Math.min(Math.max(bottomRow / H * 100, 0), 100)`)),

    { command: "essential.setName", params: { comp: name, name } },
    { command: "essential.addProperty", params: { comp: name, layer: "controls", path: "effects/#1/slider", name: "Wipe" } },
    { command: "essential.addProperty", params: { comp: name, layer: "upper", path: "effects/#3/black", name: "Top Color" } },
    { command: "essential.addProperty", params: { comp: name, layer: "upper", path: "effects/#3/white", name: "Middle Color" } },
    { command: "essential.addProperty", params: { comp: name, layer: "lower", path: "effects/#3/white", name: "Bottom Color" } },
    { command: "essential.addProperty", params: { comp: name, layer: "upper", path: "effects/#2/cell_size", name: "Pixel Size" } },
  ];
  mkdirSync(`effects/${name}`, { recursive: true });
  writeFileSync(`effects/${name}/effect.json`, JSON.stringify(steps, null, 2) + "\n");
}

// brickTextBackground: a wall of blue rounded bricks filling the frame, each holding one word picked at random
// from a sentence.
//   sentence — a guide text layer (not rendered) holding the sentence; edit it (or Sentence in Essential
//     Graphics) and every brick re-picks its words from it.
//   controls — Build (0–100): the bricks pop in one by one in a fixed random order with overshoot, and at 100 the
//     wall fills the whole comp. It's keyframed 0 → 100 over the first 2.5 s. Overshoot sets the pop. Scramble
//     (checkbox) makes every brick swap to another random word every Scramble Every seconds, each brick at its own
//     moment. Brick Color sets the bricks.
//   8 rows of bricks in a running bond (every other row shifted half a brick), each brick a shape layer with its
//   word as a child text layer that shrinks to fit.
{
  const name = "brickTextBackground";
  const set = (layer, path, value) => ({ command: "prop.set", params: { layer, path, value } });
  const expr = (layer, path, expression) => ({ command: "prop.setExpression", params: { layer, path, expression } });
  const fx = (layer, effect) => ({ command: "effect.apply", params: { effect, layers: [layer] } });
  const key = (layer, path, value, time) => ({ command: "prop.addKey", params: { layer, path, value, time } });
  const ease = (layer, path, time, side) => ({ command: "keys.setEase", params: { layer, path, time, side, speed: 0, influence: 60 } });
  const round = (v) => Math.round(v * 100) / 100;

  let seed = 424242;
  const random = () => ((seed = (seed * 1664525 + 1013904223) % 4294967296) / 4294967296);

  const W = 1920, H = 1080, rows = 8, perRow = 7, gap = 10;
  const rowH = H / rows, brickW = W / perRow;
  const bricks = [];
  for (let r = 0; r < rows; r++) {
    const offset = r % 2 === 1;
    const count = offset ? perRow + 1 : perRow;
    for (let c = 0; c < count; c++) bricks.push({ x: offset ? c * brickW : brickW / 2 + c * brickW, y: rowH / 2 + r * rowH });
  }
  const n = bricks.length;
  // A fixed random build order.
  const order = bricks.map((_, i) => i);
  for (let i = n - 1; i > 0; i--) {
    const j = Math.floor(random() * (i + 1));
    [order[i], order[j]] = [order[j], order[i]];
  }

  const controls = `var c = thisComp.layer("controls");`;
  const hash = `function rnd(v) { var s = Math.sin(v * 12.9898) * 43758.5453; return s - Math.floor(s); }`;
  const steps = [
    { command: "comp.new", params: { name, width: W, height: H, frameRate: 30, duration: 5, background: "#ffffff", open: true } },
    { command: "layer.newNull", params: { name: "controls" } },
    fx("controls", "Slider Control"),
    fx("controls", "Slider Control"),
    fx("controls", "Checkbox Control"),
    fx("controls", "Slider Control"),
    fx("controls", "Color Control"),
    key("controls", "effects/#1/slider", 0, 0),
    key("controls", "effects/#1/slider", 100, 2.5),
    ease("controls", "effects/#1/slider", 0, "out"),
    ease("controls", "effects/#1/slider", 2.5, "in"),
    set("controls", "effects/#2/slider", 1.7),
    set("controls", "effects/#3/checkbox", false),
    set("controls", "effects/#4/slider", 0.8),
    set("controls", "effects/#5/color", [0.165, 0.549, 1, 1]),
    { command: "layer.newText", params: { text: "Listen to your competitors across Twitter Reddit and Facebook help their customers and get new customers", name: "sentence", position: [960, 540], font: "Satoshi", style: "Bold", size: 40, fill: [0, 0, 0], justify: "center" } },
    { command: "layer.setSwitch", params: { layers: ["sentence"], switch: "guide", value: true } },
    // Hidden: EffectCraft still draws guide layers in the viewer. The bricks read its text either way.
    { command: "layer.setSwitch", params: { layers: ["sentence"], switch: "video", value: false } },
  ];

  bricks.forEach((b, i) => {
    const id = String(i + 1).padStart(2, "0");
    const brick = `brick ${id}`;
    const word = `word ${id}`;
    steps.push(
      { command: "layer.newShape", params: { kind: "rounded", name: brick, size: [round(brickW - gap), round(rowH - gap)], fill: [0.165, 0.549, 1], position: [round(b.x), round(b.y)] } },
      set(brick, "contents/group/contents/rect/roundness", 14),
      expr(brick, "contents/group/contents/fill/color", `thisComp.layer("controls").effect("Brick Color")("Color")`),
      // Pop in with overshoot as Build passes this brick's place in the order; every brick is in by Build 100.
      expr(brick, "transform/scale", [
        controls,
        `var build = c.effect("Build")("Slider"), ov = c.effect("Overshoot")("Slider");`,
        `var n = ${n}, place = ${order.indexOf(i)}, w = 100 / n * 4;`,
        `var t = Math.min(Math.max((build - place / n * (100 - w)) / w, 0), 1), u = t - 1;`,
        `var s = t <= 0 ? 0 : 1 + (ov + 1) * u * u * u + ov * u * u;`,
        `[100 * s, 100 * s]`,
      ].join("\n")),
      { command: "layer.newText", params: { text: "word", name: word, position: [round(b.x), round(b.y)], font: "Satoshi", style: "Bold", size: 46, fill: [1, 1, 1], justify: "center" } },
      { command: "layer.setParent", params: { layers: [word], parent: brick } },
      set(word, "transform/position", [0, 0, 0]),
      // A random word from the sentence; with Scramble on it re-picks every Scramble Every seconds.
      expr(word, "text/sourceText", [
        controls,
        hash,
        `var words = String(thisComp.layer("sentence").text.sourceText).split(/\\s+/);`,
        `var list = []; for (var k = 0; k < words.length; k++) if (words[k].length) list.push(words[k]);`,
        `var every = Math.max(c.effect("Scramble Every")("Slider"), 0.05), k0 = ${i + 1};`,
        `var tick = c.effect("Scramble")("Checkbox") == 1 ? Math.floor(time / every + rnd(k0 * 3.7)) : 0;`,
        `function mix(a) { a = (a ^ 61) ^ (a >>> 16); a = a + (a << 3); a = a ^ (a >>> 4); a = (a * 668265261) | 0; a = a ^ (a >>> 15); return a >>> 0; }`,
        `list.length ? list[mix(k0 * 7919 + tick * 104729) % list.length] : ""`,
      ].join("\n")),
      expr(word, "transform/anchor", [`var r = sourceRectAtTime(time, false);`, `[r.left + r.width / 2, r.top + r.height / 2, 0]`].join("\n")),
      expr(word, "transform/scale", [`var r = sourceRectAtTime(time, false);`, `var f = r.width > 0 ? Math.min(1, ${round(brickW - gap - 34)} / r.width) : 1;`, `[100 * f, 100 * f, 100]`].join("\n")),
    );
  });

  steps.push(
    { command: "essential.setName", params: { comp: name, name } },
    { command: "essential.addProperty", params: { comp: name, layer: "sentence", path: "text/sourceText", name: "Sentence" } },
    { command: "essential.addProperty", params: { comp: name, layer: "controls", path: "effects/#1/slider", name: "Build" } },
    { command: "essential.addProperty", params: { comp: name, layer: "controls", path: "effects/#2/slider", name: "Overshoot" } },
    { command: "essential.addProperty", params: { comp: name, layer: "controls", path: "effects/#3/checkbox", name: "Scramble" } },
    { command: "essential.addProperty", params: { comp: name, layer: "controls", path: "effects/#4/slider", name: "Scramble Every" } },
    { command: "essential.addProperty", params: { comp: name, layer: "controls", path: "effects/#5/color", name: "Brick Color" } },
  );
  mkdirSync(`effects/${name}`, { recursive: true });
  writeFileSync(`effects/${name}/effect.json`, JSON.stringify(steps, null, 2) + "\n");
}

// claudeCode, codex, terminal: the agent windows from log-cli's landing page, rebuilt as reusable precomps
// (site/apps/web/src/landing/AgentSession.tsx for the Claude Code and Codex windows, the "Paste this into your
// terminal" box in landing/useCases/UseCasesPage.tsx for the terminal). Each is a 1920×1080 comp with a transparent
// background and the window centred, built from plain shapes and text so it stays light. They play the start of the
// site's session: the prompt pops in and types, a log tool call pops in, and the reply types on word by word (the
// terminal types its lines one after another). Edit the text in Essential Graphics.
{
  const set = (layer, path, value) => ({ command: "prop.set", params: { layer, path, value } });
  const expr = (layer, path, expression) => ({ command: "prop.setExpression", params: { layer, path, expression } });
  const hex = (h) => [1, 3, 5].map((i) => Math.round((parseInt(h.slice(i, i + 2), 16) / 255) * 1000) / 1000);

  const rect = (name, cx, cy, w, h, fill, opts = {}) => [
    { command: "layer.newShape", params: { kind: "rounded", name, size: [w, h], fill: hex(fill), position: [cx, cy], ...(opts.stroke ? { stroke: hex(opts.stroke), strokeWidth: opts.strokeWidth ?? 2 } : {}) } },
    set(name, "contents/group/contents/rect/roundness", opts.round ?? 0),
  ];
  const text = (name, str, x, y, opts = {}) => ({
    command: "layer.newText",
    params: { text: str, name, position: [x, y], font: opts.font ?? "Satoshi", style: opts.style ?? "Medium", size: opts.size ?? 22, fill: hex(opts.fill ?? "#1a1a18"), justify: opts.justify ?? "left", ...(opts.box ? { box: opts.box } : {}) },
  });
  const parent = (child, to) => ({ command: "layer.setParent", params: { layers: [child], parent: to } });
  // Pops in from nothing with overshoot at t0.
  const pop = (layer, t0) => expr(layer, "transform/scale", [
    `var t = Math.min(Math.max((time - ${t0}) / 0.35, 0), 1), u = t - 1, ov = 1.7;`,
    `var s = t <= 0 ? 0 : 1 + (ov + 1) * u * u * u + ov * u * u;`,
    `[100 * s, 100 * s]`,
  ].join("\n"));
  // Types its own text on from t0, by character or by word.
  const type = (layer, t0, rate, perWord = false) => expr(layer, "text/sourceText", perWord
    ? [`var s = String(value), w = s.split(" ");`, `var n = Math.max(0, Math.floor((time - ${t0}) * ${rate}));`, `w.slice(0, n).join(" ")`].join("\n")
    : [`var s = String(value);`, `s.slice(0, Math.max(0, Math.floor((time - ${t0}) * ${rate})))`].join("\n"));
  const appearAt = (layer, t0) => expr(layer, "transform/opacity", `time >= ${t0} ? 100 : 0`);
  const essText = (comp, layer, label) => ({ command: "essential.addProperty", params: { comp, layer, path: "text/sourceText", name: label } });

  const prompt = "check my twitter whos waiting on me";
  const reply = "6 people are waiting on you, and 2 more opened your last message but didn’t reply. Reading each thread in full before drafting anything.";
  const toolArgs = '{ account: "you", waiting: true, limit: "50" }';
  const toolLines = ["@you, 6 conversations waiting on a reply, newest first", "1. @dana_builds · 2h ago · unread, waiting on you", "2. @leo_ops · 5h ago · unread, waiting on you"];
  const mono = { font: "JetBrains Mono", style: "Regular", size: 17 };
  // The window: 1400 × 800, centred; sidebar 330 wide; feed column from x 620 to 1630.
  const L = 260, T = 140, W = 1400, H = 800, side = 330, feedX = 620, feedW = 1010;

  // A brand mark from assets/ (the 24×24 SVGs from log-cli's BrandMark.tsx), sized to px and kept sharp.
  const brandMark = (file, x, y, px) => [
    { command: "file.import", params: { paths: [`${process.cwd().replace(/\\/g, "/")}/assets/${file}`] } },
    { command: "layer.addItem", params: { item: file, position: [x, y] } },
    { command: "layer.rename", params: { layer: file, name: "mark" } },
    set("mark", "transform/scale", [(px / 24) * 100, (px / 24) * 100]),
    { command: "layer.setSwitch", params: { layers: ["mark"], switch: "collapse", value: true } },
  ];

  // The prompt is typed into the input box first (the hint hides while it's there), then sent: the box clears and the
  // prompt pops in as a bubble at the top. The tool call and the reply follow.
  const round = (v) => Math.round(v * 100) / 100;
  const typeFrom = 0.3, cps = 32, sent = round(typeFrom + prompt.length / cps + 0.35);
  const typedInInput = (name, x, y, fill) => [
    text(name, " ", x, y, { size: 22, fill }),
    expr(name, "text/sourceText", [
      `var s = String(thisComp.layer("prompt").text.sourceText);`,
      `time >= ${round(sent)} ? "" : s.slice(0, Math.max(0, Math.floor((time - ${typeFrom}) * ${cps})))`,
    ].join("\n")),
    expr("input hint", "transform/opacity", `time < ${typeFrom} || time >= ${round(sent)} ? 100 : 0`),
  ];

  // ---- Claude Code ----
  {
    const name = "claudeCode";
    const steps = [
      { command: "comp.new", params: { name, width: 1920, height: 1080, frameRate: 30, duration: 6, open: true } },
      ...rect("window", L + W / 2, T + H / 2, W, H, "#F0ECE0", { stroke: "#DCD4C2", round: 18 }),
      ...rect("sidebar", L + side / 2, T + H / 2, side, H, "#EAE4D3", { round: 18 }),
      ...rect("sidebar edge", L + side - 10, T + H / 2, 20, H, "#EAE4D3"),
      ...rect("sidebar line", L + side, T + H / 2, 2, H, "#DCD4C2"),
      ...brandMark("claude.svg", L + 46, T + 58, 30),
      text("brand", "Claude", L + 70, T + 66, { font: "Georgia", style: "Regular", size: 30 }),
      text("new plus", "+", L + 32, T + 125, { size: 24, fill: "#c96442" }),
      text("new session", "New session", L + 58, T + 125, { fill: "#3d3a35" }),
      text("chats", "Chats", L + 32, T + 175, { fill: "#5b5950" }),
      ...rect("code pill", L + side / 2, T + 217, side - 30, 42, "#DFD9C8", { round: 8 }),
      text("code", "Code", L + 32, T + 225, { style: "Bold", fill: "#1a1a18" }),
      text("recents", "Recents", L + 32, T + 285, { size: 18, fill: "#8a8780" }),
      text("recent 1", "X inbox follow-ups", L + 32, T + 330, { fill: "#3d3a35" }),
      text("recent 2", "Marketplace listings", L + 32, T + 375, { fill: "#5b5950" }),
      text("recent 3", "Group listening", L + 32, T + 420, { fill: "#5b5950" }),
      text("path", "▢  your-marketing      ⑂  main", feedX, T + 42, { font: "Segoe UI", style: "Regular", size: 20, fill: "#5b5950" }),
      ...rect("top line", L + side + (W - side) / 2, T + 65, W - side, 2, "#DCD4C2"),
      // The prompt: a bubble on the right that pops in, then the text types.
      ...rect("prompt bubble", feedX + feedW - 240, T + 125, 480, 58, "#E5E0D6", { round: 26 }),
      text("prompt", prompt, feedX + feedW - 240, T + 133, { justify: "center", size: 23 }),
      parent("prompt", "prompt bubble"),
      pop("prompt bubble", sent),
      // The log tool call card.
      ...rect("tool card", feedX + feedW / 2, T + 250, feedW, 140, "#F7F5EF", { stroke: "#E5E0D6", round: 12 }),
      text("tool name", "log · twitterDms", feedX + 24, T + 215, { size: 21 }),
      text("tool args", toolArgs, feedX + 230, T + 215, { ...mono, fill: "#8a8780" }),
      text("tool check", "✓", feedX + feedW - 36, T + 215, { font: "Segoe UI Symbol", style: "Regular", size: 22, fill: "#5a8a3c" }),
      ...rect("tool line", feedX + feedW / 2, T + 232, feedW, 2, "#E5E0D6"),
      ...toolLines.map((line, k) => text(`tool result ${k + 1}`, line, feedX + 24, T + 262 + k * 25, { ...mono, fill: "#5b5950" })),
      ...["tool name", "tool args", "tool check", "tool line", "tool result 1", "tool result 2", "tool result 3"].map((child) => parent(child, "tool card")),
      pop("tool card", sent + 0.5),
      // The reply types on word by word.
      text("reply", reply, feedX, T + 360, { font: "Georgia", style: "Regular", size: 24, box: [feedX, T + 340, feedW, 110] }),
      type("reply", sent + 1.3, 9, true),
      // The input box.
      ...rect("input", feedX + feedW / 2, T + H - 80, feedW, 100, "#FFFFFF", { stroke: "#E5E0D6", round: 24 }),
      text("input hint", "Reply to Claude…", feedX + 24, T + H - 100, { fill: "#9a9893" }),
      ...typedInInput("input typing", feedX + 24, T + H - 100, "#1a1a18"),
      text("input plus", "+", feedX + 24, T + H - 52, { size: 24, fill: "#5b5950" }),
      text("model", "Opus 5.5  ▾", feedX + feedW - 170, T + H - 52, { size: 20 }),
      ...rect("send", feedX + feedW - 40, T + H - 60, 40, 40, "#c96442", { round: 8 }),
      text("send arrow", "↑", feedX + feedW - 40, T + H - 52, { font: "Segoe UI Symbol", style: "Regular", size: 22, fill: "#FFFFFF", justify: "center" }),
      { command: "essential.setName", params: { comp: name, name } },
      essText(name, "prompt", "Prompt"),
      essText(name, "tool name", "Tool"),
      essText(name, "reply", "Reply"),
    ];
    mkdirSync(`effects/${name}`, { recursive: true });
    writeFileSync(`effects/${name}/effect.json`, JSON.stringify(steps, null, 2) + "\n");
  }

  // ---- Codex ----
  {
    const name = "codex";
    const steps = [
      { command: "comp.new", params: { name, width: 1920, height: 1080, frameRate: 30, duration: 6, open: true } },
      ...rect("window", L + W / 2, T + H / 2, W, H, "#FFFFFF", { stroke: "#e5e5e5", round: 18 }),
      ...rect("sidebar", L + side / 2, T + H / 2, side, H, "#f9f9f9", { round: 18 }),
      ...rect("sidebar edge", L + side - 10, T + H / 2, 20, H, "#f9f9f9"),
      ...rect("sidebar line", L + side, T + H / 2, 2, H, "#ececec"),
      ...brandMark("codex.svg", L + 46, T + 58, 30),
      text("brand", "Codex", L + 72, T + 66, { style: "Bold", size: 24, fill: "#0d0d0d" }),
      text("new thread", "✎  New thread", L + 32, T + 125, { font: "Segoe UI", style: "Regular", fill: "#0d0d0d" }),
      text("project", "your-marketing", L + 32, T + 185, { size: 18, fill: "#8f8f8f" }),
      ...rect("recent pill", L + side / 2, T + 222, side - 30, 42, "#ececec", { round: 10 }),
      text("recent 1", "Answer my X DMs", L + 32, T + 230, { fill: "#0d0d0d" }),
      text("recent 2", "Post the listings", L + 32, T + 275, { fill: "#5d5d5d" }),
      text("recent 3", "Read the groups", L + 32, T + 320, { fill: "#5d5d5d" }),
      text("thread", "Answer my X DMs", feedX, T + 42, { size: 20, fill: "#0d0d0d" }),
      text("branch", "⑂  main", feedX + feedW, T + 42, { font: "Segoe UI", style: "Regular", size: 20, fill: "#8f8f8f", justify: "right" }),
      ...rect("top line", L + side + (W - side) / 2, T + 65, W - side, 2, "#ececec"),
      ...rect("prompt bubble", feedX + feedW - 240, T + 125, 480, 58, "#f3f3f3", { round: 29 }),
      text("prompt", prompt, feedX + feedW - 240, T + 133, { justify: "center", size: 23, fill: "#0d0d0d" }),
      parent("prompt", "prompt bubble"),
      pop("prompt bubble", sent),
      // "Called log.twitterDms" with its result box.
      ...rect("tool", feedX + feedW / 2, T + 262, feedW, 150, "#FFFFFF"),
      text("tool called", ">_  Called", feedX, T + 205, { font: "JetBrains Mono", style: "Regular", size: 19, fill: "#5d5d5d" }),
      ...rect("tool chip", feedX + 290, T + 198, 230, 32, "#f3f3f3", { round: 6 }),
      text("tool name", "log.twitterDms", feedX + 290, T + 205, { ...mono, justify: "center", fill: "#0d0d0d" }),
      ...rect("tool box", feedX + feedW / 2, T + 285, feedW, 112, "#f9f9f9", { round: 14 }),
      text("tool args", toolArgs, feedX + 18, T + 252, { ...mono, fill: "#8f8f8f" }),
      ...toolLines.map((line, k) => text(`tool result ${k + 1}`, line, feedX + 18, T + 277 + k * 24, { ...mono, fill: "#5d5d5d" })),
      ...["tool called", "tool chip", "tool name", "tool box", "tool args", "tool result 1", "tool result 2", "tool result 3"].map((child) => parent(child, "tool")),
      pop("tool", sent + 0.5),
      text("reply", reply, feedX, T + 380, { style: "Regular", size: 23, fill: "#0d0d0d", box: [feedX, T + 360, feedW, 110] }),
      type("reply", sent + 1.3, 9, true),
      ...rect("input", feedX + feedW / 2, T + H - 70, feedW, 72, "#FFFFFF", { stroke: "#e5e5e5", round: 36 }),
      text("input plus", "+", feedX + 28, T + H - 61, { size: 24, fill: "#5d5d5d" }),
      text("input hint", "Ask Codex anything", feedX + 62, T + H - 62, { fill: "#8f8f8f" }),
      ...typedInInput("input typing", feedX + 62, T + H - 62, "#0d0d0d"),
      ...rect("send", feedX + feedW - 40, T + H - 70, 44, 44, "#0d0d0d", { round: 22 }),
      text("send arrow", "↑", feedX + feedW - 40, T + H - 62, { font: "Segoe UI Symbol", style: "Regular", size: 22, fill: "#FFFFFF", justify: "center" }),
      { command: "essential.setName", params: { comp: name, name } },
      essText(name, "prompt", "Prompt"),
      essText(name, "tool name", "Tool"),
      essText(name, "reply", "Reply"),
    ];
    mkdirSync(`effects/${name}`, { recursive: true });
    writeFileSync(`effects/${name}/effect.json`, JSON.stringify(steps, null, 2) + "\n");
  }

  // ---- Terminal ----
  // The Claude Code CLI window from the rea-looksmaxxing project (log-hyperframes/effectcraft/scene2/assets.html,
  // #window): a near-black window with a title bar and traffic lights, the orange-bordered "Welcome to Claude Code"
  // box, then the session in JetBrains Mono: the prompt typed after ">", an orange ● tool line, a grey └ result and a
  // blue ● reply.
  {
    const name = "terminal";
    const left = 260, top = 130, width = 1400, height = 820;
    const consolas = { font: "Consolas", style: "Regular", size: 22 };
    const cw = 22 * 0.5498; // Consolas advance at 22 px
    const bodyX = 300, line = { font: "JetBrains Mono", style: "Regular", size: 30 };
    const typeAt = 0.5, typeRate = 40;
    const ask = `> ${prompt}`;
    const shown = round(typeAt + ask.length / typeRate + 0.4);
    const steps = [
      { command: "comp.new", params: { name, width: 1920, height: 1080, frameRate: 30, duration: 6, open: true } },
      ...rect("window", 960, 540, width, height, "#0d1117", { stroke: "#2a3442", round: 22 }),
      ...rect("bar", 960, top + 27, width, 54, "#161b22", { round: 22 }),
      ...rect("bar square", 960, top + 41, width, 26, "#161b22"),
      ...rect("bar line", 960, top + 54, width, 2, "#222b37"),
      ...["#ff5f57", "#febc2e", "#28c840"].map((fill, k) => [
        { command: "layer.newShape", params: { kind: "ellipse", name: `light ${k + 1}`, size: [16, 16], fill: hex(fill), position: [left + 30 + k * 28, top + 27] } },
      ]).flat(),
      text("title", "matt — claude — ~/log", 960, top + 34, { ...consolas, size: 20, fill: "#8b98a9", justify: "center" }),
      ...rect("welcome", 960, top + 54 + 30 + 75, width - 72, 150, "#0d1117", { stroke: "#d97757", round: 12 }),
      text("welcome star", "✻", left + 64, top + 122, { ...consolas, style: "Bold", fill: "#d97757" }),
      text("welcome to", "Welcome to", left + 64 + 2 * cw, top + 122, { ...consolas, style: "Bold", fill: "#c9d1d9" }),
      text("welcome claude", "Claude Code", left + 64 + 13 * cw, top + 122, { ...consolas, style: "Bold", fill: "#d97757" }),
      text("welcome bang", "!", left + 64 + 24 * cw, top + 122, { ...consolas, style: "Bold", fill: "#c9d1d9" }),
      text("welcome help", "/help for help, /status for your current setup", left + 64, top + 157, { ...consolas, fill: "#7d8590" }),
      text("welcome cwd", "cwd: ~/your-marketing", left + 64, top + 192, { ...consolas, fill: "#7d8590" }),
      // The session.
      text("prompt", ask, bodyX, 430, { ...line, fill: "#f2f5fa" }),
      type("prompt", typeAt, typeRate),
      text("tool", "● log · twitterDms (account=you, waiting=true)", bodyX, 500, { ...line, fill: "#d98766" }),
      appearAt("tool", shown),
      text("result", "  └ 6 conversations waiting on a reply, newest first", bodyX, 546, { ...line, fill: "#99a6b8" }),
      appearAt("result", round(shown + 0.15)),
      text("reply", "● 6 people are waiting on you, 2 more opened and didn’t reply", bodyX, 616, { ...line, fill: "#2a8cff" }),
      appearAt("reply", round(shown + 0.4)),
    ];
    // Everything rides on the window, which pops in.
    const children = ["bar", "bar square", "bar line", "light 1", "light 2", "light 3", "title", "welcome", "welcome star", "welcome to", "welcome claude", "welcome bang", "welcome help", "welcome cwd", "prompt", "tool", "result", "reply"];
    steps.push(
      ...children.map((child) => parent(child, "window")),
      pop("window", 0),
      { command: "essential.setName", params: { comp: name, name } },
      essText(name, "prompt", "Prompt"),
      essText(name, "tool", "Tool"),
      essText(name, "result", "Result"),
      essText(name, "reply", "Reply"),
    );
    mkdirSync(`effects/${name}`, { recursive: true });
    writeFileSync(`effects/${name}/effect.json`, JSON.stringify(steps, null, 2) + "\n");
  }
}
