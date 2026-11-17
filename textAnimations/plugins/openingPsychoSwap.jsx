// Swap the cyberpsycho clip inside the opener (matt, 2026-11-15) without rebuilding anything else: the pre-comp
// "opening NN opening_psycho_vX" in comp "opening" gets the new render (CLIP below) as its source, and is renamed to
// match, so the inserts, the VHS look and the CRT stay as they are.
//   effectcraft-cli --project textAnimations.ecproj script plugins/openingPsychoSwap.jsx --save
var CLIP="C:/Users/0/.buzz/REPOS/listeningkit-templates/textAnimations/assets/collage/opening_psycho_v9.mp4";
function findFile(path){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof FootageItem && it.file && it.file.fsName.replace(/\\/g,"/").toLowerCase()===path.toLowerCase()) return it;} return null; }
var pre=null;
for (var i=1;i<=app.project.numItems;i++){ var it=app.project.item(i); if(it instanceof CompItem && it.name.indexOf("opening ")===0 && it.name.indexOf("opening_psycho_v")>0) pre=it; }
if(!pre) throw new Error("no opening psycho pre-comp");
var foot=findFile(CLIP)||app.project.importFile(new ImportOptions(new File(CLIP)));
var L=pre.layer(1), was=L.name;
L.replaceSource(foot,false);
var tag=CLIP.substring(CLIP.lastIndexOf("/")+1).replace(".mp4","");
L.name=tag;
var oldName=pre.name; pre.name=oldName.replace(/opening_psycho_v\d+/,tag);
var O=null; for (var i=1;i<=app.project.numItems;i++){ var it=app.project.item(i); if(it instanceof CompItem && it.name==="opening") O=it; }
for (var k=1;k<=O.numLayers;k++) if(O.layer(k).name===oldName) O.layer(k).name=pre.name;
writeLn("swapped "+was+" -> "+tag+" in '"+pre.name+"' ("+Math.round(L.inPoint*30)+"-"+Math.round(L.outPoint*30)+", source "+foot.duration.toFixed(3)+"s)");
