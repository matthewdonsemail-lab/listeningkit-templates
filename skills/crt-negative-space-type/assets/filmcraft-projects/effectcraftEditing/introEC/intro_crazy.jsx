// The cold open, cut like the launch film's ending (matt, 2026-11-16: "we're not having the cyberpunk assets on the solid
// screens, and the in-between zoomed-in masked shots on black with the lines ... the same effect, using me"). On comp
// "intro", under the CRT, as plugins/endingCrazy.jsx and endingCards.jsx do it in the ending:
//   "insert N"   flash cuts to him (mattins/ins_NN, make_intro_inserts.py: zoomed in on his face, the cyberpsycho eye
//                glitch, the red slashes looping round him) for 3-4 frames inside each card, once or twice per card,
//                Digital Glitch hard on the first and last frame
//   "giant N"    on cards 3, 5, 8 and 10 a word blown up to fill the screen, used as an alpha matte for live footage of
//                him (the camera at that moment, zoomed on his face: him inside the letters, black round them), drifting
//                sideways, red cracks through it (mattins/giant_NN), 7 frames mid-card, glitching in and out
//   "card ui"    the ending's UI elements (assets/ui3d: dots grid, plus grid, dashed bar, chevrons, graph box, red stack)
//                on every word card, in the card's ink, on the far side from the word, cutting in
//   the thermogram ("thermal orange / green", "exposure cuts") stays on the card changes only
// Nothing within 4 frames of a word card, a transition or another hit. Rerun replaces them.
var D="C:/Users/0/filmcraft/projects/effectcraftEditing/introEC/";
var UI="C:/Users/0/.buzz/REPOS/listeningkit-templates/textAnimations/assets/ui3d/";
var UIE=[["dots_grid.png",45],["plus_grid.png",50],["dashed_bar.png",60],["chevron_bars.png",55],["graph_box.png",55],["red_stack.png",90]];
var CAM="C:/Users/0/AppData/Roaming/so.cap.desktop/recordings/Generic PnP Monitor (Display) 2026-11-16 03.27 PM.cap/content/segments/segment-0/camera.mp4";
var F=30, W=1920, H=1080;
var STARTS=[0,68,83,176,221,290,344,351,437,481,525];
var GIANT={2:"CLAUDE",4:"FUCKING",7:"WEEK.",9:"UPGRADE"};   // card index (0-based) -> the word
var LOOK=/^(thermal |exposure cuts|Global Scale|Lens Distortions|Monitor|CRT|Channel Blur|CC|CC 2|Posterize Time|Position Flicker|Glitches|Distortions|Glow)/;
function findComp(n){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof CompItem && it.name===n) return it;} return null; }
function findFile(p){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof FootageItem && it.file && it.file.fsName.replace(/\\/g,"/").toLowerCase()===p.toLowerCase()) return it;} return null; }
function byName(c,n){ for (var k=1;k<=c.numLayers;k++) if(c.layer(k).name===n) return c.layer(k); return null; }
function fx(L, id){ return L.property("Effects").addProperty(id); }
function P(e, n){ return e.property(e.property(1).matchName.replace(/-\d+$/,"")+"-"+("000"+n).slice(-4)); }
function seq(p){ var o=new ImportOptions(new File(p)); o.sequence=true; var f=app.project.importFile(o); f.mainSource.conformFrameRate=F; return f; }
var fb=new File(D+"beats.json"); fb.open("r"); var beats=JSON.parse(fb.read()); fb.close();
var C=findComp("intro"); if(!C) throw new Error("no comp intro");
for (var k=C.numLayers;k>=1;k--) if(/^(insert \d|giant \d|card ui )/.test(C.layer(k).name)) C.layer(k).remove();
var under=null; for (var k=1;k<=C.numLayers;k++) if(LOOK.test(C.layer(k).name)) under=C.layer(k);
function place(L){ if(under) L.moveAfter(under); else L.moveToBeginning(); }

