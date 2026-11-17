// matt, 2026-11-16, on comp "intro":
//   - the line back on the left (left aligned, x 110) and bigger (x1.25), each block centred top to bottom again
//   - "text glitch": the launch film ending's text glitch (plugins/endingTransitions.jsx): Digital Glitch + a Turbulent
//     Displace slip, lightly on every word card's 2 frames (hard made the word and UI unreadable) and on each card's first 3 / last 2 frames, lighter between;
//     over the type and the word cards, under the CRT
// The gradient file (left_gradient.png) was remade: black at the left edge, clear by the middle. Rerun is safe.
var F=30, SCALE=1.25;
var STARTS=[0,68,83,176,221,290,344,351,437,481,525];
var SIZE=[118,150,92,104,104,112,220,112,140,112];
var LOOK=/^(thermal |exposure cuts|Global Scale|Lens Distortions|Monitor|CRT|Channel Blur|CC|CC 2|Posterize Time|Position Flicker|Glitches|Distortions|Glow)/;
function findComp(n){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof CompItem && it.name===n) return it;} return null; }
function byName(c,n){ for (var k=1;k<=c.numLayers;k++) if(c.layer(k).name===n) return c.layer(k); return null; }
function fx(L, id){ return L.property("Effects").addProperty(id); }
function P(e, n){ return e.property(e.property(1).matchName.replace(/-\d+$/,"")+"-"+("000"+n).slice(-4)); }
var C=findComp("intro"); if(!C) throw new Error("no comp intro");
for (var i=0;i<10;i++){
  var T=byName(C,"card "+(i+1)), st=T.property("Source Text"), ex=st.expression;
  st.expression="";
  var tv=st.value; tv.justification=ParagraphJustification.LEFT_JUSTIFY; tv.fontSize=Math.round(SIZE[i]*SCALE); tv.leading=tv.fontSize*0.95; st.setValue(tv);
  T.property("Transform").property("Position").setValue([110, 400]);
  var r=T.sourceRectAtTime(T.inPoint+0.02,false);       // the full text, the expression off
  var y=400+(540-(400+r.top+r.height/2));
  T.property("Transform").property("Position").setValue([110, Math.round(y)]);
  st.expression=ex;
  writeLn("card "+(i+1)+": size "+tv.fontSize+", width "+Math.round(r.width)+", y "+Math.round(y));
}
// the text glitch
var old=byName(C,"text glitch"); if(old) old.remove();
var wins=[]; for (var k=1;k<=C.numLayers;k++){ var L=C.layer(k); if(/^wordcard bg /.test(L.name)) wins.push(Math.round(L.inPoint*F)); }
var under=null; for (var k=1;k<=C.numLayers;k++) if(LOOK.test(C.layer(k).name)) under=C.layer(k);
var tg=C.layers.addSolid([0,0,0],"text glitch",1920,1080,1); tg.adjustmentLayer=true; tg.startTime=0; tg.inPoint=0; tg.outPoint=C.duration;
var hits="var st="+JSON.stringify(STARTS.slice(0,10))+",en="+JSON.stringify(STARTS.slice(1))+",wc="+JSON.stringify(wins)+",f=Math.round(time*30),h=0;"+
  "for(var i=0;i<st.length;i++){var a=f-st[i],b=en[i]-f; if(a>=0&&a<3)h=Math.max(h,[1,0.7,0.35][a]); if(b>0&&b<=2)h=Math.max(h,b==1?0.8:0.4); if(a>=0&&b>0&&(f*7+i)%11==0)h=Math.max(h,0.3);}"+
  "for(var j=0;j<wc.length;j++){var d=f-wc[j]; if(d>=0&&d<2)h=Math.max(h,d==0?0.35:0.2);}";
var dg=fx(tg,"ec.vr.digitalglitch");
P(dg,2).expression=hits+"100*h"; P(dg,3).setValue(9); P(dg,5).expression="time*600";
var td=fx(tg,"ADBE Turbulent Displace"); P(td,3).setValue(40); P(td,5).setValue(2); P(td,6).expression="time*900";
P(td,2).expression=hits+"90*h";
if(under) tg.moveAfter(under); else tg.moveToBeginning();
writeLn("text glitch on "+wins.length+" word cards and 10 cards");
