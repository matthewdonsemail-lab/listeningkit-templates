// matt, 2026-11-17: random letters switch font inside every word. The type becomes make_letter_text.py's frames
// (letters/<layer>/: every letter where its Satoshi letter sits, a third of them redrawn 8-bit or gothic every 3 frames):
// each text layer ("card N", "wordcard word N", "wordcard line N") gets a "<name> letters" image-sequence layer right
// above it, same in/out, its ink (Fill), the deep glow, and for the line cards the hide-under-the-word-cards opacity;
// the text layer itself and intro_fonts_glow.jsx's whole-layer font copies ("card N 8bit / gothic") go off.
// Rerun replaces the "letters" layers.
var D="C:/Users/0/filmcraft/projects/effectcraftEditing/introEC/letters/", F=30;
var GLOW=[[85,4,0.8],[75,12,0.4],[70,30,0.2]];
var BASE=[[1,1,1,1],[254/255,206/255,0,1]];
function findComp(n){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof CompItem && it.name===n) return it;} return null; }
function fx(L, id){ return L.property("Effects").addProperty(id); }
function P(e, n){ return e.property(e.property(1).matchName.replace(/-\d+$/,"")+"-"+("000"+n).slice(-4)); }
function seq(p){ var o=new ImportOptions(new File(p)); o.sequence=true; var f=app.project.importFile(o); f.mainSource.conformFrameRate=F; return f; }
var C=findComp("intro"); if(!C) throw new Error("no comp intro");
for (var k=C.numLayers;k>=1;k--) if(/ letters$/.test(C.layer(k).name)) C.layer(k).remove();
// the word card windows: the line cards hide under them
var wins=[]; for (var k=1;k<=C.numLayers;k++){ var L=C.layer(k); if(/^wordcard bg /.test(L.name)) wins.push([L.inPoint, L.outPoint]); }
var targets=[]; for (var k=1;k<=C.numLayers;k++){ var L=C.layer(k); if(/^(card \d+|wordcard (word|line) \d+)$/.test(L.name)) targets.push(L); }
var n=0;
for (var t=0;t<targets.length;t++){
  var T=targets[t], dir=D+T.name.replace(/ /g,"_")+"/t_000.png";
  if(!new File(dir).exists){ writeLn("no frames for "+T.name); continue; }
  var L=C.layers.add(seq(dir)); L.name=T.name+" letters";
  L.startTime=T.inPoint; L.inPoint=T.inPoint; L.outPoint=T.outPoint;
  var ink;
  var m=T.name.match(/^card (\d+)$/);
  if(m){ ink=BASE[(+m[1]-1)%2];
    L.property("Transform").property("Opacity").expression="var F="+JSON.stringify(wins)+",o=100;for(var i=0;i<F.length;i++)if(time>=F[i][0]&&time<F[i][1])o=0;o"; }
  else { var c=T.property("Source Text").value.fillColor; ink=[c[0],c[1],c[2],1]; }
  var fl=fx(L,"ADBE Fill"); fl.name="ink"; P(fl,2).setValue(ink);
  for (var g=0;g<GLOW.length;g++){ var gl=fx(L,"ADBE Glo2"); gl.name="deep glow "+(g+1); gl.property(2).setValue(GLOW[g][0]); gl.property(3).setValue(GLOW[g][1]); gl.property(4).setValue(GLOW[g][2]); }
  L.moveBefore(T); T.enabled=false; n++;
}
var off=0; for (var k=1;k<=C.numLayers;k++) if(/^card \d+ (8bit|gothic)$/.test(C.layer(k).name)){ C.layer(k).enabled=false; off++; }
writeLn("intro: "+n+" letter layers in, "+targets.length+" text layers and "+off+" whole-layer font copies off");
