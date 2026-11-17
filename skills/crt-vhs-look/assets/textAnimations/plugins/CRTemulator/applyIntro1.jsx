// Intro 1: the CRT-Emulator plug-in's own build (style 10) in place of the hand-made CRT.
// crtEmulator.jsx is the plug-in's ExtendScript, unchanged; its CEP panel (HTML) doesn't run in EffectCraft,
// so this calls the same applyClick() the panel's Apply button calls.
#include "jsx/crtEmulator.jsx"

function findCompByName(n){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof CompItem && it.name===n) return it;} return null; }
function layerNamed(c,n){ for (var k=1;k<=c.numLayers;k++) if(c.layer(k).name===n) return c.layer(k); return null; }
var intro=findCompByName("Intro 1");

// clear the hand-made CRT and the duplicates an earlier double run left
var drop={"crt screen":1,"crt screen 2":1,"crt rolling bar":1,"crt rolling bar 2":1,"crt phosphor mask":1,"exposure cuts 2":1,"black backing 2":1};
for (var k=intro.numLayers;k>=1;k--) if(drop[intro.layer(k).name]) intro.layer(k).remove();

// the double run swapped the cards back: Discord and Facebook belong in the second and fifth slots
var J=findCompByName("logPlayJourney");
function swapTransform(a,b){
  var names=["Position","Orientation","X Rotation","Y Rotation","Z Rotation"];
  for (var i=0;i<names.length;i++){
    var pa=a.property("Transform").property(names[i]), pb=b.property("Transform").property(names[i]);
    if(!pa||!pb) continue; var va=pa.value; pa.setValue(pb.value); pb.setValue(va);
  }
}
if(layerNamed(J,"Discord play").property("Transform").property("Position").value[0]!==2720) swapTransform(layerNamed(J,"Slack play"),layerNamed(J,"Discord play"));
if(layerNamed(J,"Facebook play").property("Transform").property("Position").value[0]!==7930) swapTransform(layerNamed(J,"Reddit play"),layerNamed(J,"Facebook play"));

// The plug-in addresses effect parameters by After Effects' index. EffectCraft orders a few effects
// differently, so map the AE index to the parameter's name for those.
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
var proto=Object.getPrototypeOf(intro.layer(1).property("ADBE Effect Parade"));
var ecProperty=proto.property, ecAddProperty=proto.addProperty;
proto.property=function(x){
  var table=AE[this.matchName];
  if(table && typeof x==="number" && x>=1 && x<=table.length){ if(table[x-1]===null) return noop; x=table[x-1]; }
  if(typeof x==="string" && AE_IDS[x]){ var p=this; for (var i=0;i<AE_IDS[x].length;i++){ p=ecProperty.call(p,AE_IDS[x][i]); if(!p) return noop; } return p; }
  var r=ecProperty.call(this,x);
  return (r===null||r===undefined)&&typeof x==="string"&&/^VISINF Grain Implant-\d+$/.test(x)?noop:r;
};
proto.addProperty=function(x){ return ecAddProperty.call(this,AE_EFFECTS[x]||x); };

intro.openInViewer();
for (var k=1;k<=intro.numLayers;k++) intro.layer(k).selected=false;
intro.layer(1).selected=true;
var res=applyClick("/C:/Users/0/.buzz/REPOS/listeningkit-templates/textAnimations/plugins/CRTemulator","10");
proto.property=ecProperty; proto.addProperty=ecAddProperty;

writeLn("applyClick -> "+res);

// the platform cards (24.97 on) are UI to be read: Posterize Time holds frames from mid camera move there,
// and the full grid buries the text
var UI={"Posterize Time":0,"CRT_LINE":45,"CRT_LINE 2":45};
for (var n in UI){ var l=layerNamed(intro,n); if(l) l.property("Transform").property("Opacity").expression="time>=24.97?"+UI[n]+":value"; }
for (var k=1;k<=intro.numLayers;k++){ var l=intro.layer(k); writeLn("  "+k+" ["+l.name+"] "+l.inPoint.toFixed(2)+"→"+l.outPoint.toFixed(2)+(l.enabled?"":" (off)")); }

