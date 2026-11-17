// The launch opener's insert shots (matt, 2026-11-15): three 4-frame cutaways of a hand clicking a mouse / a finger
// pressing a key, from the style reference (projects/opening/ref/styleref.mp4, 640x268, 23.976 fps), at the moments
// the stills on either side are sent:
//   2.60 s (frame 78)   mouse click (styleref 52.09 s)   the playground prompt goes to Submit, before the cut to the chat (2.73 s)
//   3.58 s (frame 107)  finger press (styleref 26.40 s)  "my names sam whats your name?" sends, before the cut at 3.63 s
//   7.95 s (frame 238)  mouse click again (52.09 s)       on "Can I trust you?" (7.17-8.43 s)
// Each layer is the reference itself, scaled to fill the frame height (it is 2.39:1, the opener before the drop is
// 4:3 between the side bars), its sound off. Named "opening insert ..." so applyOpening.jsx keeps them under the VHS
// look. Run after plugins/openingDawn.jsx (which clears "opening") and before plugins/CRTemulator/applyOpening.jsx.
var F=30, LEN=4, SRC="C:/Users/0/.buzz/REPOS/listeningkit-templates/projects/opening/ref/styleref.mp4";
var INSERTS=[
  {name:"opening insert 1 mouse click", at:78,  src:52.09},
  {name:"opening insert 2 finger press", at:107, src:26.40},
  {name:"opening insert 3 mouse click", at:238, src:52.09}
];
function findCompByName(n){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof CompItem && it.name===n) return it;} return null; }
function findFile(path){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof FootageItem && it.file && it.file.fsName.replace(/\\/g,"/").toLowerCase()===path.toLowerCase()) return it;} return null; }
var comp=findCompByName("opening"); if(!comp) throw new Error("no comp opening");
for (var k=comp.numLayers;k>=1;k--) if(comp.layer(k).name.indexOf("opening insert ")===0) comp.layer(k).remove();
var foot=findFile(SRC)||app.project.importFile(new ImportOptions(new File(SRC)));
var fill=100*1080/foot.height;
for (var i=0;i<INSERTS.length;i++){ var s=INSERTS[i];
  var L=comp.layers.add(foot); L.name=s.name;
  L.startTime=s.at/F-s.src; L.inPoint=s.at/F; L.outPoint=(s.at+LEN)/F;
  try{ L.audioEnabled=false; }catch(x){}
  L.property("Transform").property("Position").setValue([960,540]);
  L.property("Transform").property("Scale").setValue([fill,fill]);
  L.moveToBeginning();
  writeLn(s.name+": frames "+s.at+"-"+(s.at+LEN)+", styleref "+s.src.toFixed(2)+"s, scale "+fill.toFixed(1)+"%"); }