// what's already there: word cards and transitions (frames)
var busy=[], wcs=[];
for (var k=1;k<=C.numLayers;k++){ var L=C.layer(k);
  if(/^wordcard bg /.test(L.name)){ var a=Math.round(L.inPoint*F); busy.push([a,a+2]); wcs.push(L); }
  if(/^intro trans /.test(L.name)) busy.push([Math.round(L.inPoint*F), Math.round(L.outPoint*F)]); }
for (var i=1;i<STARTS.length-1;i++) busy.push([STARTS[i],STARTS[i]]);
function free(a,len){ for (var i=0;i<busy.length;i++) if(a<busy[i][1]+4 && a+len>busy[i][0]-4) return false; return true; }
function slot(lo,hi,len){ for (var a=lo;a+len<=hi;a++) if(free(a,len)) return a; return -1; }
var hits=STARTS.slice(1,10);

// the giant words: him inside the letters
var cam=findFile(CAM)||app.project.importFile(new ImportOptions(new File(CAM)));
var nG=0;
for (var ci in GIANT){ ci=+ci; var a0=STARTS[ci], len=STARTS[ci+1]-a0, gl=7;
  var a=slot(a0+Math.round(len*0.35), STARTS[ci+1]-3, gl); if(a<0) continue;
  nG++;
  var bk=C.layers.addSolid([0,0,0],"giant "+nG+" black",W,H,1); bk.inPoint=a/F; bk.outPoint=(a+gl)/F; place(bk);
  var tx=C.layers.addText(GIANT[ci]); tx.name="giant "+nG+" word";
  var td=tx.property("Source Text").value; td.font="Satoshi"; td.fauxBold=true; td.fontSize=400; td.fillColor=[1,1,1];
  td.justification=ParagraphJustification.CENTER_JUSTIFY; tx.property("Source Text").setValue(td);
  tx.startTime=0; tx.inPoint=a/F; tx.outPoint=(a+gl)/F;
  tx.property("Transform").property("Position").setValue([W/2, H/2]);
  var r=tx.sourceRectAtTime(a/F,false), kk=Math.min(1.12*W/r.width, 1.05*H/r.height);
  tx.property("Transform").property("Scale").setValue([100*kk,100*kk]);
  tx.property("Transform").property("Position").setValue([W/2-(r.left+r.width/2)*kk, H/2-(r.top+r.height/2)*kk]);
  tx.property("Transform").property("Position").expression="value+[ (time-inPoint)*30*"+((nG%2)?14:-14)+", 0]";
  tx.moveBefore(bk);
  // the fill: the camera at that moment (the line's own source time), zoomed on his face
  var b=beats[ci], src=b.src+(a/F-b.p0);
  var fill=C.layers.add(cam); fill.name="giant "+nG+" fill"; fill.startTime=a/F-src; fill.inPoint=a/F; fill.outPoint=(a+gl)/F;
  if(fill.hasAudio) fill.audioEnabled=false;
  fill.property("Transform").property("Scale").setValue([300,300]); fill.property("Transform").property("Position").setValue([1083,140]);
  fill.moveBefore(tx);
  fill.setTrackMatte(tx, TrackMatteType.ALPHA);
  var cp=D+"mattins/giant_"+("0"+nG).slice(-2)+"/c_01.png";
  if(new File(cp).exists){ var cr=C.layers.add(seq(cp)); cr.name="giant "+nG+" cracks"; cr.startTime=a/F; cr.inPoint=a/F; cr.outPoint=(a+gl)/F; cr.moveBefore(fill); }
  var gg=fx(fill,"ec.vr.digitalglitch"); P(gg,2).expression="var f=Math.round((time-inPoint)*30); (f==0||f>="+(gl-2)+")?100:15";
  busy.push([a,a+gl]); hits.push(a);
}

