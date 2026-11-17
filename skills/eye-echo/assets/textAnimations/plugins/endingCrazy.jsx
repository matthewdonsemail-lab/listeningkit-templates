// The ending, cut harder (matt, 2026-11-16): the cards held too long and too flat, so in the comp "ending", under
// the CRT:
//   "insert N"      flash cuts to the film's earlier anime shots (the cyberpsycho clip, the cyberpunk closeups and flow,
//                   the busts) for 3-4 frames inside each card, once or twice per card, a glitch on the way out
//   "giant N"       on every third card the card's big word blown up to fill the screen, used as a matte for one of
//                   those shots (the shot inside the letters, black round them) for 7 frames mid-card, then it glitches
//                   back to the card
//   the thermogram  the ending's "thermal orange / green" and "exposure cuts" layers now fire on every card change and
//                   every insert, not just in and out
// Rerun replaces them.   Run after endingCards.jsx (and endingTransitions.jsx).
//   File > Scripts > Run Script File... > plugins/endingCrazy.jsx
var CLIPS=["C:/Users/0/.buzz/REPOS/listeningkit-templates/textAnimations/assets/collage/opening_psycho_v9.mp4",
           "C:/Users/0/.buzz/REPOS/listeningkit-templates/textAnimations/assets/collage/cyberpunk_closeups.mp4",
           "C:/Users/0/.buzz/REPOS/listeningkit-templates/textAnimations/assets/collage/bust_lines.mp4",
           "C:/Users/0/.buzz/REPOS/listeningkit-templates/textAnimations/assets/collage/cyberpunk_opening_flow.mp4"];
var F=30, W=1920, H=1080, CARD_AT=626;
var LOOK=/^(thermal |exposure cuts|Global Scale|Lens Distortions|Monitor|CRT|Channel Blur|CC|CC 2|Posterize Time|Position Flicker|Glitches|Distortions|Glow)/;
function findComp(n){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof CompItem && it.name===n) return it;} return null; }
function findFile(p){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof FootageItem && it.file && it.file.fsName.replace(/\\/g,"/").toLowerCase()===p.toLowerCase()) return it;} return null; }
function fx(L, id){ return L.property("Effects").addProperty(id); }
function P(e, n){ return e.property(e.property(1).matchName.replace(/-\d+$/,"")+"-"+("000"+n).slice(-4)); }
var seed=7; function rnd(){ seed=(seed*16807)%2147483647; return seed/2147483647; }

var C=findComp("ending"); if(!C) throw new Error("no comp 'ending'");
for (var k=C.numLayers;k>=1;k--) if(/^(insert |giant |giant black )/.test(C.layer(k).name)) C.layer(k).remove();
var under=null; for (var k=1;k<=C.numLayers;k++) if(LOOK.test(C.layer(k).name)) under=C.layer(k);
function place(L){ if(under) L.moveAfter(under); else L.moveToBeginning(); }
var clips=[]; for (var i=0;i<CLIPS.length;i++) clips.push(findFile(CLIPS[i])||app.project.importFile(new ImportOptions(new File(CLIPS[i]))));

// the cards
var cards={}, order=[];
for (var k=1;k<=C.numLayers;k++){ var L=C.layer(k); if(!/^cap /.test(L.name)) continue;
  var f=Math.round(L.inPoint*F), d=L.property("Source Text").value;
  if(!cards[f]){ cards[f]={start:f, end:Math.round(L.outPoint*F), key:null, ks:0}; order.push(f); }
  if(d.fontSize>cards[f].ks){ cards[f].ks=d.fontSize; cards[f].key=L; } }
order.sort(function(a,b){return a-b;});

