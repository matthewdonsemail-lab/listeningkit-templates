// The cold open's transitions (matt, 2026-11-16): the frames make_intro_transitions.py made (trans/cuts.json: the launch
// film ending's clip blend + pixel sort, or the red flash on every third cut) as "intro trans N" layers on every card
// change, over everything, under the CRT, as plugins/endingTransitions.jsx places the ending's. Rerun replaces them.
var DIR="C:/Users/0/filmcraft/projects/effectcraftEditing/introEC/trans/", F=30;
var LOOK=/^(thermal |exposure cuts|Global Scale|Lens Distortions|Monitor|CRT|Channel Blur|CC|CC 2|Posterize Time|Position Flicker|Glitches|Distortions|Glow)/;
function findComp(n){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof CompItem && it.name===n) return it;} return null; }
function readJson(p){ var f=new File(p); f.open("r"); var t=f.read(); f.close(); return JSON.parse(t); }
var C=findComp("intro"); if(!C) throw new Error("no comp intro");
for (var k=C.numLayers;k>=1;k--) if(/^intro trans /.test(C.layer(k).name)) C.layer(k).remove();
var under=null; for (var k=1;k<=C.numLayers;k++) if(LOOK.test(C.layer(k).name)) under=C.layer(k);
var cuts=readJson(DIR+"cuts.json");
for (var i=0;i<cuts.length;i++){ var c=cuts[i];
  var o=new ImportOptions(new File(c.path)); o.sequence=true;
  var ft=app.project.importFile(o); ft.mainSource.conformFrameRate=F;
  var L=C.layers.add(ft); L.name="intro trans "+(i+1)+" "+c.kind;
  L.startTime=c.first/F; L.inPoint=c.first/F; L.outPoint=(c.first+c.n)/F;
  if(under) L.moveAfter(under); else L.moveToBeginning();
}
writeLn("intro: "+cuts.length+" transitions");
