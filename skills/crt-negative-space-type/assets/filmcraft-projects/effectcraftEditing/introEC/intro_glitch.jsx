// matt, 2026-11-16, on comp "intro":
//   - the text centre frame (centred lines, centred on the frame)
//   - the cards alternate colours like the launch film's ending (plugins/endingCards.jsx): white / acid yellow ink,
//     by card ("card ink" Fill)
//   - as each word lands (beats.json word times): a distortion glitch on the background (screen + matt, not the type):
//     "word glitch", a 2-frame Turbulent Displace tear; and on some words a 2-frame intercut: every 3rd word a frame of
//     the launch film ("intercut N", intercuts/ic_NN.jpg from renders/launch_film_final_full.mp4), every 3rd a flat
//     colour card from the ending's palette ("flash N": acid yellow, navy, red), with the type's ink flipped so it
//     reads on it. None within 4 frames of a card change (that's the thermogram's).
// Rerun replaces them. Run after intro_words.jsx and intro_cutout.jsx.
var D="C:/Users/0/filmcraft/projects/effectcraftEditing/introEC/";
var F=30;
var STARTS=[0,68,83,176,221,290,344,351,437,481];
var BG=[[254/255,206/255,0],[16/255,24/255,60/255],[200/255,18/255,30/255]];
var INK_ON=[[16/255,24/255,60/255,1],[254/255,206/255,0,1],[1,1,1,1]];   // ink on each flash colour
var BASE=[[1,1,1,1],[254/255,206/255,0,1]];                                // card inks, alternating
function findComp(n){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof CompItem && it.name===n) return it;} return null; }
function byName(c,n){ for (var k=1;k<=c.numLayers;k++) if(c.layer(k).name===n) return c.layer(k); return null; }
function fx(L, id){ return L.property("Effects").addProperty(id); }
function P(e, n){ return e.property(e.property(1).matchName.replace(/-\d+$/,"")+"-"+("000"+n).slice(-4)); }
var f=new File(D+"beats.json"); f.open("r"); var beats=JSON.parse(f.read()); f.close();
var C=findComp("intro"); if(!C) throw new Error("no comp intro");
var DUR=C.duration;
for (var k=C.numLayers;k>=1;k--) if(/^(word glitch|intercut \d+|flash \d+)$/.test(C.layer(k).name)) C.layer(k).remove();

// every word's landing time, and what each one gets
var words=[]; for (var b=0;b<beats.length;b++) for (var w=0;w<beats[b].words.length;w++) words.push(Math.max(0,beats[b].words[w][0]));
words.sort(function(a,b){return a-b;});
function nearCut(t){ var fr=Math.round(t*F); for (var i=1;i<STARTS.length;i++) if(Math.abs(fr-STARTS[i])<=4) return true; return false; }
var glitch=[], inter=[], flash=[];
for (var n=0;n<words.length;n++){
  var t=Math.round(words[n]*F)/F; glitch.push(t);
  if(nearCut(t)) continue;
  if(n%3===1) inter.push(t); else if(n%3===2) flash.push(t);
}

// the background tear on every word: above matt and the screen, under the lines and the type
var lines=byName(C,"red lines");
var G=C.layers.addSolid([0,0,0],"word glitch",1920,1080,1); G.adjustmentLayer=true; G.startTime=0; G.inPoint=0; G.outPoint=DUR;
var td=fx(G,"ADBE Turbulent Displace");
P(td,3).setValue(60); P(td,6).expression="time*900";
P(td,2).expression="var g="+JSON.stringify(glitch)+",a=0;for(var i=0;i<g.length;i++){var d=(time-g[i])*30;if(d>=0&&d<2)a=Math.max(a,d<1?180:90);}a";
G.moveAfter(lines);

// the intercuts and flashes: 2 frames each, over everything but the type (and under the CRT, so it scans them too)
var topCard=byName(C,"card 10");
for (var i=0;i<inter.length;i++){
  var img=app.project.importFile(new ImportOptions(new File(D+"intercuts/ic_"+("0"+(i%16+1)).slice(-2)+".jpg")));
  var L=C.layers.add(img); L.name="intercut "+(i+1); L.startTime=inter[i]; L.inPoint=inter[i]; L.outPoint=inter[i]+2/F;
  L.moveAfter(topCard);
}
var flashCol=[];
for (var i=0;i<flash.length;i++){
  var c=BG[i%3], S=C.layers.addSolid(c,"flash "+(i+1),1920,1080,1);
  S.startTime=flash[i]; S.inPoint=flash[i]; S.outPoint=flash[i]+2/F; S.moveAfter(topCard);
  flashCol.push([flash[i], flash[i]+2/F, INK_ON[i%3]]);
}

// the type: centred, alternating ink, flipped on the flashes
for (var i=0;i<beats.length;i++){
  var T=byName(C,"card "+(i+1)), st=T.property("Source Text"), ex=st.expression;
  st.expression=""; var tv=st.value; tv.justification=ParagraphJustification.CENTER_JUSTIFY; st.setValue(tv); st.expression=ex;
  var p=T.property("Transform").property("Position").value; T.property("Transform").property("Position").setValue([960,p[1]]);
  var e=T.property("Effects"); for (var j=e.numProperties;j>=1;j--) if(e.property(j).name==="card ink") e.property(j).remove();
  var fl=fx(T,"ADBE Fill"); fl.name="card ink";
  P(fl,2).expression="var F="+JSON.stringify(flashCol)+",c="+JSON.stringify(BASE[i%2])+";for(var i=0;i<F.length;i++)if(time>=F[i][0]&&time<F[i][1])c=F[i][2];c";
}
writeLn("intro: "+glitch.length+" word glitches, "+inter.length+" intercuts, "+flash.length+" colour flashes; type centred, inks alternating");
