// matt, 2026-11-17, on comp "intro": the type switches font at random (an 8-bit pixel font, Press Start 2P, or an old
// gothic blackletter, UnifrakturMaguntia: both Google Fonts, OFL, installed for the user), and a deep glow on every
// text layer.
//   - the line cards ("card N"): an 8-bit copy and a gothic copy of each ("card N 8bit", "card N gothic", the same
//     word-by-word reveal and ink); every 4 frames one of the three shows, at random (60% Satoshi, 20% each other)
//   - the word cards ("wordcard word / line N"): one font per card, picked at random
//   - "deep glow 1-3" on every text layer (not the giant words: they're track mattes): three stacked Glows, a tight
//     bright core, a halo and a wide soft bloom, the way Deep Glow builds it
// Rerun replaces the copies and the glows.
var FONTS=[["Satoshi",1.0],["Press Start 2P",0.5],["UnifrakturMaguntia",1.15]];
var GLOW=[[85,4,0.8],[75,12,0.4],[70,30,0.2]];        // threshold %, radius, intensity (lighter: the CRT blew the first settings into white blobs)
function findComp(n){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof CompItem && it.name===n) return it;} return null; }
function byName(c,n){ for (var k=1;k<=c.numLayers;k++) if(c.layer(k).name===n) return c.layer(k); return null; }
function fx(L, id){ return L.property("Effects").addProperty(id); }
function hash(n){ var x=Math.sin(n*12.9898+4.1414)*43758.5453; return x-Math.floor(x); }
var C=findComp("intro"); if(!C) throw new Error("no comp intro");
for (var k=C.numLayers;k>=1;k--) if(/^card \d+ (8bit|gothic)$/.test(C.layer(k).name)) C.layer(k).remove();
function setFont(L, fam, k){
  var st=L.property("Source Text"), ex=st.expression; st.expression="";
  var td=st.value; td.font=fam; td.fauxBold=(fam==="Satoshi"); td.fontSize=Math.max(8,Math.round(td.fontSize*k)); td.leading=td.fontSize*(fam==="Press Start 2P"?1.25:0.95);
  st.setValue(td); st.expression=ex;
}
function deepGlow(L){
  var e=L.property("Effects"); for (var j=e.numProperties;j>=1;j--) if(/^deep glow/.test(e.property(j).name)) e.property(j).remove();
  for (var g=0;g<GLOW.length;g++){ var gl=fx(L,"ADBE Glo2"); gl.name="deep glow "+(g+1);
    gl.property(2).setValue(GLOW[g][0]); gl.property(3).setValue(GLOW[g][1]); gl.property(4).setValue(GLOW[g][2]); }
}
var nCard=0, nWord=0, nGlow=0;
// the line cards: three versions, switching every 4 frames
for (var i=1;i<=10;i++){
  var L=byName(C,"card "+i); if(!L) continue;
  var op=L.property("Transform").property("Opacity"), base=op.expression;      // hides under the word cards
  var pick="var b=Math.floor(Math.round(time*30)/4),x=Math.sin(b*12.9898+"+(i*78.233)+")*43758.5453;x=x-Math.floor(x);var pick=x<0.6?0:(x<0.8?1:2);";
  var vers=[L];
  for (var v=1;v<3;v++){ var Dp=L.duplicate(); Dp.name="card "+i+" "+(v==1?"8bit":"gothic"); setFont(Dp, FONTS[v][0], FONTS[v][1]/FONTS[0][1]); vers.push(Dp); }
  for (var v=0;v<3;v++){
    var o=vers[v].property("Transform").property("Opacity");
    o.expression=pick+(base? base.replace(/;o$/,";pick=="+v+"?o:0") : "pick=="+v+"?100:0");
    deepGlow(vers[v]); nGlow++;
  }
  nCard++;
}
// the word cards: one font each
for (var k=1;k<=C.numLayers;k++){ var L=C.layer(k), m=L.name.match(/^wordcard (word|line) (\d+)$/); if(!m) continue;
  var r=hash(+m[2]), v=r<0.45?0:(r<0.75?1:2);
  if(v) setFont(L, FONTS[v][0], FONTS[v][1]);
  deepGlow(L); nGlow++; if(m[1]==="word") nWord++;
}
writeLn("intro: "+nCard+" line cards x3 fonts switching every 4 frames, "+nWord+" word cards in random fonts, deep glow on "+nGlow+" text layers");
