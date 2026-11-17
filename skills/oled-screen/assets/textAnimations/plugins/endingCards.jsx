// The ending's typography, Cyberpunk-style (matt, 2026-11-15): no HUDs, just the type, flat background colour
// changes and lines. Works on the comp "ending" as endingType.jsx / launchCaptions.jsx left it (the caption layers
// "cap NNN.L" on black, under the CRT):
//   - "cards bg": the background cuts to a new flat colour on every caption card (black, acid yellow, navy, red, in
//     turn), hold keyframes on a Fill, so each colour can be changed by hand
//   - each caption's ink set against its card's background (Fill on the text layer)
//   - on every other card a heartbeat line, plotted for that card (a shape layer: a flat line across the frame
//     with an ECG beat, P bump / Q dip / R spike / S dip / T bump, whose spike rises through the card's big word,
//     sized to the word), drawn on left to right (Trim Paths End, ease out), a short bright pulse head running along
//     it, then erased from the left (Trim Start) before the card ends; glowing, in the ink colour. Like the
//     Edgerunners 2 trailer's opening line, but ours and editable: move the vertices, the beat, the timing
//   - on the cards between, the tear from Edgerunners 2 Teaser #2 (1:24, frames 23-29) opens the card: a thick red
//     line across black through the big word rips open, jagged (Turbulent Displace) and tilted, growing to the full
//     frame over 6 frames; inside it the card shows in red duotone (Tint), outside it black; a glitch frame; then
//     the card itself. Layers "card tear N" (the line, the matte), "card tear dark N", "card tear red N"
// All layers sit under the captions and the CRT, over "black". Rerun replaces them.
//   File > Scripts > Run Script File... > plugins/endingCards.jsx
var F=30, W=1920, H=1080;
var BG=[[0,0,0],[254/255,206/255,0],[16/255,24/255,60/255],[200/255,18/255,30/255]];
var INK=[[1,1,1],[16/255,24/255,60/255],[254/255,206/255,0],[1,1,1]];

function findComp(n){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof CompItem && it.name===n) return it;} return null; }
function findFile(p){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof FootageItem && it.file && it.file.fsName.replace(/\\/g,"/").toLowerCase()===p.toLowerCase()) return it;} return null; }
function fx(L, id){ return L.property("Effects").addProperty(id); }
function P(e, n){ return e.property(e.property(1).matchName.replace(/-\d+$/,"")+"-"+("000"+n).slice(-4)); }
function rgba(c){ return [c[0],c[1],c[2],1]; }

var C=findComp("ending"); if(!C) throw new Error("no comp 'ending'");
for (var k=C.numLayers;k>=1;k--){ var nm=C.layer(k).name; if(/^(cards bg|card line|card heartbeat|card tear|card cracks|card slashes|card ui)/.test(nm)) C.layer(k).remove(); }
for (var k=1;k<=C.numLayers;k++){ var L=C.layer(k); if(/^cap /.test(L.name)){ var e=L.property("Effects"); for (var j=e.numProperties;j>=1;j--) if(e.property(j).name==="card ink") e.property(j).remove(); } }
var black=null, card=null; for (var k=1;k<=C.numLayers;k++){ if(C.layer(k).name==="black") black=C.layer(k); if(C.layer(k).name==="ending card") card=C.layer(k); }

// the cards: group caption layers by their in-point; the biggest line is the card's key word
var cards={}, order=[];
for (var k=1;k<=C.numLayers;k++){ var L=C.layer(k); if(!/^cap /.test(L.name)) continue;
  var f=Math.round(L.inPoint*F), d=L.property("Source Text").value;
  if(!cards[f]){ cards[f]={start:f, end:Math.round(L.outPoint*F), layers:[], key:null, keySize:0}; order.push(f); }
  cards[f].layers.push(L); if(d.fontSize>cards[f].keySize){ cards[f].keySize=d.fontSize; cards[f].key=L; } }
order.sort(function(a,b){return a-b;});

// the background colours, cutting on each card
var bg=C.layers.addSolid([0,0,0],"cards bg",W,H,1); bg.startTime=0; bg.inPoint=0; bg.outPoint=C.duration;
if(card) bg.moveAfter(card); else if(black) bg.moveBefore(black);
var bf=fx(bg,"ADBE Fill"), bcol=P(bf,2);
for (var i=0;i<order.length;i++){ bcol.setValueAtTime(order[i]/F, rgba(BG[i%BG.length])); }
try{ for (var k=1;k<=bcol.numKeys;k++) bcol.setInterpolationTypeAtKey(k, KeyframeInterpolationType.HOLD); }catch(e){}

