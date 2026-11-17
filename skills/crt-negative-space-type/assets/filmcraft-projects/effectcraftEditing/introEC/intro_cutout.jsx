// matt, 2026-11-16: the full background video behind him, the dark gradient over it, and him cut out on a layer above
// the gradient, in frame for the whole intro (not just the face shots): (1) the plate is the screen-only plate
// (intro_screen.mp4: the edit with the camera track off); (2) "matt N" layers: his cutout for each intro line
// (cutouts/beat_NN/, make_face_cutouts.py, the camera at the same timestamps as his words), scale 225%, position
// 1442,270 (face centre ~1350 px: the text has the left, he has the right), above the gradient, under the lines, the
// type and the CRT. Rerun replaces the "matt N" / "face N" layers.
var D="C:/Users/0/filmcraft/projects/effectcraftEditing/introEC/";
function findComp(n){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof CompItem && it.name===n) return it;} return null; }
function byName(c,n){ for (var k=1;k<=c.numLayers;k++) if(c.layer(k).name===n) return c.layer(k); return null; }
var f=new File(D+"beats.json"); f.open("r"); var beats=JSON.parse(f.read()); f.close();
var C=findComp("intro"); if(!C) throw new Error("no comp intro");
var plate=byName(C,"plate");
if(!/intro_screen\.mp4$/.test(plate.source.file.fsName.replace(/\\/g,"/")))
  plate.replaceSource(app.project.importFile(new ImportOptions(new File(D+"intro_screen.mp4"))), false);
for (var k=C.numLayers;k>=1;k--) if(/^(face|matt) \d+$/.test(C.layer(k).name)) C.layer(k).remove();
var grad=byName(C,"left gradient");
for (var j=0;j<beats.length;j++){
  var o=new ImportOptions(new File(D+"cutouts/beat_"+("0"+(j+1)).slice(-2)+"/c_000.png")); o.sequence=true;
  var seq=app.project.importFile(o); seq.mainSource.conformFrameRate=30;
  var L=C.layers.add(seq); L.name="matt "+(j+1);
  L.startTime=beats[j].p0; L.inPoint=beats[j].p0; L.outPoint=beats[j].p1;
  L.property("Transform").property("Scale").setValue([225,225]);
  L.property("Transform").property("Position").setValue([1442,270]);
  L.moveBefore(grad);
}
for (var k=1;k<=C.numLayers;k++) if(/^(matt|left|plate|red|screen|cut)/.test(C.layer(k).name)) writeLn("  "+k+" "+C.layer(k).name);
