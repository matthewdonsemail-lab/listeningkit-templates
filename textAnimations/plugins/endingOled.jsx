// The ending filmed off a giant LED sign (matt, 2026-11-15), shot like the 3D sign shots in the Edgerunners trailer
// (projects/opening/ref/t1_arrows_sheet.jpg, frames 572-722: huge emissive panels and rows of glowing bars filling the
// frame, the camera low and steep, skimming fast across them, deep perspective, near sharp / far soft, heavy bloom).
// The cards are the sign; rows of LED bars in the card's ink run across the sign round each word.
//   "oled panel"     the comp "ending" mosaicked to the panel's pixel grid (Mosaic, 1920/8 x 1080/8) and multiplied by
//                    the subpixel mask (assets/oled_subpixels.png, make_oled_mask.py: every pixel three R/G/B bars),
//                    brightened and glowing like a lit panel
//   "ending screen"  the panel as a 3D layer in a dark room, a camera with depth of field on (shallow aperture, the
//                    focus always on the word it's looking at, bokeh from the lit subpixels: Highlight Gain); on every
//                    caption card the camera cuts to a new angle on that card's big word (hold keyframes), drifting a
//                    little during the card; the end card front-on and sharp
// and swaps the launch film's "ending" layer over to "ending screen". Rerun replaces it.
// Run after endingCards.jsx.   File > Scripts > Run Script File... > plugins/endingOled.jsx
var MASK="C:/Users/0/.buzz/REPOS/listeningkit-templates/textAnimations/assets/oled_subpixels.png";
var F=30, W=1920, H=1080, PITCH=8, ZOOM=2666.67, CARD_AT=626;
function findComp(n){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof CompItem && it.name===n) return it;} return null; }
function findFile(p){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof FootageItem && it.file && it.file.fsName.replace(/\\/g,"/").toLowerCase()===p.toLowerCase()) return it;} return null; }
function fx(L, id){ return L.property("Effects").addProperty(id); }
function P(e, n){ return e.property(e.property(1).matchName.replace(/-\d+$/,"")+"-"+("000"+n).slice(-4)); }
function hold(prop){ try{ for (var k=1;k<=prop.numKeys;k++) prop.setInterpolationTypeAtKey(k, KeyframeInterpolationType.LINEAR, KeyframeInterpolationType.HOLD); }catch(e){} }

var C=findComp("ending"); if(!C) throw new Error("no comp 'ending'");
var LF=findComp("launch film");
if(LF) for (var k=1;k<=LF.numLayers;k++) if(LF.layer(k).name==="ending" && LF.layer(k).source!==C) LF.layer(k).replaceSource(C,false);
var old; while((old=findComp("ending screen"))) old.remove(); while((old=findComp("oled panel"))) old.remove();

// ---- the panel
// the panel is bigger than the frame (a margin round the ending, filled with the ending itself scaled up under it),
// so the camera can sit back and angle without ever seeing the panel's edge
var MW=W*3, MH=H*3, MX=(MW-W)/2, MY=(MH-H)/2;     // a huge sign: the camera grazes it at steep angles
var PN=app.project.items.addComp("oled panel",MW,MH,1,C.duration,F);
var under=PN.layers.add(C); under.name="ending (margin)"; under.property("Transform").property("Scale").setValue([302,302]);
var pc=PN.layers.add(C); pc.name="ending";
// rows of LED bars across the sign round each card's word, in the card's ink, on during that card
var INK=[[1,1,1],[16/255,24/255,60/255],[254/255,206/255,0],[1,1,1]];
var cardsB={}, orderB=[];
for (var k=1;k<=C.numLayers;k++){ var L=C.layer(k); if(!/^cap /.test(L.name)) continue;
  var f=Math.round(L.inPoint*F), d=L.property("Source Text").value;
  if(!cardsB[f]){ cardsB[f]={start:f, end:Math.round(L.outPoint*F), key:null, ks:0}; orderB.push(f); }
  if(d.fontSize>cardsB[f].ks){ cardsB[f].ks=d.fontSize; cardsB[f].key=L; } }
