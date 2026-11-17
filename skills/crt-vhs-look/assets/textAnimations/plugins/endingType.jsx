// The launch film's ending as type only (matt, 2026-11-15: the 3D terminal / research cards "don't match what we're
// doing"). Clears the comp "ending" of every card, camera and backdrop, and leaves: black, the VO captions (made by
// plugins/launchCaptions.jsx, kept if they're there), the CRT-Emulator build (style 10, as cyberpunk) over them, the
// thermogram flash in from cyberpunk and into the end card, and the end card ("ending card": the Nous and Log logos).
// Run after endingTerminal.jsx (which builds "ending" and "ending card") and before launchCaptions.jsx.
//   effectcraft-cli --project textAnimations.ecproj script plugins/endingType.jsx --save
#include "CRTemulator/jsx/crtEmulator.jsx"
var ROOT="C:/Users/0/.buzz/REPOS/listeningkit-templates/", F=30;
var CARD_AT=58.30-37.43;   // the end card, in the ending's own time
function findComp(n){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof CompItem && it.name===n) return it;} return null; }
function byName(c,n){ for (var k=1;k<=c.numLayers;k++) if(c.layer(k).name===n) return c.layer(k); return null; }
function P(e,path){ var s=path.split("/"); var p=e; for(var i=0;i<s.length;i++){ p=p.property(s[i]); if(!p) throw new Error("no "+path); } return p; }
var E=findComp("ending"); if(!E) throw new Error("no comp ending: run plugins/endingTerminal.jsx first");
var DUR=E.duration;
// everything but the end card and the captions goes
for (var k=E.numLayers;k>=1;k--){ var l=E.layer(k); if(l.name==="ending card" || /^cap /.test(l.name)) continue; l.remove(); }
var card=byName(E,"ending card");
var bg=E.layers.addSolid([0,0,0],"black",1920,1080,1); bg.startTime=0; bg.inPoint=0; bg.outPoint=DUR; bg.moveToEnd();
if(card) card.moveBefore(bg);

// the CRT over all of it, as cyberpunk (applyCyberpunk.jsx)
var AE={
  "ADBE Glo2":["Glow Based On","Glow Threshold","Glow Radius","Glow Intensity","Composite Original","Glow Operation","Glow Colors","Color Looping","Color Loops","Color Phase","A & B Midpoint","Color A","Color B","Glow Dimensions"],
  "ADBE Displacement Map":["Displacement Map Layer","Use For Horizontal Displacement","Max Horizontal Displacement","Use For Vertical Displacement","Max Vertical Displacement","Displacement Map Behavior","Wrap Pixels Around","Expand Output"],
  "ADBE Wave Warp":["Wave Type","Wave Height","Wave Width","Direction","Wave Speed","Pinning","Phase",null],
  "ADBE Easy Levels2":["Channel",null,"Input Black","Input White","Gamma","Output Black","Output White"],
  "ADBE HUE SATURATION":["Channel Control",null,"Master Hue","Master Saturation","Master Lightness","Colorize","Colorize Hue","Colorize Saturation","Colorize Lightness"]
};
var AE_IDS={"VISINF Grain Implant-0008":["Tweaking","Intensity"]};
var AE_EFFECTS={"CC Lens":"ec.distort.cclens","CC Power Pin":"ADBE Corner Pin"};
var noop={setValue:function(){},setValueAtTime:function(){},expression:"",name:"(none in EffectCraft)"};
var proto=Object.getPrototypeOf(E.layer(1).property("ADBE Effect Parade"));
var ecProperty=proto.property, ecAddProperty=proto.addProperty;
proto.property=function(x){
  var table=AE[this.matchName];
  if(table && typeof x==="number" && x>=1 && x<=table.length){ if(table[x-1]===null) return noop; x=table[x-1]; }
  if(typeof x==="string" && AE_IDS[x]){ var p=this; for (var i=0;i<AE_IDS[x].length;i++){ p=ecProperty.call(p,AE_IDS[x][i]); if(!p) return noop; } return p; }
  var r=ecProperty.call(this,x);
  return (r===null||r===undefined)&&typeof x==="string"&&/^VISINF Grain Implant-\d+$/.test(x)?noop:r;
};
proto.addProperty=function(x){ return ecAddProperty.call(this,AE_EFFECTS[x]||x); };
E.openInViewer();
for (var k=1;k<=E.numLayers;k++) E.layer(k).selected=false;
E.layer(1).selected=true;
var res=applyClick("/"+ROOT+"textAnimations/plugins/CRTemulator","10");
proto.property=ecProperty; proto.addProperty=ecAddProperty;
var pt=byName(E,"Posterize Time"); if(pt) pt.enabled=false;
// the CRT takes its span from the layer it was applied to: make every CRT layer run the whole ending
for (var k=1;k<=E.numLayers;k++){ var l=E.layer(k); if(l.name==="black"||l.name==="ending card"||/^cap /.test(l.name)) continue;
  l.startTime=0; l.inPoint=0; l.outPoint=DUR; }

// the thermogram: in from cyberpunk, and into the end card
var CUTS="[0.0000,"+CARD_AT.toFixed(4)+"]";
var LOOK="var cuts="+CUTS+",pat={'-2':'o','-1':'g','0':'o','2':'g','3':'o'},look='';for(var i=0;i<cuts.length;i++){var f=Math.round((time-cuts[i])*30);if(pat[String(f)])look=pat[String(f)];}";
var X=E.layers.addSolid([0,0,0],"exposure cuts",1920,1080,1); X.adjustmentLayer=true; X.startTime=0; X.inPoint=0; X.outPoint=DUR;
P(X.property("Effects").addProperty("ec.color.exposure"),"master/exposure").expression="var cuts="+CUTS+";var env=0,th=0;for(var i=0;i<cuts.length;i++){var d=time-cuts[i],p=-1,f=Math.round(d*30);if(f>=-2&&f<=3&&f!==1)th=1;if(d>-.3&&d<=0)p=(d+.3)/.3;else if(d>0&&d<.4)p=1-d/.4;if(p>=0){p=p*p*(3-2*p);env=Math.max(env,p);}}th?0.35*env:3.6*env";
X.moveToBeginning();
var LUTS={"thermal orange":["thermograph_orange","o"],"thermal green":["thermograph_green","g"]};
for (var n in LUTS){ var T=E.layers.addSolid([0,0,0],n,1920,1080,1); T.adjustmentLayer=true; T.startTime=0; T.inPoint=0; T.outPoint=DUR;
  P(T.property("Effects").addProperty("ec.utility.applylut"),"lut").setValue(ROOT+"textAnimations/assets/luts/"+LUTS[n][0]+".cube");
  T.property("Transform").property("Opacity").expression=LOOK+"look==='"+LUTS[n][1]+"'?100:0"; T.moveToBeginning(); }
writeLn("ending: type on black under the CRT ("+res+"), thermogram in and into the end card; "+E.numLayers+" layers");
