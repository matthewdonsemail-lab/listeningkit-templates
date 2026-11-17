// The launch opener (comp "opening", matt's FilmCraft cut, assets/sync_opening_from_filmcraft.py), matt 2026-11-15:
//  - before the drop (0 to 00:00:10:08): a washed-out VHS look, after the tragedy_rx edit
//    (projects/opening/ref/tragedy_rx): lifted milky blacks, dull whites, less colour, a warm cast, a soft image
//    sharpened back hard so every edge rings, red and blue bleeding sideways, a little line wobble, grain; and black
//    bars down the sides, a 4:3 picture in the 16:9 frame;
//  - from the drop (10:08) to the end: the CRT-Emulator plug-in's own build (style 10), as applyCyberpunk.jsx does it,
//    with every layer it adds trimmed to start on the drop.
// Run after plugins/openingDawn.jsx, which rebuilds "opening" from scratch and clears all of this.
//   effectcraft-cli --project textAnimations.ecproj script plugins/CRTemulator/applyOpening.jsx --save
#include "jsx/crtEmulator.jsx"

var F=30, DROP=308, END=450, BAR=240;  // frames; BAR: each side bar's width (a 1440x1080 4:3 picture)
function findCompByName(n){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof CompItem && it.name===n) return it;} return null; }
function layerNamed(c,n){ for (var k=1;k<=c.numLayers;k++) if(c.layer(k).name===n) return c.layer(k); return null; }
var comp=findCompByName("opening"); if(!comp) throw new Error("no comp opening");
END=Math.round(comp.duration*F);
// an earlier run's layers go first
var MINE=["VHS look","bar left","bar right"];
for (var k=comp.numLayers;k>=1;k--){ var l=comp.layer(k); for (var j=0;j<MINE.length;j++) if(l.name===MINE[j]){ l.remove(); break; } }
var shots={}; for (var k=1;k<=comp.numLayers;k++){ var n=comp.layer(k).name; if(n.indexOf("opening ")===0) shots[n]=1; }
for (var k=comp.numLayers;k>=1;k--){ var l=comp.layer(k); if(!shots[l.name]) l.remove(); }  // and its CRT

// --- the CRT from the drop
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
var crt=0;
for (var k=1;k<=comp.numLayers;k++){ var l=comp.layer(k); if(shots[l.name]) continue;
  l.startTime=0; l.inPoint=DROP/F; l.outPoint=END/F; crt++; }

// --- the VHS look before the drop
function adj(name,a,b){ var L=comp.layers.addSolid([0,0,0],name,1920,1080,1); L.adjustmentLayer=true; L.startTime=0; L.inPoint=a/F; L.outPoint=b/F; return L; }
function fx(L,m){ return L.property("Effects").addProperty(m); }
function set(e,n,v){ var p=e.property(n); if(p) p.setValue(v); else writeLn("  (no "+n+" on "+e.name+")"); }
var V=adj("VHS look",0,DROP);
var e=fx(V,"ADBE Gaussian Blur 2"); set(e,"Blurriness",3); set(e,"Blur Dimensions",2);          // soft, sideways (tape)
e=fx(V,"ADBE Unsharp Mask2"); set(e,"Amount",180); set(e,"Radius",4); set(e,"Threshold",0);   // sharpened back hard: halos
e=fx(V,"ADBE Channel Blur"); set(e,"Red Blurriness",9); set(e,"Blue Blurriness",12); set(e,"Blur Dimensions",2);  // colour bleed
e=fx(V,"ADBE Wave Warp"); set(e,"Wave Type",1); set(e,"Wave Height",2); set(e,"Wave Width",14); set(e,"Direction",180); set(e,"Wave Speed",3);
e=fx(V,"ADBE Easy Levels2"); set(e,"Output Black",0.11); set(e,"Output White",0.88); set(e,"Gamma",1.08);  // washed out
e=fx(V,"ADBE HUE SATURATION"); set(e,"Master Saturation",-22);
e=fx(V,"ADBE Tint"); set(e,"Map Black To",[0.16,0.08,0.06,1]); set(e,"Map White To",[1,0.93,0.82,1]); set(e,"Amount to Tint",18);
e=fx(V,"VISINF Grain Implant"); try{ e.property("Tweaking").property("Intensity").setValue(1.4); }catch(x){ writeLn("  (grain intensity not set)"); }

// --- the side bars before the drop, on top of everything
function bar(name,x){ var L=comp.layers.addSolid([0,0,0],name,BAR,1080,1); L.startTime=0; L.inPoint=0; L.outPoint=DROP/F;
  L.property("Transform").property("Position").setValue([x,540]); return L; }
bar("bar left",BAR/2); bar("bar right",1920-BAR/2);
writeLn("opening: VHS look + side bars 0-"+DROP+", CRT ("+crt+" layers) "+DROP+"-"+END);
for (var k=1;k<=comp.numLayers;k++){ var l=comp.layer(k); writeLn("  "+k+" ["+l.name+"] "+Math.round(l.inPoint*F)+"-"+Math.round(l.outPoint*F)+(l.enabled?"":" (off)")); }