orderB.sort(function(a,b){return a-b;});
for (var i=0;i<orderB.length;i++){ var cd=cardsB[orderB[i]], ink=INK[i%4], pv=cd.key.property("Transform").property("Position").value;
  var cy=pv[1]-cd.ks*0.35+MY, gap=cd.ks*0.18, n=14, bw=cd.ks*0.55, bh=cd.ks*0.08, slant=(i%2)?1:-1;
  for (var r=-1;r<=1;r+=2){                                   // a row above and a row below the word
    for (var b=0;b<n;b++){
      var bar=PN.layers.addSolid(ink,"led bar "+(i+1),Math.round(bw),Math.max(4,Math.round(bh)),1);
      bar.startTime=cd.start/F; bar.inPoint=cd.start/F; bar.outPoint=cd.end/F;
      bar.property("Transform").property("Position").setValue([MX-cd.ks*2+b*(bw+gap), cy+r*cd.ks*0.85]);
      bar.property("Transform").property("Rotation").setValue(slant*-12);
      bar.property("Opacity").expression="var f=Math.round((time-inPoint)*30); (f>="+b+"*0.6)?100:0";   // the row lights up along
      bar.moveAfter(pc);
    }
  }
}
var mo=fx(pc,"ADBE Mosaic"); P(mo,1).setValue(W/PITCH); P(mo,2).setValue(H/PITCH); try{ P(mo,3).setValue(1); }catch(e){}
var mk=PN.layers.add(findFile(MASK)||app.project.importFile(new ImportOptions(new File(MASK)))); mk.name="subpixels";
mk.blendingMode=BlendingMode.MULTIPLY; mk.property("Transform").property("Scale").setValue([300,300]);
var lit=PN.layers.addSolid([0,0,0],"panel light",MW,MH,1); lit.adjustmentLayer=true;
fx(lit,"ec.color.exposure").property("master").property("exposure").setValue(1.6);
var gw=fx(lit,"ADBE Glo2"); P(gw,2).setValue(55); P(gw,3).setValue(18); P(gw,4).setValue(0.8);

// ---- the room and the camera
var SC=app.project.items.addComp("ending screen",W,H,1,C.duration,F);
SC.layers.addSolid([0.01,0.01,0.015],"room",W,H,1);
var sp=SC.layers.add(PN); sp.name="the screen"; sp.threeDLayer=true; sp.property("Transform").property("Position").setValue([W/2,H/2,0]);
// its thickness: copies stacked behind it, darker and redder the deeper they go (as the teaser's logo slab)
for (var d=1;d<=4;d++){
  var dp=SC.layers.add(PN); dp.name="the screen, depth "+d; dp.threeDLayer=true;
  dp.property("Transform").property("Position").setValue([W/2,H/2,d*14]);
  var ex=fx(dp,"ec.color.exposure"); ex.property("master").property("exposure").setValue(-0.9*d);
  var tn=fx(dp,"ADBE Tint"); P(tn,1).setValue([0,0,0,1]); P(tn,2).setValue([1,0.15,0.45,1]); P(tn,3).setValue(55);
  dp.moveAfter(sp);
}
// rows of glowing bars out in the room at different depths, in front of and behind the sign (parallax as the camera
// slides), magenta / yellow / the card colours, like the teaser's stripe arrays and trailer 1's chevrons
var BARC=[[1,0.2,0.75],[1,0.8,0.1],[1,0.25,0.35],[0.3,1,0.75]];
for (var row=0;row<10;row++){
  var z=[160,260,380,520,680,860,1060,1300,1550,1800][row], y=H/2+((row*317)%900-450)*1.6, col=BARC[row%4];
  for (var b=0;b<12;b++){
    var bar=SC.layers.addSolid(col,"bar row "+(row+1),260,22,1); bar.threeDLayer=true;
    bar.property("Transform").property("Position").setValue([-1400+b*330+(row%2)*160, y, z]);
    bar.property("Transform").property("Z Rotation").setValue(-28+(row%3)*6);
    bar.property("Opacity").expression="var f=Math.round(time*30); 60+40*Math.sin(f*0.7+"+(b+row*3)+")";
  }
}
var cam=SC.layers.addCamera("camera",[W/2,H/2]); var co=cam.property("Camera Options"), ct=cam.property("Transform");
co.property("ADBE Camera Depth of Field").setValue(1);
co.property("ADBE Camera Blur Level").setValue(100);
co.property("highlightGain").setValue(45); co.property("highlightThreshold").setValue(170); co.property("highlightSaturation").setValue(70);
co.property("irisShape").setValue(6);
co.property("ADBE Camera Focus Distance").expression="length(transform.position, transform.pointOfInterest)";

