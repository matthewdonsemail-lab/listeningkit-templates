// The ending's transitions and text glitches (matt, 2026-11-16), in the comp "ending", over the cards, the red lines
// and the UI elements, under the CRT:
//   "end trans N"   on every card change, the transition frames made by assets/make_ending_transitions.py
//                   (assets/collage/endtrans/: clip blends with a pixel sort on the cut, or the Edgerunners 2 red flash
//                   on every third cut)
//   "text glitch"   one adjustment layer: Digital Glitch hitting the type hard on the first frames of each card and its
//                   last two, lighter in between, plus a Displacement-style slip (Turbulent Displace) and an RGB split
//                   (Channel Blur off; the glitch's own colour distortion) on the same beats
// Rerun replaces them.   Run after endingCards.jsx.   File > Scripts > Run Script File... > plugins/endingTransitions.jsx
var DIR="C:/Users/0/.buzz/REPOS/listeningkit-templates/textAnimations/assets/collage/endtrans/", F=30;
var LOOK=/^(thermal |exposure cuts|Global Scale|Lens Distortions|Monitor|CRT|Channel Blur|CC|CC 2|Posterize Time|Position Flicker|Glitches|Distortions|Glow)/;
function findComp(n){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof CompItem && it.name===n) return it;} return null; }
function fx(L, id){ return L.property("Effects").addProperty(id); }
function P(e, n){ return e.property(e.property(1).matchName.replace(/-\d+$/,"")+"-"+("000"+n).slice(-4)); }
function readJson(p){ var f=new File(p); f.open("r"); var t=f.read(); f.close(); return eval("("+t+")"); }

var C=findComp("ending"); if(!C) throw new Error("no comp 'ending'");
for (var k=C.numLayers;k>=1;k--) if(/^(end trans |text glitch)/.test(C.layer(k).name)) C.layer(k).remove();
// the lowest CRT / look layer: everything new goes just under it
var under=null; for (var k=1;k<=C.numLayers;k++) if(LOOK.test(C.layer(k).name)) under=C.layer(k);

// the card starts
var s={}; for (var k=1;k<=C.numLayers;k++){ var L=C.layer(k); if(/^cap /.test(L.name)) s[Math.round(L.inPoint*F)]=Math.round(L.outPoint*F); }
var starts=[], ends=[]; for (var f in s){ starts.push(+f); } starts.sort(function(a,b){return a-b;}); for (var i=0;i<starts.length;i++) ends.push(s[starts[i]]);

// the text glitch
var tg=C.layers.addSolid([0,0,0],"text glitch",C.width,C.height,1); tg.adjustmentLayer=true; tg.startTime=0; tg.inPoint=0; tg.outPoint=C.duration;
var hits="var st=["+starts.join(",")+"],en=["+ends.join(",")+"],f=Math.round(time*30),h=0;"+
  "for(var i=0;i<st.length;i++){var a=f-st[i],b=en[i]-f; if(a>=0&&a<3)h=Math.max(h,[1,0.7,0.35][a]); if(b>0&&b<=2)h=Math.max(h,b==1?0.8:0.4); if(a>=0&&b>0&&(f*7+i)%11==0)h=Math.max(h,0.3);}";
var dg=fx(tg,"ec.vr.digitalglitch");
P(dg,2).expression=hits+"100*h"; P(dg,3).setValue(9); P(dg,5).expression="time*600";
var td=fx(tg,"ADBE Turbulent Displace"); P(td,3).setValue(40); P(td,5).setValue(2); P(td,6).expression="time*900";
P(td,2).expression=hits+"90*h";
if(under) tg.moveAfter(under); else tg.moveToBeginning();

// the transitions
var cuts=readJson(DIR+"cuts.json"), n=0;
for (var i=0;i<cuts.length;i++){ var c=cuts[i];
  var o=new ImportOptions(new File(c.path)); try{ o.sequence=true; }catch(e){}
  var ft=app.project.importFile(o); try{ ft.mainSource.conformFrameRate=F; }catch(e){}
  var L=C.layers.add(ft); L.name="end trans "+(i+1)+" "+c.kind;
  L.startTime=c.first/F; L.inPoint=c.first/F; L.outPoint=(c.first+c.n)/F;
  if(under) L.moveAfter(under); else L.moveToBeginning();
  n++;
}
writeLn("ending: "+n+" transitions, text glitch on "+starts.length+" cards");