// the flash cuts to him
var nI=0;
for (var ci=0;ci<10;ci++){ var a0=STARTS[ci], len=STARTS[ci+1]-a0;
  var nin=(len>=30)?2:(len>=14?1:0);
  for (var q=0;q<nin;q++){
    var il=(q?3:4), want=a0+Math.round(len*(nin==2?(q?0.72:0.3):0.6));
    var at=slot(want, STARTS[ci+1]-2, il); if(at<0) at=slot(a0+3, STARTS[ci+1]-2, il); if(at<0) continue;
    var p=D+"mattins/ins_"+("0"+(nI%16+1)).slice(-2)+"/f_01.jpg"; if(!new File(p).exists) continue;
    nI++;
    var L=C.layers.add(seq(p)); L.name="insert "+nI; L.startTime=at/F; L.inPoint=at/F; L.outPoint=(at+il)/F;
    var g=fx(L,"ec.vr.digitalglitch"); P(g,2).expression="var f=Math.round((time-inPoint)*30), n=Math.round((outPoint-inPoint)*30); (f==0||f>=n-1)?100:25";
    place(L); busy.push([at,at+il]); hits.push(at);
  }
}

// the UI elements on the word cards, in the card's ink, on the far side from the word
var nU=0;
for (var w=0;w<wcs.length;w++){ var bg=wcs[w], id=bg.name.replace("wordcard bg ","");
  var wl=byName(C,"wordcard word "+id); if(!wl) continue;
  var ink=wl.property("Source Text").value.fillColor, wp=wl.property("Transform").property("Position").value;
  var top=wp[1]>H/2, left=wp[0]>W/2;
  var spots=[[left?380:1540, top?230:850],[left?260:1660, top?560:520],[W/2+(left?-420:420), top?120:960]];
  for (var q=0;q<2+(w%2);q++){ var e=UIE[(w*2+q)%UIE.length];
    var f=findFile(UI+e[0])||app.project.importFile(new ImportOptions(new File(UI+e[0])));
    var U=C.layers.add(f); U.name="card ui "+id+" "+e[0].replace(".png","");
    U.startTime=bg.inPoint; U.inPoint=bg.inPoint; U.outPoint=bg.outPoint;
    U.property("Transform").property("Position").setValue(spots[q]); U.property("Transform").property("Scale").setValue([e[1],e[1]]);
    var fl=fx(U,"ADBE Fill"); P(fl,2).setValue([ink[0],ink[1],ink[2],1]);
    U.property("Opacity").expression="var f=Math.round((time-inPoint)*30); (f<"+q+")?0:85";
    U.moveBefore(bg); nU++;
  }
}

// the thermogram on every card change, insert and giant word
// the thermogram on the card changes only: on the inserts and giant words it swamped him and the black (matt's v6 stills)
hits=STARTS.slice(1,10);
var CUTS="["+hits.map(function(f){return (f/F).toFixed(4);}).join(",")+"]";
var LOOKX="var cuts="+CUTS+",pat={'-2':'o','-1':'g','0':'o','2':'g','3':'o'},look='';for(var i=0;i<cuts.length;i++){var f=Math.round((time-cuts[i])*30);if(pat[String(f)])look=pat[String(f)];}";
var to=byName(C,"thermal orange"), tg=byName(C,"thermal green"), ec=byName(C,"exposure cuts");
if(to) to.property("Transform").property("Opacity").expression=LOOKX+"look==='o'?100:0";
if(tg) tg.property("Transform").property("Opacity").expression=LOOKX+"look==='g'?100:0";
if(ec){ var ex=ec.property("Effects").property(1); ex.property("master").property("exposure").expression="var cuts="+CUTS+";var env=0,th=0;for(var i=0;i<cuts.length;i++){var d=time-cuts[i],p=-1,f=Math.round(d*30);if(f>=-2&&f<=3&&f!==1)th=1;if(d>-.15&&d<=0)p=(d+.15)/.15;else if(d>0&&d<.25)p=1-d/.25;if(p>=0){p=p*p*(3-2*p);env=Math.max(env,p);}}th?0.35*env:2.4*env"; }
writeLn("intro: "+nI+" inserts, "+nG+" giant words, "+nU+" UI elements on "+wcs.length+" word cards, thermogram on "+hits.length+" hits");
