// cyberpunk: the CRT-Emulator plug-in's own build (style 10), the same look Intro 1 has, on top of the cyberpunk
// pre-comp. Run after plugins/cyberpunkEyes.jsx (which rebuilds the comp from scratch). As applyIntro1.jsx: the
// plug-in's ExtendScript unchanged, its Apply button's applyClick() called directly, AE effect indices mapped to
// EffectCraft's names. No Posterize Time here: its layer is switched off. The thermogram flash goes back on top of
// the CRT, as in Intro 1.
#include "jsx/crtEmulator.jsx"

function findCompByName(n){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof CompItem && it.name===n) return it;} return null; }
function layerNamed(c,n){ for (var k=1;k<=c.numLayers;k++) if(c.layer(k).name===n) return c.layer(k); return null; }
var comp=findCompByName("cyberpunk");

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
var proto=Object.getPrototypeOf(comp.layer(1).property("ADBE Effect Parade"));
var ecProperty=proto.property, ecAddProperty=proto.addProperty;
proto.property=function(x){
  var table=AE[this.matchName];
  if(table && typeof x==="number" && x>=1 && x<=table.length){ if(table[x-1]===null) return noop; x=table[x-1]; }
  if(typeof x==="string" && AE_IDS[x]){ var p=this; for (var i=0;i<AE_IDS[x].length;i++){ p=ecProperty.call(p,AE_IDS[x][i]); if(!p) return noop; } return p; }
  var r=ecProperty.call(this,x);
  return (r===null||r===undefined)&&typeof x==="string"&&/^VISINF Grain Implant-\d+$/.test(x)?noop:r;
};
proto.addProperty=function(x){ return ecAddProperty.call(this,AE_EFFECTS[x]||x); };

comp.openInViewer();
for (var k=1;k<=comp.numLayers;k++) comp.layer(k).selected=false;
comp.layer(1).selected=true;
var res=applyClick("/C:/Users/0/.buzz/REPOS/listeningkit-templates/textAnimations/plugins/CRTemulator","10");
proto.property=ecProperty; proto.addProperty=ecAddProperty;
writeLn("applyClick -> "+res);

var pt=layerNamed(comp,"Posterize Time"); if(pt) pt.enabled=false;
// the cyberpsycho lines stay under the CRT (where cyberpunkEyes.jsx puts them), so they take its scan lines and grade
var top=["exposure cuts","thermal orange","thermal green"];
for (var i=0;i<top.length;i++){ var l=layerNamed(comp,top[i]); if(l) l.moveToBeginning(); }
// the outro stays under the CRT like everything else (where cyberpunkEyes.jsx puts it), so the CRT runs through its cuts
for (var k=1;k<=comp.numLayers;k++){ var l=comp.layer(k); writeLn("  "+k+" ["+l.name+"] "+l.inPoint.toFixed(2)+"→"+l.outPoint.toFixed(2)+(l.enabled?"":" (off)")); }
