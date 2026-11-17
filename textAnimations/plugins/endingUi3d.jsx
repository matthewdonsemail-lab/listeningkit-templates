// The ending as a real 3D scene (matt, 2026-11-16): every element its own 3D layer at its own depth in ONE comp, a
// camera with depth of field moving round them, as the Cyberpunk 2077 main-menu UI recreation
// (projects/opening/ref/zdepth_ref, youtube QiCYtUZkZVw): a dark navy grid panel, yellow dot and plus grids, dashed
// bars in red frames, magenta bars, the chevron bars, a graph box, a red stack, all at different z, glowing.
//   "ending 3d"  the scene: the UI elements (assets/ui3d/*.png, assets/make_ui3d_elements.py) as 3D layers at
//                z -300..+900; the ending's caption layers copied in as 3D layers floating in front of the panel
//                (yellow / white / magenta); the red cracks and slashes copied in beside them; a camera with depth of
//                field that cuts to a new angle round each card's word and drifts while it's up; bloom; the end card
//                and the ending's CRT layers copied on top as 2D layers, so the CRT sits over the whole 3D scene.
// The launch film's "ending" layer is switched to "ending 3d" ("ending" itself stays as it was). Rerun replaces it.
// Run after endingCards.jsx.   File > Scripts > Run Script File... > plugins/endingUi3d.jsx
var DIR="C:/Users/0/.buzz/REPOS/listeningkit-templates/textAnimations/assets/ui3d/";
var F=30, W=1920, H=1080, ZOOM=2666.67, CARD_AT=626, WORD_Z=-120;
var YEL=[222/255,238/255,14/255], MAG=[225/255,0,226/255], RED=[188/255,20/255,54/255], NAVY=[7/255,14/255,26/255];
var LOOK=/^(thermal |exposure cuts|Global Scale|Lens Distortions|Monitor|CRT|Channel Blur|CC|CC 2|Posterize Time|Position Flicker|Glitches|Distortions|Glow)/;
function findComp(n){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof CompItem && it.name===n) return it;} return null; }
function findFile(p){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof FootageItem && it.file && it.file.fsName.replace(/\\/g,"/").toLowerCase()===p.toLowerCase()) return it;} return null; }
function imp(p){ return findFile(p)||app.project.importFile(new ImportOptions(new File(p))); }
function fx(L, id){ return L.property("Effects").addProperty(id); }
function P(e, n){ return e.property(e.property(1).matchName.replace(/-\d+$/,"")+"-"+("000"+n).slice(-4)); }
function rgba(c){ return [c[0],c[1],c[2],1]; }

var C=findComp("ending"); if(!C) throw new Error("no comp 'ending'");
var old; while((old=findComp("ending 3d"))) old.remove();
var S=app.project.items.addComp("ending 3d",W,H,1,C.duration,F);
S.layers.addSolid(NAVY,"navy",W,H,1);

// ---- the UI elements, each its own 3D layer at its own depth
function el(name, file, x, y, z, sc, rotZ, flicker){
  var L=S.layers.add(imp(DIR+file)); L.name=name; L.threeDLayer=true;
  var t=L.property("Transform"); t.property("Position").setValue([x,y,z]); t.property("Scale").setValue([sc,sc,sc]);
  if(rotZ) t.property("Z Rotation").setValue(rotZ);
  if(flicker) L.property("Opacity").expression="var f=Math.floor(time*30); 70+30*Math.abs(Math.sin(f*1.7+"+x+"))";
  return L;
}
function bar(name, col, w, h, x, y, z){
  var L=S.layers.addSolid(col,name,w,h,1); L.threeDLayer=true; L.property("Transform").property("Position").setValue([x,y,z]); return L;
}
// far back
el("dots far", "dots_grid.png", 300, 1100, 900, 160);
el("plus far", "plus_grid.png", 1700, -100, 750, 150);
el("dots back left", "dots_grid.png", 250, 150, 420, 110, 0, true);
el("plus back right", "plus_grid.png", 1500, 120, 360, 100, 0, true);
el("dots back right", "dots_grid.png", 1650, 860, 300, 90);
// the panel the words sit over
el("grid panel", "grid_panel.png", 960, 560, 0, 125);
// the bars and frames round it, nearer
el("dashed bar top", "dashed_bar.png", 960, 250, -40, 100, 0, true);
el("dashed bar bottom", "dashed_bar.png", 1000, 880, -70, 100, 0, true);
bar("magenta bar top", MAG, 900, 22, 760, 300, -30);
bar("magenta bar bottom", MAG, 600, 20, 1360, 830, -90);
bar("red bar", RED, 700, 14, 600, 820, -60);
el("chevron bars", "chevron_bars.png", 820, 470, -20, 85);
el("graph box", "graph_box.png", 1700, 640, -160, 100);
el("red stack", "red_stack.png", 140, 430, -200, 110);
el("plus front left", "plus_grid.png", -150, 520, -260, 60);
el("dots front", "dots_grid.png", 1500, 1150, -320, 70);
// cyan rules
bar("cyan rule 1", [19/255,151/255,219/255], 700, 3, 500, 236, -10);
bar("cyan rule 2", [19/255,151/255,219/255], 900, 3, 1400, 900, -45);