// the cards and their big words (as endingCards.jsx finds them)
var cards={}, order=[];
for (var k=1;k<=C.numLayers;k++){ var L=C.layer(k); if(!/^cap /.test(L.name)) continue;
  var f=Math.round(L.inPoint*F), d=L.property("Source Text").value;
  if(!cards[f]){ cards[f]={start:f, end:Math.round(L.outPoint*F), key:null, keySize:0}; order.push(f); }
  if(d.fontSize>cards[f].keySize){ cards[f].keySize=d.fontSize; cards[f].key=L; } }
order.sort(function(a,b){return a-b;});
// steep grazing angles, as the teaser's logo shots: yaw / pitch per card
var ANG=[[46,-14],[-42,18],[38,24],[-48,-16],[44,10],[-36,-22]];
var poi=ct.property("Point of Interest"), pos=ct.property("Position"), ap=co.property("ADBE Camera Aperture");
function camAt(f, c, dist, yaw, pitch){
  var y=yaw*Math.PI/180, p=pitch*Math.PI/180;
  poi.setValueAtTime(f/F, [c[0],c[1],0]);
  pos.setValueAtTime(f/F, [c[0]+Math.sin(y)*Math.cos(p)*dist, c[1]-Math.sin(p)*dist, -Math.cos(y)*Math.cos(p)*dist]);
}
for (var i=0;i<order.length;i++){ var cd=cards[order[i]], L=cd.key;
  var pv=L.property("Transform").property("Position").value, cx=pv[0], cy=pv[1], ww=cd.keySize*3;
  try{ var r=L.sourceRectAtTime((cd.start+3)/F,false); if(!(r.width>10)) throw 0; cx=pv[0]+r.left+r.width/2; cy=pv[1]+r.top+r.height/2; ww=r.width; }catch(e){}
  var a=ANG[i%ANG.length];
  var dist=Math.max(ZOOM*0.4, Math.min(ZOOM*0.95, ZOOM*ww*1.25/W));   // the word fills most of the frame
  var dir=(a[0]>0)?1:-1, sw=ww*0.3;
  var len=cd.end-cd.start, mid=cd.start+Math.max(2, Math.round(len*0.3));
  camAt(cd.start, [cx-dir*sw*1.6, cy], dist*1.25, a[0]*1.15, a[1]*1.15);   // whipping in
  camAt(mid, [cx-dir*sw*0.3, cy], dist, a[0], a[1]);                         // and slowing
  camAt(Math.max(mid+1, cd.end-1), [cx+dir*sw*0.2, cy], dist*0.94, a[0]*0.92, a[1]*0.92);
  ap.setValueAtTime(cd.start/F, 70);
}
// the end card: front-on, the whole screen, sharp
poi.setValueAtTime(CARD_AT/F,[W/2,H/2,0]); pos.setValueAtTime(CARD_AT/F,[W/2,H/2,-ZOOM]); ap.setValueAtTime(CARD_AT/F, 0);
hold(poi); hold(pos); hold(ap);
// the drift between a card's two keys stays linear; only the jump to the next card is a cut
try{ for (var k=1;k<=pos.numKeys;k++){ if(k%3===0) continue; pos.setInterpolationTypeAtKey(k, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER); poi.setInterpolationTypeAtKey(k, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER); } }catch(e){}
// bloom over the whole scene, and on every cut a white flash frame plus a glitch frame
var bl=SC.layers.addSolid([0,0,0],"bloom",W,H,1); bl.adjustmentLayer=true;
var bg2=fx(bl,"ADBE Glo2"); P(bg2,2).setValue(70); P(bg2,3).setValue(60); P(bg2,4).setValue(0.55);
var cuts=[]; for (var i=0;i<order.length;i++) cuts.push(order[i]);
var cf=SC.layers.addSolid([0,0,0],"cut flash",W,H,1); cf.adjustmentLayer=true;
fx(cf,"ec.color.exposure").property("master").property("exposure").expression="var c=["+cuts.join(",")+"],f=Math.round(time*30),e=0;for(var i=0;i<c.length;i++){if(f==c[i])e=3;else if(f==c[i]+1)e=1.2;}e";
var cg=fx(cf,"ec.vr.digitalglitch"); P(cg,2).expression="var c=["+cuts.join(",")+"],f=Math.round(time*30),a=0;for(var i=0;i<c.length;i++){if(f>=c[i]&&f<=c[i]+2)a=100;}a";

if(LF) for (var k=1;k<=LF.numLayers;k++) if(LF.layer(k).name==="ending") LF.layer(k).replaceSource(SC,false);
writeLn("ending screen: "+order.length+" camera cuts, OLED panel, depth of field");
