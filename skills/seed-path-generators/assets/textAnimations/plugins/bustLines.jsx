// The busts scene with its cyberpsycho lines (matt, 2026-11-15): puts assets/collage/bust_lines.mp4 (made by
// assets/make_bust_lines.py: each bust's line wiping round him, then the face glitch and the flicking between his
// realistic / low-poly / dither versions) on top of the comp "outro portraits", over its six still portraits (switched
// off, kept), so the outro's timing, the CRT and everything above stay as they are. Rerun to swap in a new render.
//   File > Scripts > Run Script File... > plugins/bustLines.jsx
var CLIP="C:/Users/0/.buzz/REPOS/listeningkit-templates/textAnimations/assets/collage/bust_lines.mp4";
function findComp(n){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof CompItem && it.name===n) return it;} return null; }
function findFile(path){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof FootageItem && it.file && it.file.fsName.replace(/\\/g,"/").toLowerCase()===path.toLowerCase()) return it;} return null; }
var P=findComp("outro portraits"); if(!P) throw new Error("no comp 'outro portraits'");
for (var k=P.numLayers;k>=1;k--) if(P.layer(k).name==="bust lines") P.layer(k).remove();
var foot=findFile(CLIP); if(foot) foot.replace(new File(CLIP)); else foot=app.project.importFile(new ImportOptions(new File(CLIP)));
var L=P.layers.add(foot); L.name="bust lines"; L.startTime=0; L.inPoint=0; L.outPoint=P.duration; L.moveToBeginning();
for (var k=1;k<=P.numLayers;k++) if(/^portrait /.test(P.layer(k).name)) P.layer(k).enabled=false;
writeLn("outro portraits: bust lines on top ("+foot.duration.toFixed(2)+" s), portraits off");
