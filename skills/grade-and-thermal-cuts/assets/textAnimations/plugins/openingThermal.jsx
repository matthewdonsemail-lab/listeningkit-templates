// The opener's scene switches after the drop (matt, 2026-11-15) as thermogram transitions, the way cyberpunk's match
// cut does it (cyberpunkEyes.jsx, thermalCuts.jsx in Intro 1): frames -2 orange, -1 green, 0 orange, +1 picture,
// +2 green, +3 orange (the thermograph LUTs, assets/luts/), inside an exposure blow-out. On top of everything in
// "opening", the CRT included. The switches (timeline seconds): the drop into young Sam (10:08), Sam into young Dario,
// Dario back into the inside scene (make_opening_psycho_cut.py, 4 beats of 0.39 s each).
// Run last: after openingDawn.jsx, openingInserts.jsx and CRTemulator/applyOpening.jsx (which clears these layers).
//   effectcraft-cli --project textAnimations.ecproj script plugins/openingThermal.jsx --save
var ROOT="C:/Users/0/.buzz/REPOS/listeningkit-templates/";
var DROP=308/30, BEAT=0.39;
// the drop only (matt, 2026-11-15: the alternating cut again, no Sam / Dario sections to switch between)
var CUTS="["+[DROP].map(function(v){return v.toFixed(4);}).join(",")+"]";
function findComp(n){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof CompItem && it.name===n) return it;} return null; }
function byName(c,n){ for (var k=1;k<=c.numLayers;k++) if(c.layer(k).name===n) return c.layer(k); return null; }
function P(e,path){ var s=path.split("/"); var p=e; for(var i=0;i<s.length;i++){ p=p.property(s[i]); if(!p) throw new Error("no "+path); } return p; }
var C=findComp("opening"); if(!C) throw new Error("no comp opening");
var olds=["exposure cuts","thermal orange","thermal green"];
for (var i=0;i<olds.length;i++){ var l=byName(C,olds[i]); if(l) l.remove(); }
var DUR=C.duration;
var LOOK="var cuts="+CUTS+",pat={'-2':'o','-1':'g','0':'o','2':'g','3':'o'},look='';for(var i=0;i<cuts.length;i++){var f=Math.round((time-cuts[i])*30);if(pat[String(f)])look=pat[String(f)];}";
var X=C.layers.addSolid([0,0,0],"exposure cuts",1920,1080,1); X.adjustmentLayer=true; X.startTime=0; X.inPoint=0; X.outPoint=DUR;
var ex=X.property("Effects").addProperty("ec.color.exposure");
P(ex,"master/exposure").expression="var cuts="+CUTS+";var env=0,th=0;for(var i=0;i<cuts.length;i++){var d=time-cuts[i],p=-1,f=Math.round(d*30);if(f>=-2&&f<=3&&f!==1)th=1;if(d>-.3&&d<=0)p=(d+.3)/.3;else if(d>0&&d<.4)p=1-d/.4;if(p>=0){p=p*p*(3-2*p);env=Math.max(env,p);}}th?0.35*env:3.6*env";
X.moveToBeginning();
var LUTS={"thermal orange":["thermograph_orange","o"],"thermal green":["thermograph_green","g"]};
for (var n in LUTS){
  var T=C.layers.addSolid([0,0,0],n,1920,1080,1); T.adjustmentLayer=true; T.startTime=0; T.inPoint=0; T.outPoint=DUR;
  var lut=T.property("Effects").addProperty("ec.utility.applylut");
  P(lut,"lut").setValue(ROOT+"textAnimations/assets/luts/"+LUTS[n][0]+".cube");
  T.property("Transform").property("Opacity").expression=LOOK+"look==='"+LUTS[n][1]+"'?100:0";
  T.moveToBeginning();
}
writeLn("opening: thermogram transitions at "+CUTS+" s");