// ---- the words and the red lines, copied in as 3D layers in front of the panel
var INKS=[YEL,[1,1,1],MAG,YEL];
var cards={}, order=[], copied=[];
for (var k=C.numLayers;k>=1;k--){ var L=C.layer(k);
  if(/^(card cracks|card slashes) /.test(L.name) || /^cap /.test(L.name)){ L.copyToComp(S); copied.push(S.layer(1)); }
}
for (var c=0;c<copied.length;c++){ var L=copied[c]; L.threeDLayer=true;
  var p=L.property("Transform").property("Position").value; L.property("Transform").property("Position").setValue([p[0],p[1],/^cap /.test(L.name)?WORD_Z:WORD_Z+12]);
  if(/^cap /.test(L.name)){
    var f=Math.round(L.inPoint*F), d=L.property("Source Text").value;
    if(!cards[f]){ cards[f]={start:f, end:Math.round(L.outPoint*F), key:null, ks:0, layers:[]}; order.push(f); }
    cards[f].layers.push(L); if(d.fontSize>cards[f].ks){ cards[f].ks=d.fontSize; cards[f].key=L; }
  }
}
order.sort(function(a,b){return a-b;});
for (var i=0;i<order.length;i++){ var cd=cards[order[i]];
  for (var j=0;j<cd.layers.length;j++){ var e=cd.layers[j].property("Effects");
    for (var q=e.numProperties;q>=1;q--) if(e.property(q).name==="card ink") e.property(q).remove();
    var fl=fx(cd.layers[j],"ADBE Fill"); fl.name="card ink"; P(fl,2).setValue(rgba(INKS[i%INKS.length])); }
}

// ---- the camera: depth of field, a new angle round each card's word, drifting
var cam=S.layers.addCamera("camera",[W/2,H/2]); var co=cam.property("Camera Options"), ct=cam.property("Transform");
co.property("ADBE Camera Depth of Field").setValue(1); co.property("ADBE Camera Blur Level").setValue(100);
co.property("ADBE Camera Focus Distance").expression="length(transform.position, transform.pointOfInterest)";
co.property("highlightGain").setValue(30); co.property("highlightThreshold").setValue(200);
var poi=ct.property("Point of Interest"), pos=ct.property("Position"), ap=co.property("ADBE Camera Aperture");
var ANG=[[28,-16],[-34,14],[18,24],[-24,-20],[36,8],[-16,-26]];
function camAt(f, c, dist, yaw, pitch){
  var y=yaw*Math.PI/180, p=pitch*Math.PI/180;
  poi.setValueAtTime(f/F, c);
  pos.setValueAtTime(f/F, [c[0]+Math.sin(y)*Math.cos(p)*dist, c[1]-Math.sin(p)*dist, c[2]-Math.cos(y)*Math.cos(p)*dist]);
}
for (var i=0;i<order.length;i++){ var cd=cards[order[i]], L=cd.key;
  var pv=L.property("Transform").property("Position").value, cx=pv[0], cy=pv[1], ww=cd.ks*3;
  try{ var r=L.sourceRectAtTime((cd.start+3)/F,false); if(r.width>10){ cx=pv[0]+r.left+r.width/2; cy=pv[1]+r.top+r.height/2; ww=r.width; } }catch(e){}
  var a=ANG[i%ANG.length], dist=Math.max(ZOOM*0.75, Math.min(ZOOM*1.15, ZOOM*ww*2.0/W));
  camAt(cd.start, [cx,cy,WORD_Z], dist*1.08, a[0], a[1]);
  camAt(Math.max(cd.start+1,cd.end-1), [cx+20,cy,WORD_Z], dist*0.95, a[0]*0.7, a[1]*0.7);
  ap.setValueAtTime(cd.start/F, 35);
}
camAt(CARD_AT, [W/2,H/2,0], ZOOM, 0, 0); ap.setValueAtTime(CARD_AT/F, 0);
try{ for (var k=1;k<=pos.numKeys;k++){ var o=(k%2===0)?KeyframeInterpolationType.HOLD:KeyframeInterpolationType.LINEAR;
  pos.setInterpolationTypeAtKey(k, KeyframeInterpolationType.LINEAR, o); poi.setInterpolationTypeAtKey(k, KeyframeInterpolationType.LINEAR, o); } }catch(e){}
try{ for (var k=1;k<=ap.numKeys;k++) ap.setInterpolationTypeAtKey(k, KeyframeInterpolationType.HOLD, KeyframeInterpolationType.HOLD); }catch(e){}

// ---- bloom
var bl=S.layers.addSolid([0,0,0],"bloom",W,H,1); bl.adjustmentLayer=true;
var g1=fx(bl,"ADBE Glo2"); P(g1,2).setValue(70); P(g1,3).setValue(14); P(g1,4).setValue(0.7);
var g2=fx(bl,"ADBE Glo2"); P(g2,2).setValue(80); P(g2,3).setValue(60); P(g2,4).setValue(0.3);

// ---- the end card and the CRT on top, 2D, over the whole 3D scene
for (var k=C.numLayers;k>=1;k--){ var L=C.layer(k); if(L.name==="ending card" || LOOK.test(L.name)) L.copyToComp(S); }

var LF=findComp("launch film");
if(LF) for (var k=1;k<=LF.numLayers;k++) if(LF.layer(k).name==="ending") LF.layer(k).replaceSource(S,false);
writeLn("ending 3d: "+order.length+" cards, "+S.numLayers+" layers");
