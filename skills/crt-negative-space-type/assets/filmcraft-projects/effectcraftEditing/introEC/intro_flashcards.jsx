// matt, 2026-11-16: "the words flashing with the intercuts ... like that last composition, where it has the text at
// different places around the screen in the intercut, flashing between it": the launch film's ending cards
// (plugins/endingCards.jsx: flat colour backgrounds, the ink set against them) as 2-frame intercuts, one per spoken
// word: the word big, at a new place on the screen each time, the whole line small in a corner, on acid yellow /
// navy / red in turn. The centred line hides while a card is up, so it cuts between the card and the scene.
// Replaces intro_glitch.jsx's launch-film frames ("intercut N") and plain colour flashes ("flash N").
// None within 4 frames of a card change (the thermogram's). Rerun replaces "wordcard *" layers.
var D="C:/Users/0/filmcraft/projects/effectcraftEditing/introEC/";
var F=30, LEN=2;
var STARTS=[0,68,83,176,221,290,344,351,437,481];
var BG=[[254/255,206/255,0],[16/255,24/255,60/255],[200/255,18/255,30/255]];
var INK=[[16/255,24/255,60/255],[254/255,206/255,0],[1,1,1]];
var BASE=[[1,1,1,1],[254/255,206/255,0,1]];
// where the big word goes: [x, y, justification, size], cycled
var SPOTS=[[150,330,"L",300],[960,600,"C",380],[1770,900,"R",280],[170,930,"L",340],[1760,320,"R",300],[960,300,"C",260],
           [960,900,"C",320],[150,620,"L",260]];
var CORNER=[[1770,1010,"R"],[150,110,"L"],[1770,110,"R"],[150,1010,"L"]];
function findComp(n){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof CompItem && it.name===n) return it;} return null; }
function byName(c,n){ for (var k=1;k<=c.numLayers;k++) if(c.layer(k).name===n) return c.layer(k); return null; }
function fx(L, id){ return L.property("Effects").addProperty(id); }
function P(e, n){ return e.property(e.property(1).matchName.replace(/-\d+$/,"")+"-"+("000"+n).slice(-4)); }
var J={L:ParagraphJustification.LEFT_JUSTIFY,C:ParagraphJustification.CENTER_JUSTIFY,R:ParagraphJustification.RIGHT_JUSTIFY};
var f=new File(D+"beats.json"); f.open("r"); var beats=JSON.parse(f.read()); f.close();
var C=findComp("intro"); if(!C) throw new Error("no comp intro");
for (var k=C.numLayers;k>=1;k--) if(/^(intercut \d+|flash \d+|wordcard .*)$/.test(C.layer(k).name)) C.layer(k).remove();
function nearCut(t){ var fr=Math.round(t*F); for (var i=1;i<STARTS.length;i++) if(Math.abs(fr-STARTS[i])<=4) return true; return false; }
function txt(s, size, x, y, j, ink, a, b, name){
  var T=C.layers.addText(s); T.name=name;
  var td=T.property("Source Text").value; td.font="Satoshi"; td.fauxBold=true; td.fontSize=size; td.fillColor=ink;
  td.tracking=size<60?200:0; td.justification=J[j]; T.property("Source Text").setValue(td);
  T.startTime=0; T.inPoint=a; T.outPoint=b; T.property("Transform").property("Position").setValue([x,y]);
  return T;
}
var topCard=byName(C,"card 10"), wins=[], n=0;
for (var bi=0;bi<beats.length;bi++){
  var line=beats[bi].text.toUpperCase();
  for (var w=0;w<beats[bi].words.length;w++){
    var t=Math.round(Math.max(0,beats[bi].words[w][0])*F)/F;
    if(nearCut(t)) continue;
    var a=t, b=t+LEN/F, ci=n%3, sp=SPOTS[n%SPOTS.length], co=CORNER[n%CORNER.length];
    var word=beats[bi].words[w][1].toUpperCase().replace(/[,]$/,"");
    // last made goes on top, so: background, then the small line, then the word
    var S=C.layers.addSolid(BG[ci],"wordcard bg "+(n+1),1920,1080,1); S.startTime=a; S.inPoint=a; S.outPoint=b; S.moveAfter(topCard);
    var Sm=txt(line, 34, co[0], co[1], co[2], INK[ci], a, b, "wordcard line "+(n+1)); Sm.moveBefore(S);
    var Tw=txt(word, sp[3], sp[0], sp[1], sp[2], INK[ci], a, b, "wordcard word "+(n+1)); Tw.moveBefore(Sm);
    wins.push([a,b]); n++;
  }
}
// the centred line: hidden while a card is up; its ink back to the alternating base
for (var i=0;i<beats.length;i++){
  var T=byName(C,"card "+(i+1));
  T.property("Transform").property("Opacity").expression="var F="+JSON.stringify(wins)+",o=100;for(var i=0;i<F.length;i++)if(time>=F[i][0]&&time<F[i][1])o=0;o";
  var e=T.property("Effects"); for (var j=1;j<=e.numProperties;j++) if(e.property(j).name==="card ink"){ var p=P(e.property(j),2); p.expression=""; p.setValue(BASE[i%2]); }
}
writeLn("intro: "+n+" word cards (2 frames each), centred line hides under them");