// the girl: her flash cuts (assets/make_ending_girl_inserts.py: a different shot of her each time, the red slashes
// looping round her) and the cracks through the giant words
var GIRL="C:/Users/0/.buzz/REPOS/listeningkit-templates/textAnimations/assets/collage/girlins/";
function seq(p){ var o=new ImportOptions(new File(p)); try{ o.sequence=true; }catch(e){} var f=app.project.importFile(o); try{ f.mainSource.conformFrameRate=F; }catch(e){} return f; }
var girlN=0, giantN=0;
function girlShot(name, a, len){
  girlN++; var p=GIRL+"ins_"+("0"+girlN).slice(-2)+"/f_01.jpg";
  if(!new File(p).exists) return null;
  var L=C.layers.add(seq(p)); L.name=name; L.startTime=a/F; L.inPoint=a/F; L.outPoint=(a+len)/F;
  var g=fx(L,"ec.vr.digitalglitch"); P(g,2).expression="var f=Math.round((time-inPoint)*30), n=Math.round((outPoint-inPoint)*30); (f==0||f>=n-1)?100:25";
  return L;
}
function shot(name, a, len, ci){
  var gs=girlShot(name, a, len); if(gs) return gs;
  var src=clips[ci%clips.length], L=C.layers.add(src); L.name=name;
  var t=rnd()*Math.max(0.2, src.duration-len/F-0.1);              // a moment from somewhere in the shot
  L.startTime=a/F-t; L.inPoint=a/F; L.outPoint=(a+len)/F;
  var sc=Math.max(W/src.width, H/src.height)*100; L.property("Transform").property("Scale").setValue([sc,sc]);
  var g=fx(L,"ec.vr.digitalglitch"); P(g,2).expression="var f=Math.round((time-inPoint)*30), n=Math.round((outPoint-inPoint)*30); (f==0||f>=n-1)?100:25";
  return L;
}
var hits=[], nIns=0, nGiant=0;
for (var i=0;i<order.length;i++){ var cd=cards[order[i]], len=cd.end-cd.start;
  hits.push(cd.start);
  // the giant word
  if(i%3===1 && len>=16){
    var a=cd.start+Math.round(len*0.4), gl=7;
    var bk=C.layers.addSolid([0,0,0],"giant black "+(i+1),W,H,1); bk.inPoint=a/F; bk.outPoint=(a+gl)/F; place(bk);
    var tx=cd.key.duplicate(); tx.name="giant "+(i+1)+" word"; tx.inPoint=a/F; tx.outPoint=(a+gl)/F;
    var r=null; try{ r=tx.sourceRectAtTime(a/F,false); }catch(e){}
    var s0=tx.property("Transform").property("Scale").value[0], ww=(r&&r.width>10)?r.width:cd.ks*3, hh=(r&&r.height>10)?r.height:cd.ks*0.7;
    var k=Math.min(1.12*W/ww, 1.05*H/hh);
    tx.property("Transform").property("Scale").setValue([s0*k, s0*k]);
    if(r) tx.property("Transform").property("Position").setValue([W/2-(r.left+r.width/2)*k*s0/100, H/2-(r.top+r.height/2)*k*s0/100]);
    // it drifts sideways while it's up, like the trailer's "DAVID!"
    tx.property("Transform").property("Position").expression="value+[ (time-inPoint)*30*"+((i%2)?14:-14)+", 0]";
    tx.moveBefore(bk);
    var fill=C.layers.add(clips[(i+1)%clips.length]); fill.name="giant "+(i+1)+" fill";
    fill.startTime=a/F-rnd()*2; fill.inPoint=a/F; fill.outPoint=(a+gl)/F;
    var sc=Math.max(W/fill.source.width, H/fill.source.height)*100; fill.property("Transform").property("Scale").setValue([sc,sc]);
    fill.moveBefore(tx);
    try{ fill.setTrackMatte(tx, TrackMatteType.ALPHA); }catch(e){ fill.trackMatteType=TrackMatteType.ALPHA; }
    giantN++; var cp=GIRL+"giant_"+("0"+giantN).slice(-2)+"/c_01.png";
    if(new File(cp).exists){ var cr=C.layers.add(seq(cp)); cr.name="giant "+(i+1)+" cracks"; cr.startTime=a/F; cr.inPoint=a/F; cr.outPoint=(a+gl)/F; cr.moveBefore(fill); }
    var gg=fx(fill,"ec.vr.digitalglitch"); P(gg,2).expression="var f=Math.round((time-inPoint)*30); (f==0||f>="+(gl-2)+")?100:15";
    hits.push(a); nGiant++;
  }
  // flash cuts to the earlier shots
  var nin=(len>=30)?2:(len>=14?1:0);
  for (var q=0;q<nin;q++){
    var at=cd.start+Math.round(len*(nin==2?(q?0.72:0.3):0.6)), il=(q?3:4);
    if(i%3===1 && Math.abs(at-(cd.start+Math.round(len*0.4)))<9) at=cd.start+Math.round(len*0.8);
    if(at+il>=cd.end-2 || at+il>=CARD_AT-1) continue;
    var clash=false; for (var h=0;h<hits.length;h++) if(Math.abs(hits[h]-at)<6) clash=true;
    if(clash) continue;
    place(shot("insert "+(i+1)+"."+(q+1), at, il, i*2+q)); hits.push(at); nIns++;
  }
}
hits.push(CARD_AT); hits.sort(function(a,b){return a-b;});

// the thermogram, on every card change and insert
var CUTS="["; for (var i=0;i<hits.length;i++) CUTS+=(i?",":"")+(hits[i]/F).toFixed(4); CUTS+="]";
var LOOKX="var cuts="+CUTS+",pat={'-2':'o','-1':'g','0':'o','2':'g','3':'o'},look='';for(var i=0;i<cuts.length;i++){var f=Math.round((time-cuts[i])*30);if(pat[String(f)])look=pat[String(f)];}";
for (var k=1;k<=C.numLayers;k++){ var L=C.layer(k);
  if(L.name==="thermal orange") L.property("Transform").property("Opacity").expression=LOOKX+"look==='o'?100:0";
  if(L.name==="thermal green") L.property("Transform").property("Opacity").expression=LOOKX+"look==='g'?100:0";
  if(L.name==="exposure cuts"){ var e=L.property("Effects").property(1);
    e.property("master").property("exposure").expression="var cuts="+CUTS+";var env=0,th=0;for(var i=0;i<cuts.length;i++){var d=time-cuts[i],p=-1,f=Math.round(d*30);if(f>=-2&&f<=3&&f!==1)th=1;if(d>-.3&&d<=0)p=(d+.3)/.3;else if(d>0&&d<.4)p=1-d/.4;if(p>=0){p=p*p*(3-2*p);env=Math.max(env,p);}}th?0.35*env:3.6*env"; }
}
writeLn("ending: "+nIns+" flash cuts, "+nGiant+" giant words, thermogram on "+hits.length+" beats");
