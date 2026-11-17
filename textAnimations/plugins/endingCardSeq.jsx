// The end card as a sequence (matt, 2026-11-16), on the outro audio's loops (assets/make_outro_audio.py, times from the
// card's start):
//   0 - 1.536      the Nous logo alone, centred, the cyberpsycho lines shooting out of it as in the outro's match cut
//                  ("end lines nous", assets/make_endcard_lines.py); it jumps on each loop
//   1.536 - 3.264  the Log mark alone, centred, the lines wrapping round it ("end lines log"), jumping harder as the
//                  loops shorten
//   3.264 - 3.414  the glitch: the Log mark torn up
//   3.414 - end    both logos side by side on black, still, while the reverb plays
// Replaces what endingOutro.jsx did to "ending card". Rerun replaces it.
//   File > Scripts > Run Script File... > plugins/endingCardSeq.jsx
var DIR="C:/Users/0/.buzz/REPOS/listeningkit-templates/textAnimations/assets/collage/endcard_lines/", F=30;
var LOOPS=[0,0.768,1.536,1.92,2.304,2.496,2.688,2.784,2.88,2.976,3.072,3.12,3.168,3.216], SWAP=1.536, GLITCH=3.264, BOTH=3.414;
function findComp(n){ for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof CompItem && it.name===n) return it;} return null; }
function fx(L, id){ return L.property("Effects").addProperty(id); }
function P(e, n){ return e.property(e.property(1).matchName.replace(/-\d+$/,"")+"-"+("000"+n).slice(-4)); }
function seq(p){ var o=new ImportOptions(new File(p)); try{ o.sequence=true; }catch(e){} var f=app.project.importFile(o); try{ f.mainSource.conformFrameRate=F; }catch(e){} return f; }
var EC=findComp("ending card"); if(!EC) throw new Error("no comp 'ending card'");
for (var k=EC.numLayers;k>=1;k--) if(/^end lines /.test(EC.layer(k).name)) EC.layer(k).remove();
var N=EC.layer("end nous"), L=EC.layer("end log");
function clean(Lr){ var e=Lr.property("Effects"); for (var q=e.numProperties;q>=1;q--) e.property(q).remove(); }
clean(N); clean(L);
var lp="var Ls=["+LOOPS.join(",")+"],t=time,i=-1;for(var k=0;k<Ls.length;k++) if(t>=Ls[k]) i=k; var d=(i<0)?99:t-Ls[i];";
var both="var both=time>="+BOTH+";";
function setup(Lr, h, xSolo, xBoth, from, to){
  var src=Lr.source, b=h/src.height*100;
  Lr.inPoint=0; Lr.outPoint=EC.duration;
  Lr.property("Opacity").expression=both+"(both||(time>="+from+"&&time<"+to+"))?100:0";
  Lr.property("Transform").property("Scale").expression=lp+both+"var b="+b.toFixed(3)+";"+
    "var hit=both?0:(0.05+0.012*i), p=(d<0.06)?1+hit*(1-d/0.06):1; var k=b*p; [k,k]";
  Lr.property("Transform").property("Position").expression=lp+both+
    "var kick=(!both&&d<0.04&&i>=1)?((i%2)?1:-1)*(6+5*i):0; [both?"+xBoth+":"+xSolo+"+kick, 540]";
  var g=fx(Lr,"ec.vr.digitalglitch"); P(g,5).expression="time*700";
  P(g,2).expression=lp+both+"both?0:((time>="+GLITCH+")?100:(d<0.035?Math.min(100,15+6*i):0))";
  var t=fx(Lr,"ADBE Turbulent Displace"); P(t,3).setValue(30); P(t,6).expression="time*900";
  P(t,2).expression=both+"(!both&&time>="+GLITCH+")?180:0";
}
setup(N, 700, 960, 600, 0, SWAP);
setup(L, 760, 960, 1320, SWAP, BOTH);
var ln=EC.layers.add(seq(DIR+"nous/l_01.png")); ln.name="end lines nous"; ln.inPoint=0; ln.outPoint=SWAP;
var ll=EC.layers.add(seq(DIR+"log/l_01.png")); ll.name="end lines log"; ll.startTime=SWAP; ll.inPoint=SWAP; ll.outPoint=GLITCH;
writeLn("ending card: Nous with its lines, the Log mark wrapped in lines, glitch, then both side by side");