// the heartbeat: the path through the card's big word (word centre cx, cy, height wh), in comp pixels
function beat(cx, cy, wl, wr, wh, flip){
  // the beat sits in the bigger empty space beside the word (left of wl or right of wr), its spike taller than the
  // word; the flat line runs right through the word
  var d=flip?-1:1, u=Math.max(28, wh/3.2);
  var bx=(wl > W-wr) ? wl/2 : (wr+W)/2;
  bx=Math.max(7*u, Math.min(W-6*u, bx));
  return [[-40,cy],[bx-7*u,cy],[bx-5.8*u,cy-0.8*u*d],[bx-4.6*u,cy],[bx-2*u,cy],[bx-1.4*u,cy+1.1*u*d],
          [bx-0.5*u,cy-5.5*u*d],[bx+0.5*u,cy+3*u*d],[bx+1.3*u,cy],[bx+3*u,cy-1.3*u*d],[bx+4.6*u,cy],[W+40,cy]];
}
function strokeGroup(L, name, verts, col, width){
  var g=L.property("Contents").addProperty("ADBE Vector Group"); g.name=name; var gc=g.property("Contents");
  var sh=new Shape(); sh.vertices=verts; sh.closed=false; gc.addProperty("ADBE Vector Shape - Group").property("ADBE Vector Shape").setValue(sh);
  var st=gc.addProperty("ADBE Vector Graphic - Stroke"); st.property("ADBE Vector Stroke Color").setValue(col); st.property("ADBE Vector Stroke Width").setValue(width);
  try{ st.property("ADBE Vector Stroke Line Join").setValue(1); }catch(e){}
  return gc.addProperty("ADBE Vector Filter - Trim");
}
var DRAW=12, ERASE_AT=18;                                // frames: drawn on in DRAW, erased from ERASE_AT to the card's end
// the UI elements from the Cyberpunk menu (assets/ui3d, make_ui3d_elements.py), flat, cutting in and out with each
// card: two or three per card, in the card's ink (so they read against its colour), in the space the word leaves
var UI="C:/Users/0/.buzz/REPOS/listeningkit-templates/textAnimations/assets/ui3d/";
var UIE=[["dots_grid.png",45],["plus_grid.png",50],["dashed_bar.png",60],["chevron_bars.png",55],["graph_box.png",55],["red_stack.png",90]];
function uiAt(i, cd, ink){
  var kp=cd.key.property("Transform").property("Position").value, wl=kp[0], wt=kp[1]-cd.keySize, ww=cd.keySize*3, wh=cd.keySize;
  try{ var r=cd.key.sourceRectAtTime((cd.start+3)/F,false); if(r.width>10){ wl=kp[0]+r.left; wt=kp[1]+r.top; ww=r.width; wh=r.height; } }catch(e){}
  var top=wt>H/2, left=(wl+ww/2)>W/2;                    // put them on the far side from the word
  var spots=[[left?380:1540, top?230:850],[left?260:1660, top?560:520],[W/2+(left?-420:420), top?120:960]];
  var n=2+(i%2);
  for (var q=0;q<n;q++){ var e=UIE[(i*2+q)%UIE.length];
    var f=findFile(UI+e[0])||app.project.importFile(new ImportOptions(new File(UI+e[0])));
    var L=C.layers.add(f); L.name="card ui "+(i+1)+" "+e[0].replace(".png","");
    L.startTime=cd.start/F; L.inPoint=cd.start/F; L.outPoint=cd.end/F;
    L.property("Transform").property("Position").setValue(spots[q]);
    L.property("Transform").property("Scale").setValue([e[1],e[1]]);
    var fl=fx(L,"ADBE Fill"); P(fl,2).setValue(rgba(ink));
    // cutting in: on, off, on over the first frames (staggered), a flicker off near the end
    L.property("Opacity").expression="var f=Math.round((time-inPoint)*30), n=Math.round((outPoint-inPoint)*30); (f<"+q+"||f=="+(q+1)+"||f==n-3)?0:85";
    L.moveBefore(bg);
  }
}

// the ink, the lines
for (var i=0;i<order.length;i++){ var cd=cards[order[i]], ink=INK[i%INK.length];
  uiAt(i, cd, ink);
  for (var j=0;j<cd.layers.length;j++){ var fl=fx(cd.layers[j],"ADBE Fill"); fl.name="card ink"; P(fl,2).setValue(rgba(ink)); }
  var kp=cd.key.property("Transform").property("Position").value, ky=kp[1]-cd.keySize*0.33;
  // the Edgerunners 2 trailer's red lines (plugins/redlines, drawn per frame by assets/make_ending_redlines.py):
  // cracks down through the word on even cards, under the type; slashes looping round the word on odd cards, over it
  var RL="C:/Users/0/.buzz/REPOS/listeningkit-templates/textAnimations/assets/collage/redlines/card_"+("0"+(i+1)).slice(-2)+"/r_001.png";
  if(new File(RL).exists){
    var rs=findFile(RL); if(rs){ try{ rs.replaceWithSequence(new File(RL),false); }catch(e){ rs.replace(new File(RL)); } } else { var o=new ImportOptions(new File(RL)); try{o.sequence=true;}catch(e){} rs=app.project.importFile(o); }
    try{ rs.mainSource.conformFrameRate=F; }catch(e){}
    var rl=C.layers.add(rs); rl.name=(i%2===0?"card cracks ":"card slashes ")+(i+1);
    rl.startTime=cd.start/F; rl.inPoint=cd.start/F; rl.outPoint=cd.end/F;
    if(i%2===0) rl.moveBefore(bg); else rl.moveBefore(cd.key);
  }
}
// the CRT's colour layers grade everything blue-grey and kill the yellow and red, so they're off in the ending
// (the scanlines, the mask and the distortion stay); switch them back on by hand to compare
var GRADE=/^(CC|CC 2|CRT ExposureFIX|CRT Glow|Glow)$/;
for (var k=1;k<=C.numLayers;k++) if(GRADE.test(C.layer(k).name)) C.layer(k).enabled=false;
writeLn("ending: "+order.length+" cards, colour fields, heartbeat lines and line wipes");
