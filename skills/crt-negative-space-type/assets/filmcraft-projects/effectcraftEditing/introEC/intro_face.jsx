// matt, 2026-11-16: the full-frame shots of him fill the scene: the camera cutaways (face_cuts.json, from
// effectcraftEditing-camera-20min-v10.json) as their own layers ABOVE the left gradient (so it only darkens the screen
// recording), under the red lines and the type, and under the CRT; in the edit's bust framing (scale 225%, position
// 1052,270, the same as FilmCraft's camera clips). The thermogram looks and the cut tear move above them so they hit
// the face too. Rerun replaces the "face N" layers.
var CAM="C:/Users/0/AppData/Roaming/so.cap.desktop/recordings/Generic PnP Monitor (Display) 2026-11-16 03.27 PM.cap/content/segments/segment-0/camera.mp4";
// [comp start s, comp end s, camera source in s] (60 fps frames / 60)
var CUTS=[[5.95,7.4667,235.0],[7.4667,9.7667,2219.85],[9.7667,11.55,3347.15],[14.6667,16.1333,3912.1833]];
function findComp(n){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof CompItem && it.name===n) return it;} return null; }
function byName(c,n){ for (var k=1;k<=c.numLayers;k++) if(c.layer(k).name===n) return c.layer(k); return null; }
var C=findComp("intro"); if(!C) throw new Error("no comp intro");
for (var k=C.numLayers;k>=1;k--) if(/^face \d+$/.test(C.layer(k).name)) C.layer(k).remove();
var cam=null; for (var i=1;i<=app.project.numItems;i++){ var it=app.project.item(i); if(it instanceof FootageItem && it.file && /camera\.mp4$/i.test(it.file.fsName)) cam=it; }
if(!cam) cam=app.project.importFile(new ImportOptions(new File(CAM)));
var grad=byName(C,"left gradient"), lines=byName(C,"red lines");
for (var j=0;j<CUTS.length;j++){
  var c=CUTS[j], L=C.layers.add(cam); L.name="face "+(j+1);
  L.startTime=c[0]-c[2]; L.inPoint=c[0]; L.outPoint=c[1];
  L.property("Transform").property("Scale").setValue([225,225]);
  L.property("Transform").property("Position").setValue([1052,270]);
  if(L.hasAudio) L.audioEnabled=false;
  L.moveBefore(grad);
}
var ADJ=["cut displace","screen thermal green","screen thermal orange"];
for (var a=0;a<ADJ.length;a++){ var l=byName(C,ADJ[a]); if(l) l.moveAfter(lines); }
for (var k=1;k<=C.numLayers;k++) if(!/^(CRT|card|Global|Lens|Monitor|CC|Posterize|Position|Channel|Glitch|Distort|Glow|thermal|exposure)/.test(C.layer(k).name)) writeLn("  "+k+" "+C.layer(k).name);
